#!/usr/bin/env python3
"""
批量测试脚本
测试30个用户的匹配情况
"""
import requests
import json
import time

API_URL = "http://49.233.127.228:5000"

# 测试用户数据
test_users = [
    # 组1：正常匹配（口令ASBE0328，男，早睡，普通抗噪，混响出声）
    {"name": "用户1", "wechat_id": "user001", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户2", "wechat_id": "user002", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},

    # 组2：正常匹配（口令ASBE0328，女，晚睡，普通抗噪，寂静出声）
    {"name": "用户3", "wechat_id": "user003", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "silent", "group_code": "ASBE0328"},
    {"name": "用户4", "wechat_id": "user004", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "silent", "group_code": "ASBE0328"},

    # 组3：睡眠锁测试 - 神经衰弱必须配寂静
    {"name": "用户5", "wechat_id": "user005", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "weak", "noise_out": "silent", "group_code": "ASBE0328"},
    {"name": "用户6", "wechat_id": "user006", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "silent", "group_code": "ASBE0328"},

    # 组4：睡眠锁测试 - 低音炮必须配雷打不动
    {"name": "用户7", "wechat_id": "user007", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "strong", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户8", "wechat_id": "user008", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "bass", "group_code": "ASBE0328"},

    # 组5：不匹配 - 神经衰弱遇到混响（应该不匹配）
    {"name": "用户9", "wechat_id": "user009", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "weak", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户10", "wechat_id": "user010", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},

    # 组6：不匹配 - 低音炮遇到普通抗噪（应该不匹配）
    {"name": "用户11", "wechat_id": "user011", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "silent", "group_code": "ASBE0328"},
    {"name": "用户12", "wechat_id": "user012", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "bass", "group_code": "ASBE0328"},

    # 组7：跨群口令测试（不同口令，不应该匹配）
    {"name": "用户13", "wechat_id": "user013", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "TEST0001"},
    {"name": "用户14", "wechat_id": "user014", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "TEST0002"},

    # 组8：性别不同（不应该匹配）
    {"name": "用户15", "wechat_id": "user015", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户16", "wechat_id": "user016", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},

    # 组9：吸烟习惯不同（不应该匹配）
    {"name": "用户17", "wechat_id": "user017", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "是", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户18", "wechat_id": "user018", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},

    # 组10：作息不同（不应该匹配）
    {"name": "用户19", "wechat_id": "user019", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户20", "wechat_id": "user020", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},

    # 组11：日期不同（不应该匹配）
    {"name": "用户21", "wechat_id": "user021", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户22", "wechat_id": "user022", "gender": "男", "check_in": "2026-03-29", "check_out": "2026-03-31", "smoking": "否", "schedule": "late", "noise_in": "normal", "noise_out": "mix", "group_code": "ASBE0328"},

    # 组12-15：额外的匹配对（填充到30人）
    {"name": "用户23", "wechat_id": "user023", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "strong", "noise_out": "silent", "group_code": "ASBE0328"},
    {"name": "用户24", "wechat_id": "user024", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "strong", "noise_out": "silent", "group_code": "ASBE0328"},

    {"name": "用户25", "wechat_id": "user025", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "weak", "noise_out": "silent", "group_code": "ASBE0328"},
    {"name": "用户26", "wechat_id": "user026", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "silent", "group_code": "ASBE0328"},

    {"name": "用户27", "wechat_id": "user027", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "strong", "noise_out": "mix", "group_code": "ASBE0328"},
    {"name": "用户28", "wechat_id": "user028", "gender": "男", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "late", "noise_in": "strong", "noise_out": "mix", "group_code": "ASBE0328"},

    {"name": "用户29", "wechat_id": "user029", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "silent", "group_code": "ASBE0328"},
    {"name": "用户30", "wechat_id": "user030", "gender": "女", "check_in": "2026-03-28", "check_out": "2026-03-30", "smoking": "否", "schedule": "early", "noise_in": "normal", "noise_out": "silent", "group_code": "ASBE0328"},
]

def submit_user(user):
    """提交用户"""
    try:
        response = requests.post(
            f"{API_URL}/api/submit",
            json=user,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 80)
    print("开始批量测试 - 30个用户")
    print("=" * 80)

    matched_count = 0
    waiting_count = 0
    results = []

    for i, user in enumerate(test_users, 1):
        print(f"\n[{i}/30] 提交用户: {user['name']} ({user['wechat_id']})")
        print(f"  - 性别: {user['gender']}, 作息: {user['schedule']}, 吸烟: {user['smoking']}")
        print(f"  - 抗噪: {user['noise_in']}, 出声: {user['noise_out']}")
        print(f"  - 群口令: {user['group_code']}, 日期: {user['check_in']} ~ {user['check_out']}")

        result = submit_user(user)

        if result.get("success"):
            if result.get("matched"):
                matched_count += 1
                match_info = result.get("match_info", {})
                print(f"  ✅ 匹配成功！配对: {match_info.get('name')} ({match_info.get('wechat_id')})")
                results.append({
                    "user": user['name'],
                    "status": "matched",
                    "partner": match_info.get('name')
                })
            else:
                waiting_count += 1
                print(f"  ⏳ 已入池等待")
                results.append({
                    "user": user['name'],
                    "status": "waiting"
                })
        else:
            print(f"  ❌ 提交失败: {result.get('message', result.get('error'))}")
            results.append({
                "user": user['name'],
                "status": "error",
                "error": result.get('message', result.get('error'))
            })

        time.sleep(0.2)  # 避免请求过快

    # 统计结果
    print("\n" + "=" * 80)
    print("测试完成 - 统计结果")
    print("=" * 80)
    print(f"总提交人数: 30")
    print(f"匹配成功: {matched_count} 人 ({matched_count * 2} 人配对)")
    print(f"等待匹配: {waiting_count} 人")
    print(f"提交失败: {30 - matched_count - waiting_count} 人")

    # 获取统计数据
    try:
        stats_response = requests.get(f"{API_URL}/api/stats?group_code=ASBE0328")
        stats = stats_response.json().get("stats", {})
        print(f"\n服务器统计:")
        print(f"  - 总匹配成功数: {stats.get('total_matches', 0)}")
        print(f"  - ASBE0328口令下等待人数: {stats.get('active_count', 0)}")
    except Exception as e:
        print(f"\n获取统计数据失败: {e}")

    # 详细匹配结果
    print("\n" + "=" * 80)
    print("详细匹配结果")
    print("=" * 80)
    for r in results:
        if r['status'] == 'matched':
            print(f"✅ {r['user']} <-> {r['partner']}")
        elif r['status'] == 'waiting':
            print(f"⏳ {r['user']} (等待中)")
        else:
            print(f"❌ {r['user']} (错误: {r.get('error')})")

if __name__ == "__main__":
    main()
