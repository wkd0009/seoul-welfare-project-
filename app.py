import streamlit as st
import pandas as pd

# 앱 타이틀
st.title("서울시 1인 가구 복지 사각지대 분석")
st.write("서울 열린데이터광장 데이터를 활용해 1인 가구 대비 복지 인프라 현황을 시각화합니다.")

# 데이터 불러오기 (캐싱을 이용해 로딩 속도 최적화)
@st.cache_data
def load_data():
    df_single = pd.read_csv('data/single_household.csv', encoding='cp949')
    df_welfare = pd.read_csv('data/welfare_facilities.csv', encoding='cp949')
    return df_single, df_welfare

df_single, df_welfare = load_data()

# 사이드바 설정 (사용자 인터랙션 추가)
st.sidebar.header("필터 설정")
selected_gu = st.sidebar.selectbox("자치구를 선택하세요", df_single['자치구명'].unique())

# 선택한 자치구 데이터 필터링 및 출력
st.subheader(f"📍 {selected_gu} 현황 요약")
# (여기에 분석 표나 지도를 그리는 코드를 추가합니다)
