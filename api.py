from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import time
import hashlib
import requests
import fcntl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pypinyin import lazy_pinyin, Style

app = Flask(__name__)
CORS(app)

DATA_FILE = "/root/Roomie-Claude/room_data.json"
WISH_FILE = "wishes.json"

# 微信小程序配置
WECHAT_APPID = "wxff98b80705277ab6"
WECHAT_SECRET = "f251b2106c7655ab8b5bc7cfd5d5190e"

# 邮件推送配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "spaceone.roomie@gmail.com",
    "sender_password": "",  # 需要填入Gmail应用专用密码
    "receiver_email": "spaceone.roomie@gmail.com",
    "enabled": False  # 获取密码后改为True
}


def send_email_notification(subject, body):
    """发送邮件通知"""
    if not EMAIL_CONFIG["enabled"] or not EMAIL_CONFIG["sender_password"]:
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = EMAIL_CONFIG["receiver_email"]
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "stats": {"total_matches": 0}, "logs": []}


def append_log(room_data, event, name_a, name_b, group_code, note=""):
    """记录操作日志"""
    if "logs" not in room_data:
        room_data["logs"] = []
    room_data["logs"].append({
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "event": event,
        "a": name_a,
        "b": name_b,
        "group": group_code,
        "note": note
    })


def save_data(room_data):
    """保存数据，自动按状态排序（matched在前，active在后），使用文件锁防止并发问题"""
    # 按状态排序：matched在前，active在后
    room_data["users"].sort(key=lambda u: (u["status"] != "matched", u.get("created_at", 0)))

    # 使用文件锁确保原子性写入
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 获取排他锁
        try:
            json.dump(room_data, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # 释放锁


def generate_group_code(event_name: str, city: str, date: str, custom_suffix: str = "") -> str:
    """
    生成群口令
    规则：会议名前两个字首字母 + 城市前两个字首字母 + 日期(MMDD) + 自定义后缀（可选）
    例如：前哨大会 + 北京 + 2026-02-17 → QSDBJ0217
    例如：AI Summit + Beijing + 2026-03-28 → AIBJ0328
    """
    def get_initials(text: str, count: int = 2) -> str:
        """提取文本前count个字符的首字母（支持中英文）"""
        text = ''.join(text.split())
        chars = text[:count]
        result = []
        for char in chars:
            if '\u4e00' <= char <= '\u9fff':
                pinyin = lazy_pinyin(char, style=Style.FIRST_LETTER)
                result.append(pinyin[0].upper())
            elif char.isalpha():
                result.append(char.upper())
        return ''.join(result)

    try:
        event_abbr = get_initials(event_name, 2)
        city_abbr = get_initials(city, 2)
        date_parts = date.split('-')
        if len(date_parts) == 3:
            month_day = date_parts[1] + date_parts[2]
        else:
            month_day = str(int(time.time()))[-4:]
        code = f"{event_abbr}{city_abbr}{month_day}"
        if custom_suffix and custom_suffix.strip():
            suffix = custom_suffix.strip().upper()
            if not suffix.replace(' ', '').isalnum():
                raise ValueError("自定义标识只能包含英文字母和数字")
            suffix = suffix.replace(' ', '')
            code = f"{code}-{suffix}"
        return code
    except Exception as e:
        print(f"生成口令错误: {e}")
        hash_code = hashlib.md5(f"{event_name}{city}{date}".encode()).hexdigest()[:8].upper()
        return hash_code


def calculate_date_overlap(check_in1: str, check_out1: str, check_in2: str, check_out2: str):
    """
    计算两个日期区间的重叠部分
    返回：(是否有重叠, 重叠开始日期, 重叠结束日期)
    """
    try:
        start1 = datetime.strptime(check_in1, '%Y-%m-%d')
        end1 = datetime.strptime(check_out1, '%Y-%m-%d')
        start2 = datetime.strptime(check_in2, '%Y-%m-%d')
        end2 = datetime.strptime(check_out2, '%Y-%m-%d')

        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        if overlap_start < overlap_end:
            return True, overlap_start.strftime('%Y-%m-%d'), overlap_end.strftime('%Y-%m-%d')
        else:
            return False, None, None
    except Exception as e:
        print(f"日期计算错误: {e}")
        return False, None, None



def smoking_ok(a, b):
    """不吸烟只匹配不吸烟；any(我不介意)可匹配吸烟和any"""
    if a == "no": return b == "no"
    if b == "no": return False
    return True

def schedule_ok(a, b):
    """早鸟只匹配早鸟；any(我不介意)可匹配夜猫子和any"""
    if a == "early_bird": return b == "early_bird"
    if b == "early_bird": return False
    return True

def clean_expired_pending(room_data):
    """清理超过2分钟的 pending 状态，自动变回 active"""
    current_time = time.time()
    timeout = 120  # 2分钟

    for user in room_data["users"]:
        if user["status"] == "pending":
            pending_at = user.get("pending_at", 0)
            if current_time - pending_at > timeout:
                # 超时，变回 active
                user["status"] = "active"
                user.pop("pair_id", None)
                user.pop("matched_partner", None)
                user.pop("pending_at", None)
                print(f"用户 {user['name']} pending 超时，已变回 active")


@app.route('/api/create_activity', methods=['POST'])
def create_activity():
    """创建活动并生成群口令"""
    try:
        data = request.json
        event_name = data.get('event_name', '')
        city = data.get('city', '')
        date = data.get('date', '')
        custom_suffix = data.get('custom_suffix', '')
        contact_name = data.get('contact_name', '')
        contact_phone = data.get('contact_phone', '')
        contact_email = data.get('contact_email', '')
        note = data.get('note', '')

        if not event_name or not city or not date:
            return jsonify({"success": False, "message": "缺少必要参数"}), 400

        if not contact_name or not contact_phone:
            return jsonify({"success": False, "message": "请填写联系方式"}), 400

        if not contact_email:
            return jsonify({"success": False, "message": "请填写邮箱地址"}), 400

        group_code = generate_group_code(event_name, city, date, custom_suffix)

        # 保存口令和联系信息
        room_data = load_data()
        if "activities" not in room_data:
            room_data["activities"] = []
        if "activity_contacts" not in room_data:
            room_data["activity_contacts"] = {}

        if group_code not in room_data["activities"]:
            room_data["activities"].append(group_code)

        # 保存联系信息
        room_data["activity_contacts"][group_code] = {
            "event_name": event_name,
            "city": city,
            "date": date,
            "custom_suffix": custom_suffix,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "note": note,
            "created_at": time.time()
        }

        save_data(room_data)

        # 发送邮件通知：新群口令生成
        email_body = f"""新群口令已生成

活动信息：
- 活动名称：{event_name}
- 城市：{city}
- 日期：{date}
- 自定义后缀：{custom_suffix if custom_suffix else '无'}
- 生成的群口令：{group_code}

联系人信息：
- 姓名：{contact_name}
- 手机号：{contact_phone}
- 邮箱：{contact_email if contact_email else '未填写'}
- 备注：{note if note else '无'}
"""
        send_email_notification(
            f"[Roomie] 新群口令生成 - {group_code}",
            email_body
        )

        return jsonify({
            "success": True,
            "group_code": group_code,
            "message": "群口令生成成功"
        })

    except Exception as e:
        print(f"创建活动错误: {e}")
        return jsonify({"success": False, "message": "创建失败"}), 500


@app.route('/api/login', methods=['POST'])
def wechat_login():
    """微信登录接口"""
    try:
        data = request.json
        code = data.get('code')

        if not code:
            return jsonify({"success": False, "message": "缺少code参数"}), 400

        url = f"https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": WECHAT_APPID,
            "secret": WECHAT_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }

        response = requests.get(url, params=params)
        result = response.json()

        if "openid" in result:
            return jsonify({
                "success": True,
                "openid": result["openid"]
            })
        else:
            return jsonify({
                "success": False,
                "message": result.get("errmsg", "登录失败")
            }), 400

    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({"success": False, "message": "登录失败"}), 500


