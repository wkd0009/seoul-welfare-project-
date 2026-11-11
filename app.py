import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. 앱 제목 설정
st.title("🚇 서울시 지하철 시간대별 혼잡도 분석기")
st.write("지하철 역을 선택하여 시간대별 승하차 인원 패턴을 확인해보세요.")

# 2. 데이터 불러오기 (캐싱 적용)
@st.cache_data
def load_data():
    # 서울시 공공데이터는 보통 cp949 인코딩이 많습니다. 에러가 나면 utf-8로 바꿔보세요.
    df = pd.read_csv('subway_data.csv', encoding='cp949')
    return df

df = load_data()

# 데이터프레임 구조 확인용 (사이드바에 간단히 띄우기)
if st.sidebar.checkbox("원본 데이터 미리보기"):
    st.dataframe(df.head())

# 3. 사용자 필터 (호선 선택 -> 역 선택)
# 데이터 컬럼명은 실제 다운로드 받은 CSV 파일의 이름에 맞게 수정이 필요할 수 있습니다. (예: '호선명', '역명')
lines = df['호선명'].unique()
selected_line = st.sidebar.selectbox("호선을 선택하세요", lines)

# 선택한 호선에 해당하는 역만 필터링
filtered_df_by_line = df[df['호선명'] == selected_line]
stations = filtered_df_by_line['역명'].unique()
selected_station = st.sidebar.selectbox("역을 선택하세요", stations)

# 4. 선택한 역의 데이터 추출 및 시각화
st.subheader(f"📍 {selected_line} {selected_station} 시간대별 승하차 현황")

# 선택한 역의 행 데이터 추출
station_data = filtered_df_by_line[filtered_df_by_line['역명'] == selected_station]

if not station_data.empty:
    # 시간대별 승차/하차 컬럼만 골라내어 보기 쉽게 가공
    # (일반적으로 서울시 데이터는 '07~08시 승차', '08~09시 승차' 형태로 되어 있습니다.)
    st.write("선택된 역의 상세 데이터입니다.")
    st.dataframe(station_data)
    
    # 예시 그래프 (Streamlit 기본 바 차트 활용)
    # 데이터 구조에 맞춰 x축과 y축 컬럼명을 지정해주세요.
    st.info("💡 아래 데이터를 활용해 출퇴근 시간대(예: 08~09시, 18~19시)에 승하차 인원이 얼마나 몰리는지 분석해 보세요!")
else:
    st.warning("해당 역의 데이터가 없습니다.")
