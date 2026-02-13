# retainer_tracker_session_state.py
# 使用 streamlit + session_state（适合快速测试，不依赖文件/数据库）

import streamlit as st
import datetime

# ─── 配置部分 ────────────────────────────────────────────────
EVERY_OTHER_DAY = True           # True = 隔天佩戴    False = 按星期固定几天
WEEKLY_DAYS = [0, 2, 4]          # 星期一=0, 三=2, 五=4 ... 只在 EVERY_OTHER_DAY=False 时有效
FIRST_WEAR_DATE = "2025-02-10"   # ←←← 务必改成你**第一次真正佩戴**的日期！格式 YYYY-MM-DD
# ──────────────────────────────────────────────────────────────

# 初始化 session_state
if 'records' not in st.session_state:
    st.session_state.records = set()

if 'first_load' not in st.session_state:
    st.session_state.first_load = True

# ─── 辅助函数 ────────────────────────────────────────────────

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def is_should_wear_date(dt: datetime.date) -> bool:
    start = parse_date(FIRST_WEAR_DATE)
    if not start:
        return False
    days_diff = (dt - start).days
    if EVERY_OTHER_DAY:
        return days_diff % 2 == 0
    else:
        return dt.weekday() in WEEKLY_DAYS

def get_next_wear_date(today: datetime.date) -> datetime.date:
    worn_set = st.session_state.records
    candidate = today
    while True:
        candidate += datetime.timedelta(days=1)
        if candidate.strftime("%Y-%m-%d") in worn_set:
            continue
        if is_should_wear_date(candidate):
            return candidate

# ─── 主界面 ──────────────────────────────────────────────────

st.title("保持器佩戴记录 & 提醒")
st.caption("数据保存在浏览器本次会话中（关掉网页会丢失）")

today = datetime.date.today()
today_str = today.strftime("%Y-%m-%d")

st.subheader(f"今天：{today_str}")

records = st.session_state.records
worn_count = len(records)

st.info(f"已记录佩戴天数：**{worn_count}** 天")

# 今日操作区域
if today_str in records:
    st.success("今天已经记录佩戴 ✓")
else:
    col1, col2 = st.columns([3, 3])

    if col1.button("今天戴了", use_container_width=True, type="primary"):
        records.add(today_str)
        st.success("已记录！今天佩戴 ✓")
        st.rerun()

    if col2.button("今天没戴", use_container_width=True):
        st.info("好的，今天跳过～")
        # 可以选择在这里加个占位记录，例如加个前缀标记没戴，但这里简单不记录
        st.rerun()

# 下次提醒
st.divider()

next_date = get_next_wear_date(today)
days_later = (next_date - today).days

st.subheader("下次应该佩戴的日期")

if days_later == 0:
    st.error("今天！（但你好像还没点“今天戴了”？）")
elif days_later == 1:
    st.warning("**明天**就要戴啦！记得～")
elif days_later <= 3:
    st.warning(f"再过 **{days_later}** 天就要戴了")
else:
    st.info(f"下次佩戴日期：**{next_date.strftime('%Y-%m-%d')}**　（再过 {days_later} 天）")

st.caption(f"佩戴节奏：{'隔天佩戴' if EVERY_OTHER_DAY else '每周固定几天'}")

# 显示最近记录（折叠）
with st.expander(f"已记录日期（共 {worn_count} 天）", expanded=(worn_count <= 5)):
    if records:
        sorted_dates = sorted(records, reverse=True)
        for d in sorted_dates[:30]:  # 最多显示最近30条
            st.write(d)
    else:
        st.write("还没有任何记录～")

st.caption("小提示：第一次使用请正确设置「FIRST_WEAR_DATE」，否则提醒日期会不准。")