@app.route('/api/submit', methods=['POST'])
def submit_form():
    """提交表单接口"""
    try:
        data = request.json
        required_fields = ['name', 'wechat_id', 'gender', 'check_in', 'check_out', 'smoking', 'schedule', 'noise_in', 'noise_out', 'group_code']

        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"缺少字段: {field}"}), 400

        # 微信号统一转小写，避免大小写不同导致重复记录
        data['wechat_id'] = data['wechat_id'].strip().lower()

        # has_booked 可选，前端不传则默认 no
        data.setdefault('has_booked', 'no')

        room_data = load_data()

        # 清理过期的 pending 状态
        clean_expired_pending(room_data)

        # 获取 openid（可选字段）
        openid = data.get('openid', '')

        # 使用 openid 或 wechat_id 进行匹配
        user_identifier = openid if openid else data["wechat_id"]

        # 查找现有用户（优先使用 openid，否则使用 wechat_id）
        existing_user = None
        if openid:
            existing_user = next((u for u in room_data["users"] if u.get("openid") == openid and u["group_code"] == data["group_code"]), None)
        if not existing_user:
            existing_user = next((u for u in room_data["users"] if u["wechat_id"] == data["wechat_id"] and u["group_code"] == data["group_code"]), None)

        # 同名不同微信号检测（排除 removed 状态）
        if not existing_user:
            name_conflict = next((u for u in room_data["users"]
                if u["name"] == data["name"]
                and u["group_code"] == data["group_code"]
                and u["wechat_id"] != data["wechat_id"]
                and u.get("status") != "removed"), None)
            if name_conflict:
                return jsonify({
                    "success": False,
                    "duplicate_name": True,
                    "existing_wechat": name_conflict["wechat_id"],
                    "message": f"系统中已有一条您的记录（微信号：{name_conflict['wechat_id']}），可能导致被重复联系。请确认您的微信号是否填写正确。"
                })

        if existing_user:
            if existing_user["status"] == "matched" or existing_user["status"] == "pending":
                # 查找匹配的伙伴
                if openid and existing_user.get("openid"):
                    matched_partner = next((u for u in room_data["users"] if u.get("pair_id") == existing_user.get("pair_id") and u.get("openid") != openid), None)
                else:
                    matched_partner = next((u for u in room_data["users"] if u.get("pair_id") == existing_user.get("pair_id") and u["wechat_id"] != data["wechat_id"]), None)

                if matched_partner:
                    # 判断日期匹配类型
                    date_match_type = "full"
                    if (existing_user["check_in"] != matched_partner["check_in"] or
                        existing_user["check_out"] != matched_partner["check_out"]):
                        date_match_type = "partial"

                    # 判断是否是 pending 状态（新匹配）
                    is_pending = (existing_user["status"] == "pending")

                    return jsonify({
                        "success": True,
                        "matched": True,
                        "is_pending": is_pending,
                        "date_match_type": date_match_type,
                        "match_info": {
                            "name": matched_partner["name"],
                            "wechat_id": matched_partner["wechat_id"],
                            "check_in": matched_partner["check_in"],
                            "check_out": matched_partner["check_out"],
                            "smoking": matched_partner["smoking"],
                            "schedule": matched_partner["schedule"],
                            "noise_in": matched_partner["noise_in"],
                            "noise_out": matched_partner["noise_out"]
                        },
                        "message": "您已匹配成功" if not is_pending else "找到匹配，请确认"
                    })

            existing_user["submit_count"] = existing_user.get("submit_count", 0) + 1
            for key in required_fields:
                if key in data:
                    existing_user[key] = data[key]
            if openid:
                existing_user["openid"] = openid
            # 使用existing_user作为new_user（避免创建重复记录）
            new_user = existing_user
        else:
            # 新用户，创建记录
            new_user = {
                "name": data["name"],
                "wechat_id": data["wechat_id"],
                "gender": data["gender"],
                "check_in": data["check_in"],
                "check_out": data["check_out"],
                "smoking": data["smoking"],
                "schedule": data["schedule"],
                "noise_in": data["noise_in"],
                "noise_out": data["noise_out"],
                "has_booked": data.get("has_booked", "no"),
                "group_code": data["group_code"],
                "status": "active",
                "created_at": time.time(),
                "submit_count": 1,
                "history": []
            }

            if openid:
                new_user["openid"] = openid

        # 获取历史匹配记录（用于排除）
        history_ids = new_user.get("history", [])

        # 第一次提交：严格匹配
        matched_user = None
        submit_count = new_user["submit_count"]

        if submit_count < 2:
            # 第一次提交：严格匹配所有条件
            for user in room_data["users"]:
                # 跳过自己
                if openid and user.get("openid") == openid:
                    continue
                if not openid and user["wechat_id"] == data["wechat_id"]:
                    continue
                # 跳过同名同群的人（防止填错微信号后匹配到自己）
                if user["name"] == data["name"] and user["group_code"] == data["group_code"]:
                    continue

                # 跳过历史匹配过的人
                user_id = user.get("openid") if user.get("openid") else user["wechat_id"]
                if user_id in history_ids:
                    continue

                if (user["status"] == "active" and
                    user["group_code"] == data["group_code"] and
                    user["gender"] == data["gender"] and
                    user["check_in"] == data["check_in"] and
                    user["check_out"] == data["check_out"] and
                    smoking_ok(user.get("smoking","no"), data["smoking"]) and
                    schedule_ok(user.get("schedule","early_bird"), data["schedule"])):

                    # 两人都已订房则不匹配
                    if data.get("has_booked", "no") == "yes" and user.get("has_booked", "no") == "yes":
                        continue

                    # 噪音兼容性检查
                    if data["noise_in"] == "weak" and user["noise_out"] != "silent":
                        continue
                    if user["noise_in"] == "weak" and data["noise_out"] != "silent":
                        continue
                    if data["noise_in"] == "medium" and user["noise_out"] == "bass":
                        continue
                    if user["noise_in"] == "medium" and data["noise_out"] == "bass":
                        continue
                    if data["noise_out"] == "bass" and user["noise_in"] != "strong":
                        continue
                    if user["noise_out"] == "bass" and data["noise_in"] != "strong":
                        continue

                    matched_user = user
                    break

            # 严格匹配失败，检查是否有日期包含关系（对方日期是当前用户日期的子集）
            if not matched_user:
                for user in room_data["users"]:
                    if openid and user.get("openid") == openid:
                        continue
                    if not openid and user["wechat_id"] == data["wechat_id"]:
                        continue
                    user_id = user.get("openid") if user.get("openid") else user["wechat_id"]
                    if user_id in history_ids:
                        continue
                    if (user["status"] == "active" and
                        user["group_code"] == data["group_code"] and
                        user["gender"] == data["gender"] and
                        smoking_ok(user.get("smoking","no"), data["smoking"]) and
                        schedule_ok(user.get("schedule","early_bird"), data["schedule"]) and
                        user["check_in"] >= data["check_in"] and
                        user["check_out"] <= data["check_out"] and
                        not (user["check_in"] == data["check_in"] and user["check_out"] == data["check_out"])):
                        if data.get("has_booked", "no") == "yes" and user.get("has_booked", "no") == "yes":
                            continue
                        noise_ok = True
                        if data["noise_in"] == "weak" and user["noise_out"] != "silent":
                            noise_ok = False
                        if user["noise_in"] == "weak" and data["noise_out"] != "silent":
                            noise_ok = False
                        if data["noise_in"] == "medium" and user["noise_out"] == "bass":
                            noise_ok = False
                        if user["noise_in"] == "medium" and data["noise_out"] == "bass":
                            noise_ok = False
                        if data["noise_out"] == "bass" and user["noise_in"] != "strong":
                            noise_ok = False
                        if user["noise_out"] == "bass" and data["noise_in"] != "strong":
                            noise_ok = False
                        if noise_ok:
                            matched_user = user
                            break
        else:
            # 第二次及以后提交：先尝试严格匹配（日期完全一致，不限submit_count）
            for user in room_data["users"]:
                if openid and user.get("openid") == openid:
                    continue
                if not openid and user["wechat_id"] == data["wechat_id"]:
                    continue
                # 跳过同名同群的人（防止填错微信号后匹配到自己）
                if user["name"] == data["name"] and user["group_code"] == data["group_code"]:
                    continue
                user_id = user.get("openid") if user.get("openid") else user["wechat_id"]
                if user_id in history_ids:
                    continue
                if (user["status"] == "active" and
                    user["group_code"] == data["group_code"] and
                    user["gender"] == data["gender"] and
                    user["check_in"] == data["check_in"] and
                    user["check_out"] == data["check_out"] and
                    smoking_ok(user.get("smoking","no"), data["smoking"]) and
                    schedule_ok(user.get("schedule","early_bird"), data["schedule"])):
                    noise_ok = True
                    if data["noise_in"] == "weak" and user["noise_out"] != "silent":
                        noise_ok = False
                    if user["noise_in"] == "weak" and data["noise_out"] != "silent":
                        noise_ok = False
                    if data["noise_in"] == "medium" and user["noise_out"] == "bass":
                        noise_ok = False
                    if user["noise_in"] == "medium" and data["noise_out"] == "bass":
                        noise_ok = False
                    if data["noise_out"] == "bass" and user["noise_in"] != "strong":
                        noise_ok = False
                    if user["noise_out"] == "bass" and data["noise_in"] != "strong":
                        noise_ok = False
                    if noise_ok:
                        matched_user = user
                        break

            # 严格匹配没找到，再用放宽逻辑（日期有交集，只找submit_count>=2的用户）
            if not matched_user:
                partial_matches = []
                for user in room_data["users"]:
                    if openid and user.get("openid") == openid:
                        continue
                    if not openid and user["wechat_id"] == data["wechat_id"]:
                        continue
                    user_id = user.get("openid") if user.get("openid") else user["wechat_id"]
                    if user_id in history_ids:
                        continue
                    # 放宽逻辑仍然只匹配第二次及以后提交的用户
                    if user.get("submit_count", 1) < 2:
                        continue

                    if (user["status"] == "active" and
                            user["group_code"] == data["group_code"] and
                            user["gender"] == data["gender"] and
                            smoking_ok(user.get("smoking","no"), data["smoking"]) and
                            schedule_ok(user.get("schedule","early_bird"), data["schedule"])):

                        # 检查噪音兼容性
                        noise_compatible = True
                        if data["noise_in"] == "weak" and user["noise_out"] != "silent":
                            noise_compatible = False
                        if user["noise_in"] == "weak" and data["noise_out"] != "silent":
                            noise_compatible = False
                        if data["noise_in"] == "medium" and user["noise_out"] == "bass":
                            noise_compatible = False
                        if user["noise_in"] == "medium" and data["noise_out"] == "bass":
                            noise_compatible = False
                        if data["noise_out"] == "bass" and user["noise_in"] != "strong":
                            noise_compatible = False
                        if user["noise_out"] == "bass" and data["noise_in"] != "strong":
                            noise_compatible = False

                        if noise_compatible:
                            # 计算日期重叠
                            has_overlap, overlap_start, overlap_end = calculate_date_overlap(
                                data["check_in"], data["check_out"],
                                user["check_in"], user["check_out"]
                            )

                            if has_overlap:
                                partial_matches.append({
                                    "user": user,
                                    "overlap_start": overlap_start,
                                    "overlap_end": overlap_end
                                })

            # 如果有部分匹配，选择重叠天数最多的
            if partial_matches:
                best_match = max(partial_matches, key=lambda x: (
                    datetime.strptime(x["overlap_end"], '%Y-%m-%d') -
                    datetime.strptime(x["overlap_start"], '%Y-%m-%d')
                ).days)
                matched_user = best_match["user"]

        if matched_user:
            pair_id = f"PAIR_{int(time.time())}"
            matched_user["status"] = "pending"
            matched_user["pair_id"] = pair_id
            matched_user["pending_at"] = time.time()
            new_user["status"] = "pending"
            new_user["pair_id"] = pair_id
            new_user["pending_at"] = time.time()

            # 判断日期匹配类型
            date_match_type = "exact"
            if (new_user["check_in"] != matched_user["check_in"] or
                new_user["check_out"] != matched_user["check_out"]):
                date_match_type = "partial"

            # 保存匹配对象信息，方便查看
            matched_user["matched_partner"] = {
                "name": new_user["name"],
                "wechat_id": new_user["wechat_id"]
            }
            new_user["matched_partner"] = {
                "name": matched_user["name"],
                "wechat_id": matched_user["wechat_id"]
            }

            # 注意：不在这里添加到历史记录，等用户确认或拒绝时再添加

            if not existing_user:
                room_data["users"].append(new_user)

            save_data(room_data)

            # 发送邮件通知：匹配成功
            email_body = f"""拼房匹配成���！

群口令：{data['group_code']}

用户A：{new_user['name']}
性别：{new_user['gender']}
日期：{new_user['check_in']} - {new_user['check_out']}

用户B：{matched_user['name']}
性别：{matched_user['gender']}
日期：{matched_user['check_in']} - {matched_user['check_out']}

匹配类型：{'完全匹配' if date_match_type == 'exact' else '部分匹配'}
状态：等待双方确认
"""
            send_email_notification(
                f"[Roomie] 匹配成功 - {new_user['name']} & {matched_user['name']}",
                email_body
            )
            append_log(room_data, "matched", new_user["name"], matched_user["name"], data["group_code"])
            save_data(room_data)

            return jsonify({
                "success": True,
                "matched": True,
                "is_pending": True,  # 新匹配，pending 状态
                "date_match_type": date_match_type,
                "match_info": {
                    "name": matched_user["name"],
                    "wechat_id": matched_user["wechat_id"],
                    "check_in": matched_user["check_in"],
                    "check_out": matched_user["check_out"],
                    "smoking": matched_user["smoking"],
                    "schedule": matched_user["schedule"],
                    "noise_in": matched_user["noise_in"],
                    "noise_out": matched_user["noise_out"]
                },
                "message": "匹配成功！"
            })
        else:
            if not existing_user:
                room_data["users"].append(new_user)

            save_data(room_data)

            # 发送邮件通知：新用户提交
            email_body = f"""新用户提交拼房信息

群口令：{data['group_code']}
姓名：{data['name']}
性别：{data['gender']}
入住日期：{data['check_in']} - {data['check_out']}
吸烟：{data['smoking']}
作息：{data['schedule']}
抗噪：{data['noise_in']}
出声：{data['noise_out']}

状态：等待匹配
"""
            send_email_notification(
                f"[Roomie] 新用户提交 - {data['name']}",
                email_body
            )

            return jsonify({
                "success": True,
                "matched": False,
                "message": "已入池。若有需求匹配的群友，会联系你。若 24 小时无人联系，请微调习惯再次尝试匹配。"
            })

    except Exception as e:
        print(f"提交错误: {e}")
        return jsonify({"success": False, "message": "提交失败"}), 500


