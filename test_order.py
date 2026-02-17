#!/usr/bin/env python3
"""
顺序测试脚本
测试不同提交顺序对匹配结果的影响
"""
import requests
import json
import random
import time

API_URL = "http://49.233.127.228:5000"

# 生成50个用户，只变化作息和睡眠习惯
def generate_users():
    users = []
    user_id = 1

    # 组合：2种作息 × 3种抗噪 × 3种出声 = 18种组合
    # 每种组合生成2-3个用户，共50人
    combinations = []
    for schedule in ["early", "late"]:
        for noise_in in ["weak", "normal", "strong"]:
            for noise_out in ["silent", "mix", "bass"]:
                combinations.append((schedule, noise_in, noise_out))

    # 每种组合生成2-3个用户
    for combo in combinations:
        count = 3 if user_id <= 36 else 2  # 前12种组合各3人，后6种各2人
        for _ in range(count):
            schedule, noise_in, noise_out = combo
            users.append({
                "name": f"用户{user_id}",
                "wechat_id": f"test{user_id:03d}",
                "gender": "男",
                "check_in": "2026-04-01",
                "check_out": "2026-04-03",
                "smoking": "否",
                "schedule": schedule,
                "noise_in": noise_in,
                "noise_out": noise_out,
                "group_code": "TEST2024"
            })
            user_id += 1
            if user_id > 50:
                break
        if user_id > 50:
            break

    return users[:50]

def clear_data():
    """清空测试数据"""
    print("清空之前的测试数据...")
    # 这里需要手动清空或者重启API
    # 暂时跳过，假设每次测试前手动清空

def submit_users(users, test_name):
    """提交用户并记录结果"""
    print(f"\n{'='*80}")
    print(f"{test_name}")
    print(f"{'='*80}\n")

    matched_count = 0
    waiting_count = 0
    matches = []

    for i, user in enumerate(users, 1):
        try:
            response = requests.post(
                f"{API_URL}/api/submit",
                json=user,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("matched"):
                    matched_count += 1
                    partner = result.get("match_info", {})
                    matches.append({
                        "user": user["name"],
                        "partner": partner.get("name"),
                        "schedule": user["schedule"],
                        "noise_in": user["noise_in"],
                        "noise_out": user["noise_out"]
                    })
                    print(f"✅ {user['name']} <-> {partner.get('name')} "
                          f"[{user['schedule']}, {user['noise_in']}, {user['noise_out']}]")
                else:
                    waiting_count += 1
                    print(f"⏳ {user['name']} (等待中) "
                          f"[{user['schedule']}, {user['noise_in']}, {user['noise_out']}]")
            else:
                print(f"❌ {user['name']} 提交失败: {response.status_code}")

            time.sleep(0.1)  # 避免请求过快

        except Exception as e:
            print(f"❌ {user['name']} 提交错误: {e}")

    print(f"\n{'='*80}")
    print(f"统计结果")
    print(f"{'='*80}")
    print(f"总提交人数: 50")
    print(f"匹配成功: {matched_count} 人")
    print(f"等待匹配: {waiting_count} 人")
    print(f"匹配成功率: {matched_count/50*100:.1f}%")

    return matches

def main():
    print("="*80)
    print("顺序测试 - 测试不同提交顺序对匹配结果的影响")
    print("="*80)

    # 生成用户
    users = generate_users()

    print(f"\n生成了 {len(users)} 个测试用户")
    print("所有用户条件：男、同一口令(TEST2024)、同一日期(4月1-3日)、不吸烟")
    print("变化维度：作息(early/late) + 抗噪(weak/normal/strong) + 出声(silent/mix/bass)")

    input("\n按回车开始第一轮测试（原始顺序）...")

    # 第一轮：原始顺序
    matches1 = submit_users(users, "第一轮测试 - 原始顺序")

    input("\n\n按回车开始第二轮测试（打乱顺序）...")
    input("⚠️  请先手动清空数据库，然后按回车继续...")

    # 第二轮：打乱顺序
    users_shuffled = users.copy()
    random.shuffle(users_shuffled)
    matches2 = submit_users(users_shuffled, "第二轮测试 - 打乱顺序")

    # 对比结果
    print(f"\n{'='*80}")
    print("对比分析")
    print(f"{'='*80}")
    print(f"第一轮匹配数: {len(matches1)}")
    print(f"第二轮匹配数: {len(matches2)}")
    print(f"\n结论：")
    if len(matches1) == len(matches2):
        print("✅ 两轮匹配数量相同，算法稳定")
    else:
        print(f"⚠️  匹配数量不同，差异: {abs(len(matches1) - len(matches2))} 对")

    print("\n💡 注意：由于是'先到先得'算法，不同顺序下：")
    print("   - 匹配数量应该相同（或接近）")
    print("   - 但具体谁和谁配对可能不同")
    print("   - 这是正常现象，不影响公平性")

if __name__ == "__main__":
    main()
