import streamlit as st
import json
import os
import time
from datetime import datetime

DATA_FILE = "room_data.json"

def load_data():
    """加载数据文件"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if not content:
                    return {"users": []}
                return json.loads(content)
        except Exception:
            return {"users": []}
    return {"users": []}

def save_data(data):
    """保存数据到文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.flush()
        os.fsync(f.fileno())

def check_compatibility(user_a, user_b):
    """检查两个用户是否匹配"""
    # 基础锁：必须完全相同
    basic_fields = ['group_code', 'gender', 'check_in', 'check_out', 'smoking', 'schedule']
    for field in basic_fields:
        if user_a.get(field) != user_b.get(field):
            return False

    # 睡眠锁：兼容性检查
    na = user_a.get('noise_in')
    nb = user_b.get('noise_in')
    va = user_a.get('noise_out')
    vb = user_b.get('noise_out')

    # 如果有人神经衰弱，室友必须寂静
    if (na == 'weak' and vb != 'silent') or (nb == 'weak' and va != 'silent'):
        return False

    # 如果有人低音炮，室友必须雷打不动
    if (va == 'bass' and nb != 'strong') or (vb == 'bass' and na != 'strong'):
        return False

    return True

def find_match(new_user, users):
    """在用户池中寻找匹配"""
    for user in users:
        if user['status'] == 'active' and check_compatibility(new_user, user):
            return user
    return None

# 页面配置
st.set_page_config(page_title="Space One拼房实验室", page_icon="🚀")

