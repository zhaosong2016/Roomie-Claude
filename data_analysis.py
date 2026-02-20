#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Space One 拼房实验室 - 数据分析脚本

用途：分析 room_data.json，生成统计报告
使用：python3 data_analysis.py
"""

import json
from datetime import datetime
from collections import defaultdict

def load_data():
    """加载数据文件"""
    try:
        with open('room_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 错误：找不到 room_data.json 文件")
        print("请确保在 Roomie-Claude 目录下运行此脚本")
        return None
    except json.JSONDecodeError:
        print("❌ 错误：room_data.json 格式错误")
        return None

def analyze_basic_stats(data):
    """基础统计"""
    users = data.get('users', [])
    total_users = len(users)
    matched_users = sum(1 for u in users if u.get('status') == 'matched')
    active_users = sum(1 for u in users if u.get('status') == 'active')

    print("\n" + "="*60)
    print("📊 基础统计")
    print("="*60)
    print(f"总用户数：{total_users}")
    print(f"已匹配：{matched_users} 人 ({matched_users/total_users*100:.1f}%)" if total_users > 0 else "已匹配：0 人")
    print(f"等待中：{active_users} 人 ({active_users/total_users*100:.1f}%)" if total_users > 0 else "等待中：0 人")
    print(f"匹配成功率：{matched_users/total_users*100:.1f}%" if total_users > 0 else "匹配成功率：0%")

    # 匹配对数
    pairs = matched_users // 2
    print(f"成功配对：{pairs} 对")

def analyze_by_activity(data):
    """按活动分析"""
    users = data.get('users', [])
    activity_stats = defaultdict(lambda: {'total': 0, 'matched': 0, 'active': 0})

    for user in users:
        code = user.get('group_code', 'UNKNOWN')
        activity_stats[code]['total'] += 1
        if user.get('status') == 'matched':
            activity_stats[code]['matched'] += 1
        else:
            activity_stats[code]['active'] += 1

    print("\n" + "="*60)
    print("🎯 各活动统计")
    print("="*60)

    for code, stats in sorted(activity_stats.items(), key=lambda x: x[1]['total'], reverse=True):
        total = stats['total']
        matched = stats['matched']
        active = stats['active']
        match_rate = matched/total*100 if total > 0 else 0

        print(f"\n活动口令：{code}")
        print(f"  总人数：{total}")
        print(f"  已匹配：{matched} ({match_rate:.1f}%)")
        print(f"  等待中：{active}")

def analyze_by_gender(data):
    """按性别分析"""
    users = data.get('users', [])
    gender_stats = defaultdict(lambda: {'total': 0, 'matched': 0, 'active': 0})

    for user in users:
        gender = user.get('gender', 'unknown')
        gender_label = '女' if gender == 'female' else '男' if gender == 'male' else '未知'
        gender_stats[gender_label]['total'] += 1
        if user.get('status') == 'matched':
            gender_stats[gender_label]['matched'] += 1
        else:
            gender_stats[gender_label]['active'] += 1

    print("\n" + "="*60)
    print("👥 性别分布")
    print("="*60)

    for gender, stats in gender_stats.items():
        total = stats['total']
        matched = stats['matched']
        active = stats['active']

        print(f"\n{gender}：{total} 人")
        print(f"  已匹配：{matched}")
        print(f"  等待中：{active}")

def analyze_habits(data):
    """生活习惯分析"""
    users = data.get('users', [])

    # 吸烟习惯
    smoking_stats = defaultdict(int)
    for user in users:
        smoking = user.get('smoking', 'unknown')
        label = '吸烟' if smoking == 'yes' else '不吸烟' if smoking == 'no' else '未知'
        smoking_stats[label] += 1

    # 作息习惯
    schedule_stats = defaultdict(int)
    for user in users:
        schedule = user.get('schedule', 'unknown')
        label = '早睡鸟' if schedule == 'early_bird' else '夜猫子' if schedule == 'night_owl' else '未知'
        schedule_stats[label] += 1

    # 抗噪等级
    noise_in_stats = defaultdict(int)
    for user in users:
        noise_in = user.get('noise_in', 'unknown')
        label = '神经衰弱' if noise_in == 'weak' else '普通玩家' if noise_in == 'medium' else '雷打不动' if noise_in == 'strong' else '未知'
        noise_in_stats[label] += 1

    # 出声分贝
    noise_out_stats = defaultdict(int)
    for user in users:
        noise_out = user.get('noise_out', 'unknown')
        label = '寂静模式' if noise_out == 'silent' else '混响模式' if noise_out == 'loud' else '低音炮模式' if noise_out == 'bass' else '未知'
        noise_out_stats[label] += 1

    print("\n" + "="*60)
    print("🛏️ 生活习惯分布")
    print("="*60)

    print("\n吸烟习惯：")
    for label, count in smoking_stats.items():
        print(f"  {label}：{count} 人")

    print("\n作息习惯：")
    for label, count in schedule_stats.items():
        print(f"  {label}：{count} 人")

    print("\n抗噪等级：")
    for label, count in noise_in_stats.items():
        print(f"  {label}：{count} 人")

    print("\n出声分贝：")
    for label, count in noise_out_stats.items():
        print(f"  {label}：{count} 人")

def analyze_dates(data):
    """入住日期分析"""
    users = data.get('users', [])
    date_stats = defaultdict(int)

    for user in users:
        check_in = user.get('check_in', '')
        if check_in:
            date_stats[check_in] += 1

    print("\n" + "="*60)
    print("📅 热门入住日期 (Top 10)")
    print("="*60)

    sorted_dates = sorted(date_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for date, count in sorted_dates:
        print(f"{date}：{count} 人")

def analyze_submit_count(data):
    """提交次数分析"""
    users = data.get('users', [])
    submit_stats = defaultdict(int)

    for user in users:
        count = user.get('submit_count', 1)
        submit_stats[count] += 1

    print("\n" + "="*60)
    print("🔄 提交次数分布")
    print("="*60)

    for count in sorted(submit_stats.keys()):
        users_count = submit_stats[count]
        print(f"提交 {count} 次：{users_count} 人")

def analyze_history(data):
    """历史记忆分析"""
    users = data.get('users', [])

    users_with_history = sum(1 for u in users if u.get('history', []))
    total_history_records = sum(len(u.get('history', [])) for u in users)

    print("\n" + "="*60)
    print("🔍 历史记忆统计")
    print("="*60)
    print(f"有历史记录的用户：{users_with_history} 人")
    print(f"历史记录总数：{total_history_records} 条")

    if users_with_history > 0:
        avg_history = total_history_records / users_with_history
        print(f"平均每人历史记录：{avg_history:.1f} 条")

def analyze_recent_activity(data):
    """最近活动分析"""
    users = data.get('users', [])

    # 按创建时间排序，取最近10个
    sorted_users = sorted(users, key=lambda x: x.get('created_at', 0), reverse=True)[:10]

    print("\n" + "="*60)
    print("⏰ 最近加入的用户 (Top 10)")
    print("="*60)

    for i, user in enumerate(sorted_users, 1):
        name = user.get('name', '未知')
        timestamp = user.get('created_at', 0)
        status = '已匹配' if user.get('status') == 'matched' else '等待中'

        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = '未知时间'

        print(f"{i}. {name} - {status} - {time_str}")

def generate_report(data):
    """生成完整报告"""
    print("\n" + "🎯 " * 20)
    print("Space One 拼房实验室 - 数据分析报告")
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 " * 20)

    analyze_basic_stats(data)
    analyze_by_activity(data)
    analyze_by_gender(data)
    analyze_habits(data)
    analyze_dates(data)
    analyze_submit_count(data)
    analyze_history(data)
    analyze_recent_activity(data)

    print("\n" + "="*60)
    print("✅ 报告生成完成")
    print("="*60 + "\n")

def main():
    """主函数"""
    data = load_data()
    if data:
        generate_report(data)

if __name__ == '__main__':
    main()
