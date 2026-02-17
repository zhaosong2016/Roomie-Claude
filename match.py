"""
匹配逻辑模块
负责用户之间的匹配算法
"""
from typing import Dict, Optional, List

def check_compatibility(user_a: Dict, user_b: Dict) -> bool:
    """检查两个用户是否匹配

    基础锁（必须完全相同）：
    - group_code: 群口令
    - gender: 性别
    - check_in: 入住日期
    - check_out: 退房日期
    - smoking: 吸烟习惯
    - schedule: 作息倾向

    睡眠锁（兼容性检查）：
    - 如果有人神经衰弱(weak)，室友必须寂静(silent)
    - 如果有人低音炮(bass)，室友必须雷打不动(strong)
    """
    # 基础锁：必须完全相同
    basic_fields = ['group_code', 'gender', 'check_in', 'check_out', 'smoking', 'schedule']
    for field in basic_fields:
        if user_a.get(field) != user_b.get(field):
            return False

    # 睡眠锁：兼容性检查
    na = user_a.get('noise_in')  # A的抗噪等级
    nb = user_b.get('noise_in')  # B的抗噪等级
    va = user_a.get('noise_out')  # A的出声分贝
    vb = user_b.get('noise_out')  # B的出声分贝

    # 如果有人神经衰弱，室友必须寂静
    if (na == 'weak' and vb != 'silent') or (nb == 'weak' and va != 'silent'):
        return False

    # 如果有人低音炮，室友必须雷打不动
    if (va == 'bass' and nb != 'strong') or (vb == 'bass' and na != 'strong'):
        return False

    return True

def find_match(new_user: Dict, users: List[Dict]) -> Optional[Dict]:
    """在用户池中寻找匹配

    参数：
    - new_user: 新提交的用户
    - users: 用户池（只包含active状态的用户）

    返回：
    - 匹配的用户，如果没找到返回None
    """
    for user in users:
        if user['status'] == 'active' and check_compatibility(new_user, user):
            return user
    return None
