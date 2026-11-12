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
    **2023년과 2025년 서울 지하철 노선별 평균 혼잡도를 비교하여
    노선별 혼잡도 변화와 혼잡 관리 방안을 분석합니다.**
    """
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

@st.cache_data
def load_data():

    file_path = "지하철+혼잡도_20261111105028.csv"

    raw = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        header=None
    )

    # 데이터 행 추출
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

    data.insert(
        0,
        "연도",
        years.values
    )

    # 숫자로 변환
    for col in columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

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

# ==================================================
# 노선 선택 기능
# ==================================================

st.header("🚇 노선을 선택해 보세요")

selected_line = st.selectbox(
    "분석할 노선을 선택하세요.",
    lines
)

# --------------------------------------------------
# 선택된 노선의 데이터 추출
# --------------------------------------------------

value_2023 = df.loc[
    df["연도"] == "2023",
    selected_line
].iloc[0]

value_2025 = df.loc[
    df["연도"] == "2025",
    selected_line
].iloc[0]

change = value_2025 - value_2023

# ==================================================
# 선택 노선의 핵심 수치
# ==================================================

st.subheader(f"📊 {selected_line} 혼잡도 분석")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="2023년 혼잡도",
        value=f"{value_2023:.1f}%"
    )

with col2:
    st.metric(
        label="2025년 혼잡도",
        value=f"{value_2025:.1f}%"
    )

with col3:
    st.metric(
        label="변화량",
        value=f"{change:+.1f}%p"
    )

# ==================================================
# 변화량에 따른 동적 메시지
# ==================================================

if change > 0:

    st.error(
        f"🔴 {selected_line}은(는) "
        f"2023년 대비 혼잡도가 "
        f"**{change:.1f}%p 증가했습니다.**"
    )

elif change < 0:

    st.success(
        f"🟢 {selected_line}은(는) "
        f"2023년 대비 혼잡도가 "
        f"**{abs(change):.1f}%p 감소했습니다.**"
    )

else:

    st.info(
        f"🔵 {selected_line}은(는) "
        f"2023년과 2025년의 혼잡도가 "
        f"**변화하지 않았습니다.**"
    )

# ==================================================
# 선택 노선의 2023 vs 2025 그래프
# ==================================================

st.subheader(f"📈 {selected_line} 연도별 혼잡도")

line_chart_data = pd.DataFrame({
    "연도": ["2023년", "2025년"],
    "혼잡도": [
        value_2023,
        value_2025
    ]
})

fig_selected = px.bar(
    line_chart_data,
    x="연도",
    y="혼잡도",
    text_auto=".1f",
    title=f"{selected_line} 2023년 vs 2025년 혼잡도",
    labels={
        "연도": "연도",
        "혼잡도": "평균 혼잡도 (%)"
    }
)

fig_selected.update_layout(
    yaxis_title="평균 혼잡도 (%)",
    xaxis_title=""
)

st.plotly_chart(
    fig_selected,
    use_container_width=True
)

# ==================================================
# 전체 노선 비교
# ==================================================

st.header("📊 전체 노선 혼잡도 비교")

selected_year = st.selectbox(
    "비교할 연도를 선택하세요.",
    ["2023", "2025"],
    key="year_select"
)

year_data = df[
    df["연도"] == selected_year
].iloc[0]

chart_data = pd.DataFrame({
    "노선": lines,
    "혼잡도": [
        year_data[line]
        for line in lines
    ]
})

chart_data = chart_data.sort_values(
    "혼잡도",
    ascending=False
)

fig = px.bar(
    chart_data,
    x="노선",
    y="혼잡도",
    title=f"{selected_year} 노선별 평균 혼잡도",
    text_auto=".1f",
    labels={
        "노선": "지하철 노선",
        "혼잡도": "평균 혼잡도 (%)"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# 2023 vs 2025 전체 비교
# ==================================================

st.header("📈 2023년 vs 2025년 전체 노선 비교")

comparison = []

for line in lines:

    value_2023_line = df.loc[
        df["연도"] == "2023",
        line
    ].iloc[0]

    value_2025_line = df.loc[
        df["연도"] == "2025",
        line
    ].iloc[0]

    comparison.append({
        "노선": line,
        "2023년": value_2023_line,
        "2025년": value_2025_line,
        "변화량": value_2025_line - value_2023_line
    })

comparison_df = pd.DataFrame(comparison)

long_df = comparison_df.melt(
    id_vars="노선",
    value_vars=[
        "2023년",
        "2025년"
    ],
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

# ==================================================
# 혼잡도 변화량
# ==================================================

st.header("📉 노선별 혼잡도 변화량")

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
        "변화량": "변화량 (%p)"
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

# ==================================================
# TOP 5
# ==================================================

st.header("🔥 2025년 혼잡도 TOP 5")

top5 = comparison_df[
    ["노선", "2025년"]
].sort_values(
    "2025년",
    ascending=False
).head(5)

st.dataframe(
    top5,
    hide_index=True,
    use_container_width=True
)

# ==================================================
# 정책 제안
# ==================================================

st.header("💡 데이터 기반 정책 제안")

most_crowded = comparison_df.sort_values(
    "2025년",
    ascending=False
).iloc[0]

most_increased = comparison_df.sort_values(
    "변화량",
    ascending=False
).iloc[0]

most_decreased = comparison_df.sort_values(
    "변화량",
    ascending=True
).iloc[0]

st.markdown(
    f"""
    ### 분석 결과

    - 2025년 가장 높은 혼잡도를 보인 노선은
      **{most_crowded['노선']} ({most_crowded['2025년']:.1f}%)**입니다.
    - 2023년 대비 혼잡도가 가장 크게 증가한 노선은
      **{most_increased['노선']} ({most_increased['변화량']:+.1f}%p)**입니다.
    - 혼잡도가 가장 크게 감소한 노선은
      **{most_decreased['노선']} ({most_decreased['변화량']:+.1f}%p)**입니다.

    ### 정책 제안

    혼잡도가 높은 노선과 혼잡도가 증가한 노선을 중심으로
    다음과 같은 정책을 고려할 수 있습니다.

    1. 출퇴근 시간대 배차 간격 단축
    2. 혼잡 노선의 추가 차량 투입
    3. 혼잡 시간대 이용객 분산 유도
    4. 혼잡 노선과 연결되는 대체 노선의 이용 활성화
    """
)

# ==================================================
# 원본 데이터
# ==================================================

with st.expander("📋 원본 데이터 확인"):

    st.dataframe(
        df,
        use_container_width=True
    )
