import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="서울 지하철 혼잡도 분석",
    page_icon="🚇",
    layout="wide"
)

st.title("🚇 서울 지하철 노선별 혼잡도 분석")
st.markdown(
    """
    **2023년과 2025년 서울 지하철 혼잡도 데이터를 비교하여
    노선별 혼잡도와 변화 양상을 분석합니다.**
    """
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

@st.cache_data
def load_data():

    file_path = "지하철+혼잡도_20261111105028.csv"

    # 첫 번째 행과 두 번째 행이 다중 헤더이므로
    # 실제 분석에 필요한 두 번째 행을 기준으로 읽는다.
    raw = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        header=None
    )

    # 실제 데이터
    years = raw.iloc[2:, 0].astype(str)

    data = raw.iloc[2:, 1:].copy()

    columns = [
        "평균",
        "1호선",
        "2호선",
        "3호선",
        "4호선",
        "5호선",
        "6호선",
        "7호선",
        "8호선",
        "9호선",
        "우이신설선",
        "신림선"
    ]

    data.columns = columns
    data.insert(0, "연도", years.values)

    # 숫자형 변환
    for col in columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    return data


df = load_data()

# --------------------------------------------------
# 노선 목록
# --------------------------------------------------

lines = [
    "1호선",
    "2호선",
    "3호선",
    "4호선",
    "5호선",
    "6호선",
    "7호선",
    "8호선",
    "9호선",
    "우이신설선",
    "신림선"
]

# --------------------------------------------------
# 핵심 지표
# --------------------------------------------------

avg_2023 = df.loc[df["연도"] == "2023", "평균"].iloc[0]
avg_2025 = df.loc[df["연도"] == "2025", "평균"].iloc[0]

change = avg_2025 - avg_2023

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "2023년 전체 평균",
        f"{avg_2023:.1f}%"
    )

with col2:
    st.metric(
        "2025년 전체 평균",
        f"{avg_2025:.1f}%"
    )

with col3:
    st.metric(
        "평균 변화",
        f"{change:+.1f}%p"
    )

# --------------------------------------------------
# 1. 전체 평균 혼잡도 변화
# --------------------------------------------------

st.header("1️⃣ 전체 평균 혼잡도 변화")

st.write(
    "서울 지하철 전체 평균 혼잡도가 2023년과 2025년에 "
    "어떻게 변화했는지 확인합니다."
)

st.info(
    f"2023년 평균 혼잡도는 {avg_2023:.1f}%에서 "
    f"2025년 {avg_2025:.1f}%로 "
    f"{change:+.1f}%p 변화했습니다."
)

# --------------------------------------------------
# 2. 노선별 혼잡도 비교
# --------------------------------------------------

st.header("2️⃣ 노선별 혼잡도 비교")

selected_year = st.selectbox(
    "비교할 연도를 선택하세요.",
    ["2023", "2025"]
)

year_data = df[df["연도"] == selected_year].iloc[0]

chart_data = pd.DataFrame({
    "노선": lines,
    "혼잡도": [year_data[line] for line in lines]
})

chart_data = chart_data.sort_values(
    "혼잡도",
    ascending=False
)

fig = px.bar(
    chart_data,
    x="노선",
    y="혼잡도",
    title=f"{selected_year}년 노선별 평균 혼잡도",
    text_auto=".1f",
    labels={
        "노선": "지하철 노선",
        "혼잡도": "평균 혼잡도 (%)"
    }
)

fig.update_layout(
    yaxis_title="평균 혼잡도 (%)",
    xaxis_title="노선"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 3. 2023 vs 2025 비교
# --------------------------------------------------

st.header("3️⃣ 2023년 vs 2025년 노선별 비교")

comparison = []

for line in lines:
    value_2023 = df.loc[
        df["연도"] == "2023", line
    ].iloc[0]

    value_2025 = df.loc[
        df["연도"] == "2025", line
    ].iloc[0]

    comparison.append({
        "노선": line,
        "2023년": value_2023,
        "2025년": value_2025
    })

comparison_df = pd.DataFrame(comparison)

long_df = comparison_df.melt(
    id_vars="노선",
    value_vars=["2023년", "2025년"],
    var_name="연도",
    value_name="혼잡도"
)

fig2 = px.bar(
    long_df,
    x="노선",
    y="혼잡도",
    color="연도",
    barmode="group",
    title="2023년과 2025년 노선별 혼잡도 비교",
    text_auto=".1f",
    labels={
        "노선": "지하철 노선",
        "혼잡도": "평균 혼잡도 (%)"
    }
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# --------------------------------------------------
# 4. 혼잡도 변화량
# --------------------------------------------------

st.header("4️⃣ 혼잡도가 가장 많이 변한 노선")

comparison_df["변화량"] = (
    comparison_df["2025년"]
    - comparison_df["2023년"]
)

change_df = comparison_df.sort_values(
    "변화량",
    ascending=False
)

fig3 = px.bar(
    change_df,
    x="노선",
    y="변화량",
    title="2023년 → 2025년 혼잡도 변화량",
    text_auto=".1f",
    labels={
        "노선": "지하철 노선",
        "변화량": "혼잡도 변화 (%p)"
    }
)

fig3.add_hline(
    y=0,
    line_dash="dash"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# --------------------------------------------------
# 5. 가장 혼잡한 노선
# --------------------------------------------------

st.header("5️⃣ 2025년 가장 혼잡한 노선 TOP 5")

top5 = (
    comparison_df[
        ["노선", "2025년"]
    ]
    .sort_values(
        "2025년",
        ascending=False
    )
    .head(5)
)

st.dataframe(
    top5,
    hide_index=True,
    use_container_width=True
)

most_crowded = top5.iloc[0]

st.warning(
    f"2025년 기준 가장 높은 혼잡도를 보인 노선은 "
    f"**{most_crowded['노선']}**이며, "
    f"평균 혼잡도는 **{most_crowded['2025년']:.1f}%**입니다."
)

# --------------------------------------------------
# 6. 분석 결과
# --------------------------------------------------

st.header("6️⃣ 분석 결과 및 정책 제안")

increase = comparison_df.sort_values(
    "변화량",
    ascending=False
).iloc[0]

decrease = comparison_df.sort_values(
    "변화량",
    ascending=True
).iloc[0]

st.markdown(
    f"""
    ### 📌 주요 분석 결과

    - 2023년 전체 평균 혼잡도: **{avg_2023:.1f}%**
    - 2025년 전체 평균 혼잡도: **{avg_2025:.1f}%**
    - 전체 평균 변화: **{change:+.1f}%p**
    - 혼잡도가 가장 크게 증가한 노선: **{increase['노선']}**
      ({increase['변화량']:+.1f}%p)
    - 혼잡도가 가장 크게 감소한 노선: **{decrease['노선']}**
      ({decrease['변화량']:+.1f}%p)

    ### 💡 정책 제안

    혼잡도가 높은 노선과 혼잡도가 증가한 노선을 중심으로
    출퇴근 시간대의 배차 간격을 줄이거나 차량을 추가 투입하는
    방안을 고려할 수 있습니다.

    또한 특정 노선에 이용객이 집중되는 현상을 완화하기 위해
    혼잡 시간대 분산을 유도하는 정책도 필요합니다.
    """
)

# --------------------------------------------------
# 원본 데이터
# --------------------------------------------------

with st.expander("📋 원본 데이터 확인"):
    st.dataframe(
        df,
        use_container_width=True
    )
