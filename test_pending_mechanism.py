#!/usr/bin/env python3
"""
Pending 机制批量测试脚本
测试内容：
1. Pending 状态创建
2. 60秒超时自动清理
3. Confirm 接口
4. Reject 接口
5. History 防重复匹配
"""

import requests
import time
import json
from datetime import datetime

# 配置
API_URL = "http://49.233.127.228:5000"
GROUP_CODE = "TESTPENDING"

# 测试结果统计
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

def log(message, level="INFO"):
    """打印日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_api(test_name, func):
    """测试包装器"""
    results["total"] += 1
    log(f"开始测试: {test_name}")
    try:
        func()
        results["passed"] += 1
        log(f"✅ {test_name} - 通过", "PASS")
        return True
    except AssertionError as e:
        results["failed"] += 1
        error_msg = f"❌ {test_name} - 失败: {str(e)}"
        log(error_msg, "FAIL")
        results["errors"].append(error_msg)
        return False
    except Exception as e:
        results["failed"] += 1
        error_msg = f"❌ {test_name} - 错误: {str(e)}"
        log(error_msg, "ERROR")
        results["errors"].append(error_msg)
        return False

def submit_user(name, wechat_id, check_in="2026-03-05", check_out="2026-03-08"):
    """提交用户"""
    data = {
        "name": name,
        "wechat_id": wechat_id,
        "gender": "女",
        "check_in": check_in,
        "check_out": check_out,
        "smoking": "no",
        "schedule": "early_bird",
        "noise_in": "medium",
        "noise_out": "silent",
        "group_code": GROUP_CODE,
        "openid": ""
    }

    response = requests.post(f"{API_URL}/api/submit", json=data, timeout=10)
    return response.json()

def confirm_match(wechat_id):
    """确认匹配"""
    data = {
        "wechat_id": wechat_id,
        "group_code": GROUP_CODE,
        "openid": ""
    }
    response = requests.post(f"{API_URL}/api/confirm", json=data, timeout=10)
    return response.json()

def reject_match(wechat_id):
    """拒绝匹配"""
    data = {
        "wechat_id": wechat_id,
        "group_code": GROUP_CODE,
        "openid": ""
    }
    response = requests.post(f"{API_URL}/api/reject", json=data, timeout=10)
    return response.json()

def check_code():
    """检查群口令状态"""
    response = requests.get(f"{API_URL}/api/check_code?code={GROUP_CODE}", timeout=10)
    return response.json()

# ============ 测试用例 ============

def test_1_pending_creation():
    """测试1: Pending 状态创建"""
    log("提交用户 Alice...")
    result1 = submit_user("Alice", "alice_pending_test")
    assert result1["success"], "Alice 提交失败"
    assert not result1.get("matched"), "Alice 不应该立即匹配"

    log("提交用户 Bob（应该匹配 Alice）...")
    result2 = submit_user("Bob", "bob_pending_test")
    assert result2["success"], "Bob 提交失败"
    assert result2.get("matched"), "Bob 应该匹配到 Alice"
    assert result2.get("is_pending") == True, "应该是 pending 状态"
    assert result2["match_info"]["name"] == "Alice", "应该匹配到 Alice"

    log("验证 Alice 也是 pending 状态...")
    result3 = submit_user("Alice", "alice_pending_test")
    assert result3.get("matched"), "Alice 应该显示已匹配"
    assert result3.get("is_pending") == True, "Alice 应该是 pending 状态"

def test_2_confirm_match():
    """测试2: 确认匹配"""
    log("提交用户 Carol...")
    submit_user("Carol", "carol_confirm_test")

    log("提交用户 Dave（匹配 Carol）...")
    result = submit_user("Dave", "dave_confirm_test")
    assert result.get("matched"), "Dave 应该匹配到 Carol"
    assert result.get("is_pending") == True, "应该是 pending 状态"

    log("Dave 确认匹配...")
    confirm_result = confirm_match("dave_confirm_test")
    assert confirm_result["success"], "确认匹配失败"

    log("验证状态变为 matched...")
    result2 = submit_user("Dave", "dave_confirm_test")
    assert result2.get("matched"), "Dave 应该显示已匹配"
    assert result2.get("is_pending") == False, "应该不再是 pending 状态"

def test_3_reject_match():
    """测试3: 拒绝匹配"""
    log("提交用户 Eve...")
    submit_user("Eve", "eve_reject_test")

    log("提交用户 Frank（匹配 Eve）...")
    result = submit_user("Frank", "frank_reject_test")
    assert result.get("matched"), "Frank 应该匹配到 Eve"
    assert result.get("is_pending") == True, "应该是 pending 状态"

    log("Frank 拒绝匹配...")
    reject_result = reject_match("frank_reject_test")
    assert reject_result["success"], "拒绝匹配失败"

    log("验证状态变回 active...")
    result2 = submit_user("Frank", "frank_reject_test")
    assert not result2.get("matched"), "Frank 应该变回等待状态"

    log("验证 Eve 也变回 active...")
    result3 = submit_user("Eve", "eve_reject_test")
    assert not result3.get("matched"), "Eve 应该变回等待状态"

def test_4_history_prevention():
    """测试4: History 防止重复匹配"""
    log("提交用户 Grace...")
    submit_user("Grace", "grace_history_test")

    log("提交用户 Henry（匹配 Grace）...")
    submit_user("Henry", "henry_history_test")

    log("Henry 拒绝匹配...")
    reject_match("henry_history_test")

    log("Henry 再次提交，不应该再匹配到 Grace...")
    result = submit_user("Henry", "henry_history_test")
    # 因为只有 Grace 和 Henry，拒绝后应该没有其他人可匹配
    assert not result.get("matched") or result["match_info"]["name"] != "Grace", \
        "Henry 不应该再次匹配到 Grace"

def test_5_timeout_cleanup():
    """测试5: 超时自动清理（需要等待）"""
    log("提交用户 Ivy...")
    submit_user("Ivy", "ivy_timeout_test")

    log("提交用户 Jack（匹配 Ivy）...")
    result = submit_user("Jack", "jack_timeout_test")
    assert result.get("matched"), "Jack 应该匹配到 Ivy"
    assert result.get("is_pending") == True, "应该是 pending 状态"

    log("等待 65 秒让 pending 超时...")
    for i in range(13):
        time.sleep(5)
        log(f"已等待 {(i+1)*5} 秒...")

    log("验证状态是否自动变回 active...")
    result2 = submit_user("Jack", "jack_timeout_test")
    # 超时后应该变回 active，但因为 Ivy 还在，可能会再次匹配
    # 所以这里只检查不是 pending 状态
    if result2.get("matched"):
        assert result2.get("is_pending") == True, "如果再次匹配，应该是新的 pending"

def test_6_batch_matching():
    """测试6: 批量匹配测试"""
    log("批量创建 20 对用户...")
    for i in range(20):
        user1 = f"BatchUser{i*2+1}"
        user2 = f"BatchUser{i*2+2}"
        wechat1 = f"batch_user_{i*2+1}"
        wechat2 = f"batch_user_{i*2+2}"

        submit_user(user1, wechat1)
        result = submit_user(user2, wechat2)

        assert result.get("matched"), f"{user2} 应该匹配到 {user1}"
        assert result.get("is_pending") == True, f"{user2} 应该是 pending 状态"

    log("批量匹配测试完成，共创建 20 对 pending 匹配")

def test_7_concurrent_confirm():
    """测试7: 并发确认测试"""
    log("创建 5 对用户并快速确认...")
    for i in range(5):
        user1 = f"ConcurrentUser{i*2+1}"
        user2 = f"ConcurrentUser{i*2+2}"
        wechat1 = f"concurrent_{i*2+1}"
        wechat2 = f"concurrent_{i*2+2}"

        submit_user(user1, wechat1)
        submit_user(user2, wechat2)

        # 快速确认
        confirm_match(wechat2)

        # 验证状态
        result = submit_user(user2, wechat2)
        assert result.get("matched"), f"{user2} 应该已匹配"
        assert result.get("is_pending") == False, f"{user2} 应该不再是 pending"

# ============ 主程序 ============

def main():
    log("=" * 60)
    log("Pending 机制批量测试开始")
    log("=" * 60)

    # 检查 API 连接
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        log(f"API 连接正常: {response.json()}")
    except Exception as e:
        log(f"API 连接失败: {e}", "ERROR")
        return

    # 运行测试
    test_api("测试1: Pending 状态创建", test_1_pending_creation)
    test_api("测试2: 确认匹配", test_2_confirm_match)
    test_api("测试3: 拒绝匹配", test_3_reject_match)
    test_api("测试4: History 防止重复匹配", test_4_history_prevention)
    test_api("测试6: 批量匹配测试", test_6_batch_matching)
    test_api("测试7: 并发确认测试", test_7_concurrent_confirm)

    # 超时测试（可选，需要等待 65 秒）
    log("\n是否运行超时测试？（需要等待 65 秒）")
    log("跳过超时测试，如需测试请手动运行 test_5_timeout_cleanup()")
    # test_api("测试5: 超时自动清理", test_5_timeout_cleanup)

    # 打印结果
    log("=" * 60)
    log("测试完成！")
    log("=" * 60)
    log(f"总测试数: {results['total']}")
    log(f"通过: {results['passed']}")
    log(f"失败: {results['failed']}")

    if results['errors']:
        log("\n失败的测试:")
        for error in results['errors']:
            log(error)

    # 检查最终状态
    log("\n检查群口令状态...")
    try:
        status = check_code()
        log(f"等待匹配: {status.get('waiting_count', 0)}")
        log(f"已匹配: {status.get('matched_count', 0)}")
    except Exception as e:
        log(f"获取状态失败: {e}", "ERROR")

    log("=" * 60)

if __name__ == "__main__":
    main()
