import json, time, uuid

with open("/root/Roomie-Claude/room_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

users = data["users"]

# 第一步：解除 YXSZ0410 所有已匹配的人
for u in users:
    if u.get("group_code") == "YXSZ0410" and u.get("status") == "matched":
        u["status"] = "active"
        u["pair_id"] = None
        u["matched_partner"] = None

# 第二步：把已找好室友的4人状态设为 removed
remove_names = {"诸蕾", "孙泉钦", "马淼", "茅书铭"}
for u in users:
    if u.get("group_code") == "YXSZ0410" and u["name"] in remove_names:
        u["status"] = "removed"

# 第三步：重新匹配
def noise_ok(a, b):
    if a["noise_in"] == "weak" and b["noise_out"] != "silent": return False
    if b["noise_in"] == "weak" and a["noise_out"] != "silent": return False
    if a["noise_in"] == "medium" and b["noise_out"] == "bass": return False
    if b["noise_in"] == "medium" and a["noise_out"] == "bass": return False
    if a["noise_out"] == "bass" and b["noise_in"] != "strong": return False
    if b["noise_out"] == "bass" and a["noise_in"] != "strong": return False
    return True

candidates = [u for u in users if u.get("group_code") == "YXSZ0410" and u.get("status") == "active"]

pairs = []
matched_ids = set()

for i, a in enumerate(candidates):
    if a["wechat_id"] in matched_ids:
        continue
    for b in candidates[i+1:]:
        if b["wechat_id"] in matched_ids:
            continue
        if (a["gender"] == b["gender"] and
            a["check_in"] == b["check_in"] and
            a["check_out"] == b["check_out"] and
            a["smoking"] == b["smoking"] and
            a["schedule"] == b["schedule"] and
            noise_ok(a, b)):
            pairs.append((a, b))
            matched_ids.add(a["wechat_id"])
            matched_ids.add(b["wechat_id"])
            break

for a, b in pairs:
    pair_id = "PAIR_" + str(int(time.time())) + "_" + uuid.uuid4().hex[:4]
    for u in users:
        if u["wechat_id"] == a["wechat_id"] and u.get("group_code") == "YXSZ0410":
            u["status"] = "matched"
            u["pair_id"] = pair_id
            u["matched_partner"] = {"name": b["name"], "wechat_id": b["wechat_id"]}
        if u["wechat_id"] == b["wechat_id"] and u.get("group_code") == "YXSZ0410":
            u["status"] = "matched"
            u["pair_id"] = pair_id
            u["matched_partner"] = {"name": a["name"], "wechat_id": a["wechat_id"]}

with open("/root/Roomie-Claude/room_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("=== 匹配结果 ===")
print("参与匹配：" + str(len(candidates)) + " 人，配对：" + str(len(pairs)) + " 对")
print()
for a, b in pairs:
    print("  " + a["name"] + " <-> " + b["name"])

unmatched_names = [u["name"] for u in users if u.get("group_code") == "YXSZ0410" and u.get("status") == "active"]
print()
print("未匹配（" + str(len(unmatched_names)) + " 人）：" + ", ".join(unmatched_names))
print("移除（已找好室友）：" + ", ".join(remove_names))