# 自定义CSS - VS Code蓝色主题
st.markdown("""
<style>
    /* 按钮样式 - 使用更强的选择器 */
    div.stButton > button:first-child,
    button[kind="primary"],
    button[kind="secondary"] {
        background-color: #007ACC !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }

    div.stButton > button:first-child:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #005A9E !important;
        border: none !important;
    }

    /* 单选框样式 - 覆盖Streamlit默认 */
    input[type="radio"] {
        accent-color: #007ACC !important;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        width: 16px;
        height: 16px;
        border: 2px solid #ccc;
        border-radius: 50%;
        outline: none;
        cursor: pointer;
    }

    input[type="radio"]:checked {
        border-color: #007ACC !important;
        background-color: #007ACC !important;
        box-shadow: inset 0 0 0 3px white;
    }

    /* 复选框样式 */
    input[type="checkbox"] {
        accent-color: #007ACC !important;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        width: 16px;
        height: 16px;
        border: 2px solid #ccc;
        border-radius: 3px;
        outline: none;
        cursor: pointer;
    }

    input[type="checkbox"]:checked {
        border-color: #007ACC !important;
        background-color: #007ACC !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='white' d='M13.5 2L6 9.5 2.5 6 1 7.5l5 5 9-9z'/%3E%3C/svg%3E");
        background-size: 12px;
        background-position: center;
        background-repeat: no-repeat;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown("### 🚀 Space One拼房实验室（网页版）")
st.markdown("---")

# 加载数据
data = load_data()
users = data["users"]

# 群口令输入
group_code = st.text_input("🔑 输入群专属口令", type="password")

if not group_code:
    st.warning("请输入群口令以开启拼房功能")
    st.stop()

# 主表单
with st.form("roomie_form"):
    st.markdown("#### 填写信息进入拼房池")

    # 基本信息
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("你的名字/昵称", placeholder="怎么称呼你？")
    with col2:
        wechat_id = st.text_input("你的微信号", placeholder="用于匹配成功后联系")

    # 性别
    gender = st.radio("你的性别", ["女", "男"], horizontal=True, index=None)

    # 日期
    st.markdown("**打算住几晚**")
    col3, col4 = st.columns(2)
    with col3:
        check_in = st.date_input("入住日期", value=None)
    with col4:
        check_out = st.date_input("退房日期", value=None)

    # 吸烟
    smoking = st.radio("是否吸烟", ["否", "是"], horizontal=True, index=None)

    st.markdown("---")
    st.markdown("#### 睡眠习惯摸底")

    # 作息倾向
    st.markdown("**1. 你的'作息'倾向**")
    schedule = st.radio(
        "作息",
        ["early", "late"],
        format_func=lambda x: "[早睡鸟] 习惯早睡早起，生物钟稳定" if x == "early" else "[夜猫子] 越晚越精神，深夜才是自由时间",
        index=None,
        label_visibility="collapsed"
    )

    # 抗噪等级
    st.markdown("**2. 你的'抗噪'等级**")
    noise_in = st.radio(
        "抗噪",
        ["weak", "normal", "strong"],
        format_func=lambda x: {
            "weak": "[神经衰弱] 有动静就醒",
            "normal": "[普通玩家] 正常翻身没问题",
            "strong": "[雷打不动] 倒头就睡，浑然不觉"
        }[x],
        index=None,
        label_visibility="collapsed"
    )

    # 出声分贝
    st.markdown("**3. 你的'出声'分贝**")
    noise_out = st.radio(
        "出声",
        ["silent", "mix", "bass"],
        format_func=lambda x: {
            "silent": "[寂静模式] 非常安静，基本无声",
            "mix": "[混响模式] 偶尔翻身或磨牙",
            "bass": "[低音炮模式] 呼噜明显哈哈"
        }[x],
        index=None,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # 同意条款
    agree = st.checkbox("同意与我需求匹配的人通过微信联系我")

    # 提交按钮
    submit = st.form_submit_button("确认进入拼房池", use_container_width=True)

# 处理提交
if submit:
    # 验证必填项
    if not name or not wechat_id:
        st.error("❌ 名字和微信号都是必填项")
    elif gender is None:
        st.error("❌ 请选择性别")
    elif check_in is None or check_out is None:
        st.error("❌ 请选择入住和退房日期")
    elif check_in >= check_out:
        st.error("❌ 退房日期必须晚于入住日期")
    elif smoking is None:
        st.error("❌ 请选择是否吸烟")
    elif schedule is None:
        st.error("❌ 请选择作息倾向")
    elif noise_in is None:
        st.error("❌ 请选择抗噪等级")
    elif noise_out is None:
        st.error("❌ 请选择出声分贝")
    elif not agree:
        st.error("❌ 请勾选同意条款")
    else:
        # 创建新用户
        new_user = {
            "name": name,
            "wechat_id": wechat_id,
            "gender": gender,
            "check_in": check_in.strftime("%Y-%m-%d"),
            "check_out": check_out.strftime("%Y-%m-%d"),
            "smoking": smoking,
            "schedule": schedule,
            "noise_in": noise_in,
            "noise_out": noise_out,
            "group_code": group_code,
            "status": "active",
            "created_at": time.time()
        }

        # 去重：移除同一微信号在同一群的活跃记录
        data["users"] = [
            u for u in users
            if not (u["wechat_id"] == wechat_id and u["group_code"] == group_code and u["status"] == "active")
        ]
        users = data["users"]

        # 寻找匹配
        matched_user = find_match(new_user, users)

        if matched_user:
            # 找到匹配
            st.balloons()
            st.success(f"🎊 你与 **{matched_user['name']}** 需求匹配！")
            st.info(f"👉 对方微信号: **{matched_user['wechat_id']}**")

            # 更新状态
            matched_user["status"] = "matched"
            new_user["status"] = "matched"
            users.append(new_user)
            save_data(data)
        else:
            # 未找到匹配，入池等待
            users.append(new_user)
            save_data(data)
            st.info("⏳ 已入池。若有需求匹配的群友，会联系你。若 24 小时无人联系，请微调习惯再次尝试匹配。")

# 显示当前等待人数
st.markdown("---")
active_count = len([u for u in users if u["group_code"] == group_code and u["status"] == "active"])
st.write(f"📊 当前口令下共有 **{active_count}** 位群友正在寻房")