@app.route('/api/confirm', methods=['POST'])
def confirm_match():
    """确认匹配（从 pending 变为 matched）"""
    try:
        data = request.json
        wechat_id = data.get('wechat_id')
        group_code = data.get('group_code')
        openid = data.get('openid', '')

        if not wechat_id or not group_code:
            return jsonify({"success": False, "message": "缺少参数"}), 400

        room_data = load_data()

        # 查找用户
        user = None
        if openid:
            user = next((u for u in room_data["users"] if u.get("openid") == openid and u["group_code"] == group_code), None)
        if not user:
            user = next((u for u in room_data["users"] if u["wechat_id"] == wechat_id and u["group_code"] == group_code), None)

        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        if user["status"] != "pending":
            return jsonify({"success": False, "message": "当前不是待确认状态"}), 400

        pair_id = user.get("pair_id")
        if pair_id:
            # 找到配对的两个用户，都变为 matched
            paired_users = [u for u in room_data["users"] if u.get("pair_id") == pair_id]

            if len(paired_users) == 2:
                user_a, user_b = paired_users[0], paired_users[1]

                # 获取双方的 ID
                user_a_id = user_a.get("openid") if user_a.get("openid") else user_a["wechat_id"]
                user_b_id = user_b.get("openid") if user_b.get("openid") else user_b["wechat_id"]

                # 双方互相加入历史记忆
                if "history" not in user_a:
                    user_a["history"] = []
                if user_b_id not in user_a["history"]:
                    user_a["history"].append(user_b_id)

                if "history" not in user_b:
                    user_b["history"] = []
                if user_a_id not in user_b["history"]:
                    user_b["history"].append(user_a_id)

                # 变为 matched 状态
                confirmed_at = time.time()
                for u in paired_users:
                    u["status"] = "matched"
                    u["confirmed_at"] = confirmed_at
                    u.pop("pending_at", None)

                # 更新统计
                room_data["stats"]["total_matches"] += 1
                append_log(room_data, "confirmed", user_a["name"], user_b["name"], group_code)

        save_data(room_data)

        return jsonify({"success": True, "message": "匹配确认成功"})

    except Exception as e:
        print(f"确认匹配错误: {e}")
        return jsonify({"success": False, "message": "操作失败"}), 500


