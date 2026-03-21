import json
import requests
import os
import shutil
import subprocess

WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/d268c4d9-31b9-49d7-bcb6-ee8156a13c8a"
DATA_FILE = "/root/Roomie-Claude/room_data.json"
SNAPSHOT_FILE = "/root/Roomie-Claude/notify_snapshot.json"
API_HEALTH_URL = "http://127.0.0.1:5000/api/health"

def send_feishu(text):
    try:
        requests.post(WEBHOOK, json={"msg_type": "text", "content": {"text": text}}, timeout=5)
    except Exception as e:
        print(f"发送失败: {e}")

def check_health():
    errors = []

    # 1. API 是否响应
    try:
        r = requests.get(API_HEALTH_URL, timeout=5)
        if r.status_code != 200:
            errors.append(f"API 响应异常（状态码 {r.status_code}）")
    except Exception:
        errors.append("API 无响应，Flask 进程可能已崩溃")

    # 2. 数据文件是否可读
    try:
        with open(DATA_FILE) as f:
            json.load(f)
    except Exception as e:
        errors.append(f"数据文件损坏或不可读：{e}")

    # 3. 磁盘空间
    usage = shutil.disk_usage("/")
    free_gb = usage.free / (1024 ** 3)
    if free_gb < 1.0:
        errors.append(f"磁盘空间不足，剩余 {free_gb:.1f} GB")

    if errors:
        msg = "⚠️ 服务器异常报告\n" + "\n".join(f"• {e}" for e in errors)
        send_feishu(msg)

def load_snapshot():
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE) as f:
            return json.load(f)
    return {"users": [], "matched_pairs": []}

def save_snapshot(snapshot):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, ensure_ascii=False)

def main():
    check_health()

    with open(DATA_FILE) as f:
        data = json.load(f)

    users = data["users"]
    hhhz_users = [u for u in users if u["group_code"] == "HHHZ0327"]
    matched = [u for u in hhhz_users if u["status"] == "matched"]
    active = [u for u in hhhz_users if u["status"] == "active"]

    snapshot = load_snapshot()
    old_wechat_ids = set(snapshot.get("users", []))
    old_pairs = set(snapshot.get("matched_pairs", []))

    # 检测新用户
    new_users = [u for u in hhhz_users if u["wechat_id"] not in old_wechat_ids]

    # 检测新匹配
    current_pairs = set()
    for u in matched:
        pair_id = u.get("pair_id", "")
        if pair_id:
            current_pairs.add(pair_id)
    new_pairs = current_pairs - old_pairs

    messages = []

    if new_users:
        names = "、".join([u["name"] for u in new_users])
        messages.append(
            f"📝 新用户加入（+{len(new_users)}人）：{names}\n"
            f"当前：共 {len(hhhz_users)} 人，{len(matched)} 人已匹配，{len(active)} 人等待"
        )

    if new_pairs:
        for pair_id in new_pairs:
            pair_users = [u for u in matched if u.get("pair_id") == pair_id]
            if len(pair_users) == 2:
                a, b = pair_users
                messages.append(
                    f"🎉 新匹配成功！\n"
                    f"{a['name']} ↔ {b['name']}\n"
                    f"{a['check_in']} ~ {a['check_out']} | {'不吸烟' if a['smoking']=='no' else '吸烟'} | {'早鸟' if a['schedule']=='early_bird' else '夜猫'}\n"
                    f"当前：共 {len(matched)//2} 对已匹配"
                )

    for msg in messages:
        send_feishu(msg)

    # 更新快照
    new_snapshot = {
        "users": [u["wechat_id"] for u in hhhz_users],
        "matched_pairs": list(current_pairs)
    }
    save_snapshot(new_snapshot)

if __name__ == "__main__":
    main()
