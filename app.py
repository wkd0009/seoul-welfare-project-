import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------
# 기본 설정
# -----------------------------------------
st.set_page_config(
    page_title="서울 지하철 혼잡도 분석",
    page_icon="🚇",
    layout="wide"
)

st.title("🚇 서울 지하철 노선별 혼잡도 분석")
st.write("2023년과 2025년의 서울 지하철 노선별 혼잡도를 비교합니다.")

# -----------------------------------------
# 데이터 불러오기
# -----------------------------------------
file_path = "지하철+혼잡도_20261111105028.csv"

try:
    df = pd.read_csv(file_path, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding="utf-8-sig")
except FileNotFoundError:
    st.error(f"데이터 파일을 찾을 수 없습니다: {file_path}")
    st.stop()

# -----------------------------------------
# 데이터 전처리
# -----------------------------------------
df["시점"] = df["시점"].astype(str)

# 시점에서 연도 추출
df["연도"] = df["시점"].str[:4]

# 분석할 노선 목록
lines = [
    "1호선", "2호선", "3호선", "4호선", "5호선",
    "6호선", "7호선", "8호선", "9호선",
    "우이신설선", "신림선"
]

# -----------------------------------------
# 제목
# -----------------------------------------
st.header("📊 전체 노선 혼잡도 변화")

st.write(
    "변화량은 **2025년 혼잡도 - 2023년 혼잡도**로 계산합니다. "
    "양수이면 혼잡도가 증가했고, 음수이면 감소한 것입니다."
)

# -----------------------------------------
# 2023년 / 2025년 데이터 추출
# -----------------------------------------
try:
    data_2023 = df[df["연도"] == "2023"].iloc[0]
    data_2025 = df[df["연도"] == "2025"].iloc[0]
except IndexError:
    st.error("2023년 또는 2025년 데이터를 찾을 수 없습니다.")
    st.stop()

# -----------------------------------------
# 전체 노선 변화량 계산
# -----------------------------------------
change_data = []

for line in lines:
    try:
        value_2023 = float(data_2023[line])
        value_2025 = float(data_2025[line])

        change = value_2025 - value_2023

        change_data.append({
            "노선": line,
            "2023년": value_2023,
            "2025년": value_2025,
            "변화량": change
        })

    except (KeyError, ValueError, TypeError):
        # 해당 노선의 데이터가 없거나 숫자로 변환할 수 없는 경우
        continue

change_df = pd.DataFrame(change_data)

# 데이터가 하나도 없을 경우
if change_df.empty:
    st.error("분석할 노선 데이터가 없습니다.")
    st.stop()

# -----------------------------------------
# 1. 혼잡도 증가 TOP 5
# -----------------------------------------
st.header("🔴 혼잡도 증가 TOP 5")

increase_df = change_df[change_df["변화량"] > 0].copy()

# 증가폭이 큰 순서대로 정렬
increase_df = increase_df.sort_values(
    by="변화량",
    ascending=False
).head(5)

if increase_df.empty:
    st.info("혼잡도가 증가한 노선이 없습니다.")
else:
    increase_df = increase_df.reset_index(drop=True)
    increase_df.insert(
        0,
        "순위",
        range(1, len(increase_df) + 1)
    )

    # 화면 표시용 데이터
    increase_display = increase_df[
        ["순위", "노선", "변화량"]
    ].copy()

    increase_display["변화량"] = increase_display["변화량"].apply(
        lambda x: f"+{x:.1f}%p"
    )

    st.dataframe(
        increase_display,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------
# 2. 혼잡도 감소 TOP 5
# -----------------------------------------
st.header("🔵 혼잡도 감소 TOP 5")

decrease_df = change_df[change_df["변화량"] < 0].copy()

# 감소폭이 큰 순서대로 정렬
# 예: -22.6이 -5.3보다 먼저 나오도록 절댓값 기준으로 정렬
decrease_df["감소폭"] = decrease_df["변화량"].abs()

decrease_df = decrease_df.sort_values(
    by="감소폭",
    ascending=False
).head(5)

if decrease_df.empty:
    st.info("혼잡도가 감소한 노선이 없습니다.")
else:
    decrease_df = decrease_df.reset_index(drop=True)
    decrease_df.insert(
        0,
        "순위",
        range(1, len(decrease_df) + 1)
    )

    # 화면 표시용 데이터
    decrease_display = decrease_df[
        ["순위", "노선", "변화량"]
    ].copy()

    decrease_display["변화량"] = decrease_display["변화량"].apply(
        lambda x: f"{x:.1f}%p"
    )

    st.dataframe(
        decrease_display,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------
# 3. 노선별 혼잡도 변화 전체 그래프
# -----------------------------------------
st.header("📈 전체 노선 혼잡도 변화량")

graph_df = change_df.sort_values(
    by="변화량",
    ascending=False
)

fig = px.bar(
    graph_df,
    x="노선",
    y="변화량",
    text="변화량",
    labels={
        "노선": "지하철 노선",
        "변화량": "혼잡도 변화량 (%p)"
    },
    title="2023년 대비 2025년 노선별 혼잡도 변화"
)

fig.update_traces(
    texttemplate="%{text:.1f}%p",
    textposition="outside"
)

fig.add_hline(
    y=0,
    line_width=1
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------------
# 4. 노선 선택 기능
# -----------------------------------------
st.header("🚇 개별 노선 분석")

selected_line = st.selectbox(
    "분석할 노선을 선택하세요.",
    lines
)

selected_data = change_df[
    change_df["노선"] == selected_line
]

if selected_data.empty:
    st.warning("선택한 노선의 데이터가 없습니다.")
else:
    value_2023 = selected_data["2023년"].iloc[0]
    value_2025 = selected_data["2025년"].iloc[0]
    change = selected_data["변화량"].iloc[0]

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

    # -----------------------------------------
    # 변화에 따른 자동 분석 문장
    # -----------------------------------------
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

    # -----------------------------------------
    # 선택한 노선 그래프
    # -----------------------------------------
    selected_graph = pd.DataFrame({
        "연도": ["2023년", "2025년"],
        "혼잡도": [value_2023, value_2025]
    })

    fig_selected = px.bar(
        selected_graph,
        x="연도",
        y="혼잡도",
        text="혼잡도",
        title=f"{selected_line} 혼잡도 변화",
        labels={
            "연도": "연도",
            "혼잡도": "혼잡도 (%)"
        }
    )

    fig_selected.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    st.plotly_chart(
        fig_selected,
        use_container_width=True
    )

# -----------------------------------------
# 5. 원본 데이터 확인
# -----------------------------------------
with st.expander("📄 원본 데이터 보기"):
    st.dataframe(
        df,
        use_container_width=True
    )