@app.route('/api/reject', methods=['POST'])
def reject_match():
    """拒绝匹配（从 pending 变回 active，并加入历史记忆）"""
    try:
        data = request.json
        wechat_id = data.get('wechat_id')
        group_code = data.get('group_code')
        openid = data.get('openid', '')

        if not wechat_id or not group_code:
            return jsonify({"success": False, "message": "缺少参数"}), 400

        room_data = load_data()

        # 查找用户
        user = None
        if openid:
            user = next((u for u in room_data["users"] if u.get("openid") == openid and u["group_code"] == group_code), None)
        if not user:
            user = next((u for u in room_data["users"] if u["wechat_id"] == wechat_id and u["group_code"] == group_code), None)

        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        if user["status"] != "pending":
            return jsonify({"success": False, "message": "当前不是待确认状态"}), 400

        pair_id = user.get("pair_id")
        if pair_id:
            # 找到配对的两个用户
            paired_users = [u for u in room_data["users"] if u.get("pair_id") == pair_id]

            if len(paired_users) == 2:
                user_a, user_b = paired_users[0], paired_users[1]

                # 获取双方的 ID
                user_a_id = user_a.get("openid") if user_a.get("openid") else user_a["wechat_id"]
                user_b_id = user_b.get("openid") if user_b.get("openid") else user_b["wechat_id"]

                # 双方互相加入历史记忆（防止再次匹配）
                if "history" not in user_a:
                    user_a["history"] = []
                if user_b_id not in user_a["history"]:
                    user_a["history"].append(user_b_id)

                if "history" not in user_b:
                    user_b["history"] = []
                if user_a_id not in user_b["history"]:
                    user_b["history"].append(user_a_id)

            # 双方都变回 active 状态
            for u in room_data["users"]:
                if u.get("pair_id") == pair_id:
                    u["status"] = "active"
                    u.pop("pair_id", None)
                    u.pop("matched_partner", None)
                    u.pop("pending_at", None)

            append_log(room_data, "rejected", user_a["name"], user_b["name"], group_code)

        save_data(room_data)

        return jsonify({"success": True, "message": "已拒绝此匹配"})

    except Exception as e:
        print(f"拒绝匹配错误: {e}")
        return jsonify({"success": False, "message": "操作失败"}), 500


