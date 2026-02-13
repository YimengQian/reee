import streamlit as st
import datetime
import os
import json
from dateutil.relativedelta import relativedelta

# ─── 配置 ────────────────────────────────────────────────
EVERY_OTHER_DAY = True           # 改成 False 则使用下面的 WEEKLY_DAYS
WEEKLY_DAYS = [0, 2, 4]          # 周一=0, 周三=2, 周五=4 ...
FIRST_WEAR_DATE = "2025-02-10"   # 必须改成你第一次戴的真实日期！
DATA_FILE = "retainer_records.json"
# ──────────────────────────────────────────────────────────

@st.cache_data
def load_records():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_records(records_set):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(records_set), f, ensure_ascii=False)

def is_should_wear_date(dt: datetime.date) -> bool:
    start = datetime.datetime.strptime(FIRST_WEAR_DATE, "%Y-%m-%d").date()
    days_diff = (dt - start).days
    
    if EVERY_OTHER_DAY:
        return days_diff % 2 == 0
    else:
        return dt.weekday() in WEEKLY_DAYS

def get_next_wear_date(today: datetime.date, worn_set) -> datetime.date:
    candidate = today
    while True:
        candidate += datetime.timedelta(days=1)
        if candidate.strftime("%Y-%m-%d") in worn_set:
            continue
        if is_should_wear_date(candidate):
            return candidate

# ─── 主程序 ───────────────────────────────────────────────

st.title("保持器佩戴提醒小助手")
st.caption("简单记录 & 自动提醒下次该戴的日子")

today_str = datetime.date.today().strftime("%Y-%m-%d")
st.subheader(f"今天：{today_str}")

records = load_records()

# 显示已记录的天数
st.info(f"目前已记录佩戴天数：**{len(records)}** 天")

# 今日操作
if today_str in records:
    st.success("今天已经记录佩戴 ✓")
else:
    col1, col2 = st.columns(2)
    if col1.button("今天戴了", use_container_width=True, type="primary"):
        records.add(today_str)
        save_records(records)
        st.success("已记录！今天佩戴 ✓")
        st.rerun()
    
    if col2.button("今天没戴", use_container_width=True):
        st.info("好的，已跳过今天～")
        st.rerun()

# 下次提醒
if records:
    next_date = get_next_wear_date(datetime.date.today(), records)
    days_later = (next_date - datetime.date.today()).days
    
    st.divider()
    st.subheader("下次应该佩戴的日子")
    
    if days_later == 0:
        st.error("今天就要戴！（但你好像还没记录？）")
    elif days_later == 1:
        st.warning("明天就要戴啦！记得～")
    elif days_later <= 3:
        st.warning(f"再过 **{days_later}** 天就要戴了")
    else:
        st.info(f"下次佩戴日期：**{next_date}**　（再过 {days_later} 天）")
    
    st.caption(f"佩戴节奏：{'隔天佩戴' if EVERY_OTHER_DAY else '每周固定几天'}")

# 历史记录（可折叠）
with st.expander("查看已佩戴历史"):
    if records:
        sorted_dates = sorted(records, reverse=True)
        for d in sorted_dates[:40]:  # 最多显示最近40天
            st.write(d)
    else:
        st.write("还没有记录～")

st.caption("数据保存在本地文件 retainer_records.json　建议用 Git / 云盘定期备份")