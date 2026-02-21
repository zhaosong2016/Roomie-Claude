#!/usr/bin/env python3
import json

# 读取数据
with open('room_data.json', 'r') as f:
    data = json.load(f)

# 删除所有 TESTPENDING 群组的用户
original_count = len(data['users'])
data['users'] = [u for u in data['users'] if u.get('group_code') != 'TESTPENDING']
removed_count = original_count - len(data['users'])

# 保存数据
with open('room_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"清理完成！删除了 {removed_count} 个 TESTPENDING 测试用户")