@app.route('/api/unmatch', methods=['POST'])
def unmatch():
    """解除匹配"""
    try:
        data = request.json
        wechat_id = data.get('wechat_id')
        group_code = data.get('group_code')
        openid = data.get('openid', '')

        if not wechat_id or not group_code:
            return jsonify({"success": False, "message": "缺少参数"}), 400

        room_data = load_data()

        # 查找用户（优先使用 openid）
        user = None
        if openid:
            user = next((u for u in room_data["users"] if u.get("openid") == openid and u["group_code"] == group_code), None)
        if not user:
            user = next((u for u in room_data["users"] if u["wechat_id"] == wechat_id and u["group_code"] == group_code), None)

        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        if user["status"] != "matched":
            return jsonify({"success": False, "message": "当前未匹配"}), 400

        pair_id = user.get("pair_id")
        if pair_id:
            # 找到配对的两个用户
            paired_users = [u for u in room_data["users"] if u.get("pair_id") == pair_id]

            if len(paired_users) == 2:
                user_a, user_b = paired_users[0], paired_users[1]

                # 获取双方的 ID
                user_a_id = user_a.get("openid") if user_a.get("openid") else user_a["wechat_id"]
                user_b_id = user_b.get("openid") if user_b.get("openid") else user_b["wechat_id"]

                # 双方互相加入历史记忆
                if "history" not in user_a:
                    user_a["history"] = []
                if user_b_id not in user_a["history"]:
                    user_a["history"].append(user_b_id)

                if "history" not in user_b:
                    user_b["history"] = []
                if user_a_id not in user_b["history"]:
                    user_b["history"].append(user_a_id)

            # 解除匹配状态
            for u in room_data["users"]:
                if u.get("pair_id") == pair_id:
                    u["status"] = "active"
                    u.pop("pair_id", None)
                    u.pop("matched_partner", None)

            confirmed_at = user_a.get("confirmed_at") or user_b.get("confirmed_at")
            minutes = round((time.time() - confirmed_at) / 60) if confirmed_at else None
            note = f"by:{user['name']}" + (f" after:{minutes}min" if minutes is not None else "")
            append_log(room_data, "unmatched", user_a["name"], user_b["name"], group_code, note=note)

        save_data(room_data)

        return jsonify({"success": True, "message": "已解除匹配"})

    except Exception as e:
        print(f"解除匹配错误: {e}")
        return jsonify({"success": False, "message": "操作失败"}), 500


