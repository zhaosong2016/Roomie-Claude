#!/usr/bin/env python3
import json

# 读取数据
with open('room_data.json', 'r') as f:
    data = json.load(f)

# 筛选 TESTPENDING 群组的用户
testusers = [u for u in data['users'] if u.get('group_code') == 'TESTPENDING']

# 统计各状态用户数
active_count = len([u for u in testusers if u['status'] == 'active'])
pending_count = len([u for u in testusers if u['status'] == 'pending'])
matched_count = len([u for u in testusers if u['status'] == 'matched'])

print(f"TESTPENDING 群组统计：")
print(f"总用户数: {len(testusers)}")
print(f"Active (等待匹配): {active_count}")
print(f"Pending (待确认): {pending_count}")
print(f"Matched (已匹配): {matched_count}")

# 显示前5个用户的状态
if testusers:
    print(f"\n前5个用户状态：")
    for u in testusers[:5]:
        print(f"  {u['name']}: {u['status']}")
