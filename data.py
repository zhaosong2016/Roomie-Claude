"""
数据管理模块
负责用户数据的读取、保存和管理
"""
import json
import os
import time
from typing import Dict, List, Optional

DATA_FILE = "room_data.json"

def load_data() -> Dict:
    """加载数据文件"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if not content:
                    return {"users": [], "stats": {"total_matches": 0}}
                return json.loads(content)
        except Exception as e:
            print(f"加载数据失败: {e}")
            return {"users": [], "stats": {"total_matches": 0}}
    return {"users": [], "stats": {"total_matches": 0}}

def save_data(data: Dict) -> bool:
    """保存数据到文件"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

def get_user_by_wechat(wechat_id: str, group_code: str) -> Optional[Dict]:
    """根据微信号和群口令查找用户"""
    data = load_data()
    for user in data["users"]:
        if user.get("wechat_id") == wechat_id and user.get("group_code") == group_code:
            return user
    return None

def add_or_update_user(user_data: Dict) -> Dict:
    """添加或更新用户

    如果用户已存在（相同微信号+群口令），则：
    1. 保存旧数据到history
    2. 更新current数据
    3. 增加submit_count

    如果是新用户，直接添加
    """
    data = load_data()
    wechat_id = user_data.get("wechat_id")
    group_code = user_data.get("group_code")

    # 查找是否已存在
    existing_user = None
    for i, user in enumerate(data["users"]):
        if user.get("wechat_id") == wechat_id and user.get("group_code") == group_code:
            existing_user = user
            existing_index = i
            break

    if existing_user:
        # 用户已存在，更新数据
        # 保存旧数据到history
        if "history" not in existing_user:
            existing_user["history"] = []

        # 将当前数据（除了history和submit_count）保存到history
        old_data = {k: v for k, v in existing_user.items() if k not in ["history", "submit_count"]}
        old_data["submitted_at"] = existing_user.get("created_at", time.time())
        existing_user["history"].append(old_data)

        # 更新当前数据
        for key, value in user_data.items():
            existing_user[key] = value

        # 增加提交次数
        existing_user["submit_count"] = existing_user.get("submit_count", 1) + 1
        existing_user["created_at"] = time.time()

        data["users"][existing_index] = existing_user
        result_user = existing_user
    else:
        # 新用户
        user_data["created_at"] = time.time()
        user_data["submit_count"] = 1
        user_data["history"] = []
        data["users"].append(user_data)
        result_user = user_data

    save_data(data)
    return result_user

def update_user_status(wechat_id: str, group_code: str, status: str, pair_id: Optional[str] = None) -> bool:
    """更新用户状态"""
    data = load_data()

    for user in data["users"]:
        if user.get("wechat_id") == wechat_id and user.get("group_code") == group_code:
            user["status"] = status
            if pair_id:
                user["pair_id"] = pair_id
            save_data(data)
            return True

    return False

def get_active_users(group_code: str) -> List[Dict]:
    """获取指定群口令下的活跃用户"""
    data = load_data()
    return [
        user for user in data["users"]
        if user.get("group_code") == group_code and user.get("status") == "active"
    ]

def get_stats(group_code: Optional[str] = None) -> Dict:
    """获取统计数据

    返回：
    - total_matches: 总匹配成功数
    - active_count: 当前群口令下等待匹配的人数（如果提供group_code）
    """
    data = load_data()
    stats = {
        "total_matches": data.get("stats", {}).get("total_matches", 0)
    }

    if group_code:
        active_count = len([
            user for user in data["users"]
            if user.get("group_code") == group_code and user.get("status") == "active"
        ])
        stats["active_count"] = active_count

    return stats

def increment_match_count() -> None:
    """增加匹配成功计数"""
    data = load_data()
    if "stats" not in data:
        data["stats"] = {"total_matches": 0}
    data["stats"]["total_matches"] = data["stats"].get("total_matches", 0) + 1
    save_data(data)