@app.route('/api/check_code', methods=['GET', 'POST'])
def check_code():
    """验证群口令是否存在"""
    try:
        # 支持GET和POST两种方式
        if request.method == 'GET':
            group_code = request.args.get('group_code', '').strip().upper()
        else:
            data = request.json
            group_code = data.get('group_code', '').strip().upper()

        if not group_code:
            return jsonify({"success": False, "message": "请输入群口令"}), 400

        room_data = load_data()

        # 清理过期的 pending 状态
        clean_expired_pending(room_data)
        save_data(room_data)

        group_users = [u for u in room_data["users"] if u["group_code"] == group_code]
        activities = room_data.get("activities", [])

        if not group_users and group_code not in activities:
            return jsonify({"success": False, "message": "群口令不存在，请检查后重试"}), 404

        # 统计等待匹配和已匹配的用户数
        active_count = len([u for u in group_users if u["status"] == "active"])
        pending_count = len([u for u in group_users if u["status"] == "pending"])
        matched_count = len([u for u in group_users if u["status"] == "matched"])

        return jsonify({
            "success": True,
            "exists": True,
            "active_count": active_count,
            "pending_count": pending_count,
            "matched_count": matched_count,
            "message": f"此口令下有{active_count}位用户等待匹配，{pending_count}位待确认，{matched_count}位已匹配"
        })

    except Exception as e:
        print(f"验证口令错误: {e}")
        return jsonify({"success": False, "message": "验证失败"}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    try:
        room_data = load_data()
        total_users = len(room_data["users"])
        total_matches = room_data["stats"].get("total_matches", 0)

        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_matches": total_matches
            }
        })

    except Exception as e:
        print(f"获取统计错误: {e}")
        return jsonify({"success": False, "message": "获取失败"}), 500


