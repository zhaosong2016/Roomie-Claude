"""
API接口模块
提供给小程序调用的HTTP接口
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import hashlib
from data import (
    add_or_update_user,
    get_active_users,
    update_user_status,
    get_stats,
    increment_match_count,
    get_user_by_wechat
)
from match import find_match

app = Flask(__name__)
CORS(app)  # 允许跨域请求

def generate_group_code(event_name: str, city: str, date: str, custom_suffix: str = "") -> str:
    """
    生成群口令

    规则：会议名首字母 + 城市首字母 + 日期(MMDD) + 自定义后缀（可选）
    例如：AI Summit + Beijing + 2026-03-28 + "A组" → ASBJ0328-A组

    如果首字母提取失败，使用哈希值
    """
    try:
        # 提取会议名首字母（取前两个单词）
        event_parts = event_name.strip().split()[:2]
        event_abbr = ''.join([word[0].upper() for word in event_parts if word])

        # 提取城市首字母（取前两个字符）
        city_abbr = city.strip()[:2].upper()

        # 提取日期MMDD
        date_parts = date.split('-')
        if len(date_parts) == 3:
            month_day = date_parts[1] + date_parts[2]
        else:
            month_day = str(int(time.time()))[-4:]

        code = f"{event_abbr}{city_abbr}{month_day}"

        # 如果生成的口令太短，补充哈希值
        if len(code) < 6:
            hash_suffix = hashlib.md5(f"{event_name}{city}{date}".encode()).hexdigest()[:2].upper()
            code += hash_suffix

        # 添加自定义后缀（自动转大写，只允许英文和数字）
        if custom_suffix and custom_suffix.strip():
            suffix = custom_suffix.strip().upper()
            # 验证只包含英文字母和数字
            if not suffix.replace(' ', '').isalnum():
                return jsonify({
                    "success": False,
                    "message": "自定义标识只能包含英文字母和数字"
                }), 400
            # 移除空格
            suffix = suffix.replace(' ', '')
            code = f"{code}-{suffix}"

        return code
    except Exception as e:
        # 如果生成失败，使用时间戳
        return f"EVENT{int(time.time()) % 100000}"

@app.route('/api/create_activity', methods=['POST'])
def create_activity():
    """
    创建活动接口（组织者使用）

    请求参数：
    {
        "event_name": "AI Summit",
        "city": "Beijing",
        "date": "2026-03-28"
    }

    返回：
    {
        "success": true,
        "group_code": "ASBJ0328",
        "message": "活动创建成功"
    }
    """
    try:
        data = request.json

        # 验证必填字段
        required_fields = ['event_name', 'city', 'date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False,
                    "message": f"缺少必填字段: {field}"
                }), 400

        # 生成口令（支持自定义后缀）
        custom_suffix = data.get('custom_suffix', '')
        group_code = generate_group_code(
            data['event_name'],
            data['city'],
            data['date'],
            custom_suffix
        )

        return jsonify({
            "success": True,
            "group_code": group_code,
            "message": "活动创建成功"
        })

    except Exception as e:
        print(f"创建活动错误: {e}")
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        }), 500

@app.route('/api/submit', methods=['POST'])
def submit_form():
    """
    提交表单接口

    请求参数：
    {
        "name": "张三",
        "wechat_id": "zhangsan123",
        "gender": "男",
        "check_in": "2026-03-28",
        "check_out": "2026-03-30",
        "smoking": "否",
        "schedule": "late",
        "noise_in": "normal",
        "noise_out": "mix",
        "group_code": "abc123"
    }

    返回：
    {
        "success": true,
        "matched": true/false,
        "match_info": {
            "name": "李四",
            "wechat_id": "lisi456"
        },
        "message": "匹配成功！" / "已入池等待"
    }
    """
    try:
        data = request.json

        # 验证必填字段
        required_fields = [
            'name', 'wechat_id', 'gender', 'check_in', 'check_out',
            'smoking', 'schedule', 'noise_in', 'noise_out', 'group_code'
        ]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False,
                    "message": f"缺少必填字段: {field}"
                }), 400

        # 创建新用户数据
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
            "group_code": data["group_code"],
            "status": "active"
        }

        # 获取当前群口令下的活跃用户
        active_users = get_active_users(data["group_code"])

        # 寻找匹配
        matched_user = find_match(new_user, active_users)

        if matched_user:
            # 找到匹配
            pair_id = f"PAIR_{int(time.time())}"

            # 更新双方状态
            update_user_status(matched_user["wechat_id"], matched_user["group_code"], "matched", pair_id)
            new_user["status"] = "matched"
            new_user["pair_id"] = pair_id

            # 保存新用户
            add_or_update_user(new_user)

            # 增加匹配计数
            increment_match_count()

            return jsonify({
                "success": True,
                "matched": True,
                "match_info": {
                    "name": matched_user["name"],
                    "wechat_id": matched_user["wechat_id"]
                },
                "message": "匹配成功！"
            })
        else:
            # 未找到匹配，入池等待
            add_or_update_user(new_user)

            return jsonify({
                "success": True,
                "matched": False,
                "message": "已入池。若有需求匹配的群友，会联系你。若 24 小时无人联系，请微调习惯再次尝试匹配。"
            })

    except Exception as e:
        print(f"提交表单错误: {e}")
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        }), 500

@app.route('/api/check_code', methods=['GET'])
def check_code():
    """
    检查群口令接口

    请求参数：
    - group_code: 群口令

    返回：
    {
        "success": true,
        "exists": true,
        "active_count": 5,
        "matched_count": 12,
        "message": "此口令下有用户"
    }
    """
    try:
        group_code = request.args.get('group_code')

        if not group_code:
            return jsonify({
                "success": False,
                "message": "缺少群口令参数"
            }), 400

        # 获取该口令下的统计数据
        stats = get_stats(group_code)
        active_count = stats.get('active_count', 0)

        # 计算已匹配人数（需要查询数据）
        from data import load_data
        data = load_data()
        matched_count = len([
            u for u in data["users"]
            if u.get("group_code") == group_code and u.get("status") == "matched"
        ])

        # 判断是否有用户
        total_users = active_count + matched_count
        exists = total_users > 0

        return jsonify({
            "success": True,
            "exists": exists,
            "active_count": active_count,
            "matched_count": matched_count,
            "message": "此口令下有用户" if exists else "此口令下暂无用户"
        })

    except Exception as e:
        print(f"检查口令错误: {e}")
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    获取统计数据接口

    请求参数：
    - group_code: 群口令（可选）

    返回：
    {
        "success": true,
        "stats": {
            "total_matches": 100,
            "active_count": 5
        }
    }
    """
    try:
        group_code = request.args.get('group_code')
        stats = get_stats(group_code)

        return jsonify({
            "success": True,
            "stats": stats
        })

    except Exception as e:
        print(f"获取统计数据错误: {e}")
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        }), 500

@app.route('/api/check_match', methods=['GET'])
def check_match():
    """
    检查是否有新匹配接口
    用于先来的人刷新页面时查看是否被匹配

    请求参数：
    - wechat_id: 微信号
    - group_code: 群口令

    返回：
    {
        "success": true,
        "matched": true/false,
        "match_info": {
            "name": "李四",
            "wechat_id": "lisi456"
        }
    }
    """
    try:
        wechat_id = request.args.get('wechat_id')
        group_code = request.args.get('group_code')

        if not wechat_id or not group_code:
            return jsonify({
                "success": False,
                "message": "缺少参数"
            }), 400

        user = get_user_by_wechat(wechat_id, group_code)

        if not user:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            }), 404

        if user.get("status") == "matched":
            # 已匹配，返回匹配状态
            return jsonify({
                "success": True,
                "matched": True,
                "message": "你已匹配成功！"
            })
        else:
            return jsonify({
                "success": True,
                "matched": False,
                "message": "暂无匹配"
            })

    except Exception as e:
        print(f"检查匹配错误: {e}")
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "success": True,
        "message": "API运行正常",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    # 生产环境运行
    app.run(host='0.0.0.0', port=5000, debug=False)
