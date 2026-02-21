#!/usr/bin/env python3
"""
生成真机测试用户数据
10个用户，条件设置为容易匹配
"""

import requests
import time

API_URL = "http://49.233.127.228:5000"
GROUP_CODE = "ASBJ0328"  # 使用真实的群口令

# 10个测试用户
test_users = [
    {"name": "张伟", "wechat_id": "zhangwei_test", "gender": "男"},
    {"name": "李娜", "wechat_id": "lina_test", "gender": "女"},
    {"name": "王芳", "wechat_id": "wangfang_test", "gender": "女"},
    {"name": "刘强", "wechat_id": "liuqiang_test", "gender": "男"},
    {"name": "陈静", "wechat_id": "chenjing_test", "gender": "女"},
    {"name": "杨明", "wechat_id": "yangming_test", "gender": "男"},
    {"name": "赵丽", "wechat_id": "zhaoli_test", "gender": "女"},
    {"name": "黄磊", "wechat_id": "huanglei_test", "gender": "男"},
    {"name": "周敏", "wechat_id": "zhoumin_test", "gender": "女"},
    {"name": "吴刚", "wechat_id": "wugang_test", "gender": "男"},
]

# 统一的匹配条件（容易匹配）
common_data = {
    "check_in": "2026-03-05",
    "check_out": "2026-03-08",
    "smoking": "no",
    "schedule": "early_bird",
    "noise_in": "medium",
    "noise_out": "silent",
    "group_code": GROUP_CODE,
    "openid": ""
}

print("=" * 60)
print("开始创建真机测试用户")
print("=" * 60)

for i, user in enumerate(test_users, 1):
    data = {**common_data, **user}

    try:
        response = requests.post(f"{API_URL}/api/submit", json=data, timeout=10)
        result = response.json()

        if result.get("success"):
            if result.get("matched"):
                print(f"{i}. ✅ {user['name']} - 已匹配到 {result['match_info']['name']}")
            else:
                print(f"{i}. ⏳ {user['name']} - 等待匹配中")
        else:
            print(f"{i}. ❌ {user['name']} - 失败: {result.get('message')}")

    except Exception as e:
        print(f"{i}. ❌ {user['name']} - 错误: {str(e)}")

    time.sleep(0.5)  # 避免请求过快

print("=" * 60)
print("测试用户创建完成！")
print("=" * 60)
print("\n真机测试用户列表：")
for i, user in enumerate(test_users, 1):
    print(f"{i}. {user['name']} (微信号: {user['wechat_id']}, 性别: {user['gender']})")
