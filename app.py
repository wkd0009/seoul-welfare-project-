import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="서울 지하철 혼잡도 분석",
    page_icon="🚇",
    layout="wide"
)

st.title("🚇 서울 지하철 노선별 혼잡도 분석")
st.write("2023년과 2025년 서울 지하철 노선별 혼잡도를 비교합니다.")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
file_path = "지하철+혼잡도_20261111105028.csv"

try:
    df = pd.read_csv(file_path, encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding="cp949")

# 컬럼명 앞뒤 공백 제거
df.columns = df.columns.astype(str).str.strip()

# --------------------------------------------------
# 데이터 확인 및 정리
# --------------------------------------------------

# 시점 컬럼 확인
if "시점" not in df.columns:
    st.error("CSV 파일에서 '시점' 컬럼을 찾을 수 없습니다.")
    st.write("현재 CSV의 컬럼명:")
    st.write(df.columns.tolist())
    st.stop()

df["시점"] = df["시점"].astype(str).str.strip()

# 연도 추출
df["연도"] = df["시점"].str[:4]

# 숫자형으로 변환할 수 있는 컬럼 변환
for column in df.columns:
    if column not in ["시점", "연도"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

# --------------------------------------------------
# 분석 대상 노선
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

# 실제 CSV에 존재하는 노선만 사용
available_lines = [
    line for line in lines
    if line in df.columns
]

# 존재하지 않는 노선이 있다면 경고
missing_lines = [
    line for line in lines
    if line not in df.columns
]

if missing_lines:
    st.warning(
        "CSV에서 다음 노선 컬럼을 찾을 수 없습니다: "
        + ", ".join(missing_lines)
    )

if not available_lines:
    st.error("분석할 지하철 노선 데이터가 없습니다.")
    st.write("현재 CSV 컬럼명:")
    st.write(df.columns.tolist())
    st.stop()

# --------------------------------------------------
# 혼잡도 등급 함수
# --------------------------------------------------
def get_congestion_grade(value):

    if value < 100:
        return "여유", "🟢", "#2E7D32"

    elif value < 130:
        return "보통", "🔵", "#1976D2"

    elif value < 150:
        return "혼잡", "🟠", "#EF6C00"

    else:
        return "매우 혼잡", "🔴", "#C62828"


# --------------------------------------------------
# 혼잡도 뱃지 UI
# --------------------------------------------------
def congestion_badge(value):

    grade, emoji, color = get_congestion_grade(value)

    st.markdown(
        f"""
        <div style="
            display: inline-block;
            padding: 8px 18px;
            border-radius: 20px;
            background-color: {color};
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin: 5px 0 15px 0;
        ">
            {emoji} {grade}
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------
if "2023" not in df["연도"].values:
    st.error("2023년 데이터가 없습니다.")
    st.write(df["연도"].unique())
    st.stop()

if "2025" not in df["연도"].values:
    st.error("2025년 데이터가 없습니다.")
    st.write(df["연도"].unique())
    st.stop()


# --------------------------------------------------
# 전체 평균 혼잡도
# --------------------------------------------------
st.header("📊 전체 평균 혼잡도")

# '평균' 컬럼이 있는 경우
if "평균" in df.columns:

    avg_2023 = df.loc[
        df["연도"] == "2023",
        "평균"
    ].iloc[0]

    avg_2025 = df.loc[
        df["연도"] == "2025",
        "평균"
    ].iloc[0]

else:

    # 평균 컬럼이 없을 경우
    # 각 노선의 평균값을 계산
    avg_2023 = df.loc[
        df["연도"] == "2023",
        available_lines
    ].mean(axis=1).iloc[0]

    avg_2025 = df.loc[
        df["연도"] == "2025",
        available_lines
    ].mean(axis=1).iloc[0]

avg_change = avg_2025 - avg_2023

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "2023년 평균 혼잡도",
        f"{avg_2023:.1f}%"
    )

with col2:
    st.metric(
        "2025년 평균 혼잡도",
        f"{avg_2025:.1f}%"
    )

with col3:
    st.metric(
        "변화량",
        f"{avg_change:+.1f}%p"
    )

st.subheader("현재 전체 평균 혼잡도 등급")

congestion_badge(avg_2025)


# --------------------------------------------------
# 혼잡도 등급 기준 안내
# --------------------------------------------------
st.info(
    """
### 🚦 혼잡도 등급 기준

🟢 **여유** : 100% 미만

🔵 **보통** : 100% 이상 ~ 130% 미만

🟠 **혼잡** : 130% 이상 ~ 150% 미만

🔴 **매우 혼잡** : 150% 이상

**※ 본 등급은 공식 기준이 아니며, 데이터 이해를 돕기 위해 본 사이트에서 자체 설정한 분석 기준입니다.**
"""
)


# --------------------------------------------------
# 노선 선택
# --------------------------------------------------
st.header("🚇 노선별 상세 분석")

selected_line = st.selectbox(
    "분석할 노선을 선택하세요.",
    available_lines
)

value_2023 = df.loc[
    df["연도"] == "2023",
    selected_line
].iloc[0]

value_2025 = df.loc[
    df["연도"] == "2025",
    selected_line
].iloc[0]

change = value_2025 - value_2023


# --------------------------------------------------
# 선택 노선 수치
# --------------------------------------------------
st.subheader(f"📍 {selected_line} 혼잡도")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "2023년 혼잡도",
        f"{value_2023:.1f}%"
    )

with col2:
    st.metric(
        "2025년 혼잡도",
        f"{value_2025:.1f}%"
    )

with col3:
    st.metric(
        "변화량",
        f"{change:+.1f}%p"
    )


# --------------------------------------------------
# 혼잡도 등급
# --------------------------------------------------
st.write("### 현재 혼잡도 등급")

congestion_badge(value_2025)


# --------------------------------------------------
# 변화량 분석
# --------------------------------------------------
if change > 0:

    st.error(
        f"🔴 {selected_line}은(는) 2023년 대비 혼잡도가 "
        f"**{change:.1f}%p 증가했습니다.**"
    )

elif change < 0:

    st.success(
        f"🟢 {selected_line}은(는) 2023년 대비 혼잡도가 "
        f"**{abs(change):.1f}%p 감소했습니다.**"
    )

else:

    st.info(
        f"🔵 {selected_line}은(는) 2023년과 2025년의 "
        f"혼잡도가 **변화하지 않았습니다.**"
    )


# --------------------------------------------------
# 선택 노선 그래프
# --------------------------------------------------
chart_data = pd.DataFrame({
    "연도": ["2023년", "2025년"],
    "혼잡도": [value_2023, value_2025]
})

fig = px.bar(
    chart_data,
    x="연도",
    y="혼잡도",
    text="혼잡도",
    title=f"{selected_line} 2023년 vs 2025년 혼잡도"
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    yaxis_title="혼잡도 (%)",
    xaxis_title="연도"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 2025년 노선별 혼잡도
# --------------------------------------------------
st.header("📈 2025년 노선별 혼잡도")

line_data = pd.DataFrame({
    "노선": available_lines,
    "혼잡도": [
        df.loc[
            df["연도"] == "2025",
            line
        ].iloc[0]
        for line in available_lines
    ]
})

line_data = line_data.sort_values(
    "혼잡도",
    ascending=False
)

fig2 = px.bar(
    line_data,
    x="노선",
    y="혼잡도",
    text="혼잡도",
    title="2025년 서울 지하철 노선별 혼잡도"
)

fig2.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig2.update_layout(
    yaxis_title="혼잡도 (%)",
    xaxis_title="노선"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# --------------------------------------------------
# 2023 → 2025 변화량
# --------------------------------------------------
st.header("📊 노선별 혼잡도 변화")

change_data = []

for line in available_lines:

    v2023 = df.loc[
        df["연도"] == "2023",
        line
    ].iloc[0]

    v2025 = df.loc[
        df["연도"] == "2025",
        line
    ].iloc[0]

    change_data.append({
        "노선": line,
        "2023년": v2023,
        "2025년": v2025,
        "변화량": v2025 - v2023
    })

change_df = pd.DataFrame(change_data)

change_df = change_df.sort_values(
    "변화량",
    ascending=False
)

fig3 = px.bar(
    change_df,
    x="노선",
    y="변화량",
    text="변화량",
    title="2023년 대비 2025년 혼잡도 변화"
)

fig3.update_traces(
    texttemplate="%{text:+.1f}%p",
    textposition="outside"
)

fig3.add_hline(
    y=0,
    line_dash="dash"
)

fig3.update_layout(
    yaxis_title="변화량 (%p)",
    xaxis_title="노선"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# --------------------------------------------------
# 증가 TOP 5
# --------------------------------------------------
st.header("🔺 혼잡도 증가 노선 TOP 5")

increase_top5 = change_df.head(5)

st.dataframe(
    increase_top5[
        ["노선", "2023년", "2025년", "변화량"]
    ],
    use_container_width=True
)


# --------------------------------------------------
# 감소 TOP 5
# --------------------------------------------------
st.header("🔻 혼잡도 감소 노선 TOP 5")

decrease_top5 = change_df.sort_values(
    "변화량"
).head(5)

st.dataframe(
    decrease_top5[
        ["노선", "2023년", "2025년", "변화량"]
    ],
    use_container_width=True
)


# --------------------------------------------------
# 정책 제안
# --------------------------------------------------
st.header("💡 정책적 시사점")

st.write(
    """
혼잡도가 높은 노선은 출퇴근 시간대 열차 운행 확대,
배차 간격 단축, 승객 분산 등의 정책을 고려할 수 있습니다.

반대로 혼잡도가 감소한 노선은 이용객 변화의 원인을 분석하여
다른 노선의 혼잡 완화 정책에 활용할 수 있습니다.
"""
)


# --------------------------------------------------
# 데이터 한계
# --------------------------------------------------
st.header("⚠️ 데이터의 한계")

st.warning(
    """
본 분석은 노선별 평균 혼잡도 데이터를 활용한 분석입니다.
따라서 특정 역, 시간대, 방향별 혼잡도 차이를 직접적으로 보여주지는 않습니다.

또한 혼잡도 등급은 공식적인 서울교통공사 기준이 아니라
본 사이트에서 데이터 이해를 돕기 위해 설정한 분석 기준입니다.
"""
)


# --------------------------------------------------
# 원본 데이터
# --------------------------------------------------
with st.expander("📄 원본 데이터 확인하기"):
    st.dataframe(
        df,
        use_container_width=True
    )
