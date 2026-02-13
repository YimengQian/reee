# retainer_supabase.py
# 永久保存版：Supabase + Streamlit（跨设备同步）
# 佩戴节奏：每 3 天戴一次

import streamlit as st
from supabase import create_client, Client
import datetime

# ─── 配置 ────────────────────────────────────────────────
WEAR_INTERVAL_DAYS = 3             # 每隔几天戴一次（3 = 三天戴一次，2 = 隔天一次，4 = 四天一次……）
FIRST_WEAR_DATE = "2025-02-14"     # ←←← 务必修改成你**第一次真正佩戴**的日期！格式：YYYY-MM-DD
# ──────────────────────────────────────────────────────────

# 初始化 Supabase 客户端（缓存，性能更好）
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# 加载所有已记录的日期
def load_records():
    try:
        response = supabase.table("retainer_records").select("date").execute()
        return {row["date"] for row in response.data}
    except Exception as e:
        st.error(f"数据库连接失败：{e}")
        st.stop()
        return set()

# 添加记录（使用 upsert 防止同一天重复插入）
def add_record(date_str: str):
    try:
        supabase.table("retainer_records").upsert({"date": date_str}).execute()
        st.success("已永久记录！✅")
    except Exception as e:
        st.error(f"保存失败：{e}")

# ─── 辅助函数 ────────────────────────────────────────────────
def parse_date(date_str: str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        st.error(f"第一次佩戴日期格式错误！请使用 YYYY-MM-DD 格式，目前设置为：{FIRST_WEAR_DATE}")
        st.stop()
        return None

def is_should_wear_date(dt: datetime.date) -> bool:
    start = parse_date(FIRST_WEAR_DATE)
    if not start:
        return False
    
    days_diff = (dt - start).days
    
    # 早于第一次佩戴日 → 不应该佩戴
    if days_diff < 0:
        return False
    
    # 核心判断：是否落在 0, 3, 6, 9, 12…… 这些天数上
    return days_diff % WEAR_INTERVAL_DAYS == 0

def get_next_wear_date(today: datetime.date, worn_set: set) -> datetime.date:
    candidate = today
    # 最多向前找 365 天，避免死循环（理论上不会发生）
    for _ in range(365):
        candidate += datetime.timedelta(days=1)
        candidate_str = candidate.strftime("%Y-%m-%d")
        if candidate_str in worn_set:
            continue
        if is_should_wear_date(candidate):
            return candidate
    # 如果异常找不到，返回一个很远的未来日期（几乎不会发生）
    return today + datetime.timedelta(days=365)

# ─── 主界面 ──────────────────────────────────────────────────
st.title("保持器佩戴提醒 · 永久版")
st.caption("数据永久保存在 Supabase 云端，任何设备均可同步查看")

today = datetime.date.today()
today_str = today.strftime("%Y-%m-%d")

st.subheader(f"今天：{today_str}")

records = load_records()
st.info(f"已记录佩戴天数：**{len(records)}** 天")

# 今日操作区域
if today_str in records:
    st.success("今天已经记录佩戴 ✓")
else:
    col1, col2 = st.columns(2)
    
    if col1.button("今天戴了！", use_container_width=True, type="primary"):
        add_record(today_str)
        st.rerun()
    
    if col2.button("今天没戴", use_container_width=True):
        st.info("今天跳过～")
        st.rerun()

# 下次提醒
st.divider()
st.subheader("下次应该佩戴的日子")

next_date = get_next_wear_date(today, records)
days_later = (next_date - today).days

if days_later == 0:
    st.error("今天就要戴！（如果还没记录，请点击上面按钮）")
elif days_later == 1:
    st.warning("**明天**就要戴啦！记得～")
elif days_later <= 3:
    st.warning(f"再过 **{days_later}** 天就要戴了")
else:
    st.info(f"下次日期：**{next_date.strftime('%Y-%m-%d')}**　（再过 {days_later} 天）")

st.caption(f"佩戴节奏：每 {WEAR_INTERVAL_DAYS} 天佩戴一次（首次佩戴日：{FIRST_WEAR_DATE}）")

# 历史记录（可折叠）
with st.expander(f"已记录日期（共 {len(records)} 天）", expanded=False):
    if records:
        for d in sorted(records, reverse=True)[:60]:
            st.write(d)
    else:
        st.write("还没有任何佩戴记录～")

st.caption("数据由 Supabase 提供永久存储支持")