@app.route('/api/check_match', methods=['POST'])
def check_match():
    """检查用户匹配状态"""
    try:
        data = request.json
        wechat_id = data.get('wechat_id')
        group_code = data.get('group_code')
        openid = data.get('openid', '')

        if not wechat_id or not group_code:
            return jsonify({"success": False, "message": "缺少参数"}), 400

        room_data = load_data()

        # 查找用户（优先使用 openid）
        user = None
        if openid:
            user = next((u for u in room_data["users"] if u.get("openid") == openid and u["group_code"] == group_code), None)
        if not user:
            user = next((u for u in room_data["users"] if u["wechat_id"] == wechat_id and u["group_code"] == group_code), None)

        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        if user["status"] == "matched":
            # 查找匹配的伙伴
            if openid and user.get("openid"):
                matched_partner = next((u for u in room_data["users"] if u.get("pair_id") == user.get("pair_id") and u.get("openid") != openid), None)
            else:
                matched_partner = next((u for u in room_data["users"] if u.get("pair_id") == user.get("pair_id") and u["wechat_id"] != wechat_id), None)

            if matched_partner:
                return jsonify({
                    "success": True,
                    "matched": True,
                    "match_info": {
                        "name": matched_partner["name"],
                        "wechat_id": matched_partner["wechat_id"],
                        "check_in": matched_partner["check_in"],
                        "check_out": matched_partner["check_out"]
                    }
                })

        return jsonify({"success": True, "matched": False, "message": "等待匹配中"})

    except Exception as e:
        print(f"检查匹配错误: {e}")
        return jsonify({"success": False, "message": "检查失败"}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """查看操作日志"""
    room_data = load_data()
    logs = room_data.get("logs", [])
    group_code = request.args.get("group_code")
    if group_code:
        logs = [l for l in logs if l.get("group") == group_code]
    return jsonify({"logs": list(reversed(logs))})  # 最新的在前


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": time.time()})


@app.route('/', methods=['GET'])
def index():
    """网页版入口"""
    return send_file('index.html')


@app.route('/shenzhen', methods=['GET'])
def shenzhen_index():
    """深圳游学分享报名"""
    return send_file('shenzhen.html')


@app.route('/api/wish', methods=['POST'])
def submit_wish():
    """提交想法/建议/问题/表扬"""
    try:
        data = request.json
        wish_type = data.get('type', 'suggestion')
        content = data.get('content', '').strip()
        contact = data.get('contact', '').strip()
        is_public = data.get('is_public', True)
        openid = data.get('openid', '')

        if not content:
            return jsonify({"success": False, "message": "内容不能为空"}), 400

        # 加载现有数据
        try:
            with open(WISH_FILE, 'r', encoding='utf-8') as f:
                wishes_data = json.load(f)
        except FileNotFoundError:
            wishes_data = {"wishes": []}

        # 创建新记录
        new_wish = {
            "type": wish_type,
            "content": content,
            "contact": contact,
            "is_public": is_public,
            "openid": openid,
            "created_at": time.time(),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        wishes_data["wishes"].append(new_wish)

        # 保存数据
        with open(WISH_FILE, 'w', encoding='utf-8') as f:
            json.dump(wishes_data, f, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "message": "提交成功"
        })

    except Exception as e:
        print(f"提交许愿错误: {e}")
        return jsonify({"success": False, "message": "提交失败"}), 500


@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    schedule_map = {"early_bird": "早起型", "night_owl": "夜猫型", "any": "我不介意"}
    noise_in_map = {"weak": "轻度敏感", "medium": "适中", "strong": "耐受力强"}
    noise_out_map = {"silent": "安静", "medium": "适中", "loud": "较吵", "bass": "低音炮"}

    room_data = load_data()

    users = room_data.get("users", [])
    group_code = request.args.get("group_code", "HHHZ0327")
    target_users = [u for u in users if u.get("group_code") == group_code]

    matched = [u for u in target_users if u.get("status") == "matched"]
    active = [u for u in target_users if u.get("status") == "active"]

    seen_pairs = set()
    pairs = []
    for u in matched:
        pid = u.get("pair_id", "")
        if pid and pid not in seen_pairs:
            seen_pairs.add(pid)
            partner = next((x for x in matched if x.get("pair_id") == pid and x["wechat_id"] != u["wechat_id"]), None)
            if partner:
                pairs.append({
                    "A": {"name": u["name"], "gender": "女" if u["gender"] == "female" else "男",
                          "check_in": u["check_in"], "check_out": u["check_out"],
                          "smoking": {"yes":"吸烟","no":"不吸烟","any":"我不介意"}.get(u.get("smoking","no"),"不吸烟"),
                          "schedule": schedule_map.get(u["schedule"], u["schedule"]),
                          "noise_out": noise_out_map.get(u["noise_out"], u["noise_out"])},
                    "B": {"name": partner["name"], "gender": "女" if partner["gender"] == "female" else "男",
                          "check_in": partner["check_in"], "check_out": partner["check_out"],
                          "smoking": {"yes":"吸烟","no":"不吸烟","any":"我不介意"}.get(partner.get("smoking","no"),"不吸烟"),
                          "schedule": schedule_map.get(partner["schedule"], partner["schedule"]),
                          "noise_out": noise_out_map.get(partner["noise_out"], partner["noise_out"])}
                })

    waiting = []
    for u in active:
        waiting.append({
            "name": u["name"],
            "gender": "女" if u["gender"] == "female" else "男",
            "check_in": u["check_in"],
            "check_out": u["check_out"],
            "smoking": {"yes":"吸烟","no":"不吸烟","any":"我不介意"}.get(u.get("smoking","no"),"不吸烟"),
            "schedule": schedule_map.get(u["schedule"], u["schedule"]),
            "noise_in": noise_in_map.get(u["noise_in"], u["noise_in"]),
            "noise_out": noise_out_map.get(u["noise_out"], u["noise_out"]),
            "contact": u.get("wechat_id", ""),
            "submit_count": u.get("submit_count", 1)
        })

    return jsonify({
        "group_code": group_code,
        "summary": {
            "total": len(target_users),
            "matched_pairs": len(pairs),
            "matched_users": len(matched),
            "waiting": len(active)
        },
        "matched_pairs": pairs,
        "waiting_users": waiting
    })


# ══════════════════════════════════════════════════════════
# 深圳游学分享报名系统
# ══════════════════════════════════════════════════════════

SHENZHEN_FILE = "/root/Roomie-Claude/shenzhen_data.json"
SHENZHEN_ADMIN_PASSWORD = "szyx2026"


def load_shenzhen():
    try:
        with open(SHENZHEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"topics": [], "signups": []}


def save_shenzhen(data):
    with open(SHENZHEN_FILE, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def check_admin(req):
    return req.headers.get('X-Admin-Password') == SHENZHEN_ADMIN_PASSWORD


@app.route('/api/shenzhen/propose', methods=['POST'])
def shenzhen_propose():
    body = request.get_json()
    name = (body.get('name') or '').strip()
    company = (body.get('company') or '').strip()
    job_title = (body.get('job_title') or '').strip()
    topic = (body.get('topic') or '').strip()
    desc = (body.get('desc') or '').strip()
    phone = (body.get('phone') or '').strip()

    if not all([name, company, job_title, topic, phone]):
        return jsonify({"success": False, "message": "请填写所有必填项"})

    data = load_shenzhen()

    # 同手机号已提交过主题
    existing = next((t for t in data['topics'] if t['phone'] == phone and not t.get('cancelled')), None)
    if existing:
        return jsonify({"success": False, "message": "你已提交过分享话题"})

    # 已报名的人不能再提交主题
    signup = next((s for s in data['signups'] if s['phone'] == phone), None)
    if signup:
        return jsonify({"success": False, "message": "你已报名了其他话题，不能再提交分享"})

    topic_id = hashlib.md5((phone + str(time.time())).encode()).hexdigest()[:12]
    data['topics'].append({
        "id": topic_id,
        "name": name,
        "company": company,
        "job_title": job_title,
        "topic": topic,
        "desc": desc,
        "phone": phone,
        "created_at": time.time(),
        "cancelled": False
    })
    save_shenzhen(data)
    return jsonify({"success": True})


@app.route('/api/shenzhen/topics', methods=['GET'])
def shenzhen_topics():
    data = load_shenzhen()
    # 统计每个话题报名人数（只统计未取消话题的有效报名）
    result = []
    for t in data['topics']:
        count = sum(1 for s in data['signups'] if s['topic_id'] == t['id'])
        result.append({
            "id": t['id'],
            "name": t['name'],
            "company": t['company'],
            "job_title": t['job_title'],
            "topic": t['topic'],
            "desc": t.get('desc', ''),
            "count": count,
            "cancelled": t.get('cancelled', False)
        })
    # 按报名人数降序，取消的排最后
    result.sort(key=lambda x: (x['cancelled'], -x['count']))
    return jsonify({"topics": result})


@app.route('/api/shenzhen/signup', methods=['POST'])
def shenzhen_signup():
    body = request.get_json()
    name = (body.get('name') or '').strip()
    phone = (body.get('phone') or '').strip()
    topic_id = (body.get('topic_id') or '').strip()

    if not all([name, phone, topic_id]):
        return jsonify({"success": False, "message": "参数不完整"})

    data = load_shenzhen()

    # 话题是否存在且未取消
    topic = next((t for t in data['topics'] if t['id'] == topic_id and not t.get('cancelled')), None)
    if not topic:
        return jsonify({"success": False, "message": "该话题不存在或已取消"})

    # 分享者不能报名
    is_proposer = any(t['phone'] == phone and not t.get('cancelled') for t in data['topics'])
    if is_proposer:
        return jsonify({"success": False, "is_proposer": True, "message": "你已提交过分享话题，不能同时报名"})

    # 是否已报名（改报名则覆盖）
    existing = next((s for s in data['signups'] if s['phone'] == phone), None)
    changed = existing is not None and existing['topic_id'] != topic_id

    if existing:
        existing['topic_id'] = topic_id
        existing['name'] = name
        existing['updated_at'] = time.time()
    else:
        data['signups'].append({
            "phone": phone,
            "name": name,
            "topic_id": topic_id,
            "created_at": time.time()
        })

    save_shenzhen(data)
    return jsonify({"success": True, "changed": changed, "topic_name": topic['topic']})


@app.route('/api/shenzhen/check_signup', methods=['GET'])
def shenzhen_check_signup():
    phone = request.args.get('phone', '').strip()
    if not phone:
        return jsonify({"cancelled": False})

    data = load_shenzhen()
    signup = next((s for s in data['signups'] if s['phone'] == phone), None)
    if not signup:
        return jsonify({"cancelled": False})

    topic = next((t for t in data['topics'] if t['id'] == signup['topic_id']), None)
    cancelled = topic is None or topic.get('cancelled', False)
    return jsonify({"cancelled": cancelled})


@app.route('/api/shenzhen/admin/topics', methods=['GET'])
def shenzhen_admin_topics():
    if not check_admin(request):
        return jsonify({"message": "无权限"}), 403

    data = load_shenzhen()
    result = []
    for t in data['topics']:
        signups = [{"name": s['name'], "phone": s['phone']}
                   for s in data['signups'] if s['topic_id'] == t['id']]
        result.append({
            "id": t['id'],
            "name": t['name'],
            "company": t['company'],
            "job_title": t['job_title'],
            "topic": t['topic'],
            "desc": t.get('desc', ''),
            "phone": t['phone'],
            "cancelled": t.get('cancelled', False),
            "signups": signups
        })
    result.sort(key=lambda x: (x['cancelled'], -len(x['signups'])))
    return jsonify({"topics": result})


@app.route('/api/shenzhen/admin/delete_topic', methods=['POST'])
def shenzhen_admin_delete():
    if not check_admin(request):
        return jsonify({"success": False, "message": "无权限"}), 403

    body = request.get_json()
    topic_id = (body.get('topic_id') or '').strip()

    data = load_shenzhen()
    topic = next((t for t in data['topics'] if t['id'] == topic_id), None)
    if not topic:
        return jsonify({"success": False, "message": "话题不存在"})

    topic['cancelled'] = True
    save_shenzhen(data)
    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
