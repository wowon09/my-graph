import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 타이틀
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("1년치(365일) 일별 박스오피스 데이터를 바탕으로 시간의 흐름에 따른 영화 관객 수 변화를 시각화합니다.")
st.markdown("---")

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # 날짜 열을 진짜 datetime 형식으로 변환 (YYYYMMDD -> YYYY-MM-DD)
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 수치형 데이터 타입 정제
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    df = load_data()
    
    # -------------------------------------------------------------------
    # 구역 1: 영화별 일관객 변화 (선 그래프)
    # -------------------------------------------------------------------
    st.header("📌 Section 1. 영화별 일별 관객 수 추이")
    
    # 영화 목록 추출
    movie_list = sorted(df['영화명'].dropna().unique())
    
    # 영화 선택 드롭다운
    selected_movie = st.selectbox(
        "📊 관객 수 추이를 확인할 영화를 선택하세요:",
        options=movie_list,
        index=0 if movie_list else None
    )
    
    if selected_movie:
        # 선택한 영화의 데이터 필터링
        movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')
        
        # Plotly 선 그래프 생성
        fig1 = px.line(
            movie_df,
            x='날짜',
            y='일관객',
            title=f"<b>[{selected_movie}]</b> 날짜별 일관객 수 변화",
            labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
            markers=True
        )
        
        # Tooltip 및 스타일 설정
        fig1.update_traces(
            hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객 수:</b> %{y:,}명<extra></extra>",
            line=dict(width=2.5, color='#E50914')
        )
        
        fig1.update_layout(
            xaxis_title="날짜",
            yaxis_title="일일 관객 수 (명)",
            hovermode="x unified",
            template="plotly_white",
            height=500
        )
        
        # 그래프 출력
        st.plotly_chart(fig1, use_container_width=True)
        
        # '이 그래프로 알 수 있는 것' 문구 작성
        st.info("💡 **이 그래프로 알 수 있는 것:** 하루 영화 관객 수 10위까지의 영화들을 알 수 있다.")

    st.markdown("---")

    # -------------------------------------------------------------------
    # 구역 2: 기간 내 총 일관객 상위 5개 영화 비교 (선 그래프)
    # -------------------------------------------------------------------
    st.header("📌 Section 2. 총 일관객 상위 5개 영화의 날짜별 관객 수 비교")
    
    # 해당 기간 내 총 일관객 합계 기준 상위 5개 영화 추출
    top5_movies = (
        df.groupby('영화명')['일관객']
        .sum()
        .nlargest(5)
        .index.tolist()
    )
    
    # 상위 5개 영화 데이터 필터링 및 날짜 정렬
    df_top5 = df[df['영화명'].isin(top5_movies)].sort_values('날짜')
    
    # Plotly 다중 선 그래프 생성 (영화명별 색상 구분)
    fig2 = px.line(
        df_top5,
        x='날짜',
        y='일관객',
        color='영화명',
        title="<b>기간 내 총 일관객 수 Top 5 영화의 날짜별 관객 수 추이 비교</b>",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)', '영화명': '영화 제목'},
        markers=True
    )
    
    # Tooltip 설정 및 범례(Legend) 대화형 기능 강화
    fig2.update_traces(
        hovertemplate="<b>영화:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객 수:</b> %{y:,}명<extra></extra>"
    )
    
    fig2.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=550,
        legend=dict(
            title="영화 목록 (클릭하여 토글)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # 그래프 출력
    st.plotly_chart(fig2, use_container_width=True)
    
    # '이 그래프로 알 수 있는 것' 문구 입력 자리
    st.info("💡 **이 그래프로 알 수 있는 것:** ")

    st.markdown("---")

    # -------------------------------------------------------------------
    # 구역 3: 날짜별 10위권 일관객 총합 영역 그래프 (Top 3 주석 표시)
    # -------------------------------------------------------------------
    st.header("📌 Section 3. 날짜별 박스오피스 TOP 10 전체 관객 수 추이")
    
    # 날짜별 10위권 일관객 합계 계산
    daily_total = df.groupby('날짜')['일관객'].sum().reset_index()
    daily_total = daily_total.sort_values('날짜')
    
    # 관객 수 합계가 가장 큰 상위 3일 추출
    top3_days = daily_total.nlargest(3, '일관객')
    
    # 영역 그래프(Area Chart) 생성
    fig3 = px.area(
        daily_total,
        x='날짜',
        y='일관객',
        title="<b>날짜별 박스오피스 Top 10 일관객 총합 (관객 피크 Top 3 날짜 표시)</b>",
        labels={'날짜': '날짜', '일관객': 'TOP 10 일관객 총합(명)'}
    )
    
    fig3.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>TOP 10 관객 총합:</b> %{y:,}명<extra></extra>",
        fillcolor='rgba(229, 9, 20, 0.3)',
        line=dict(color='#E50914', width=2)
    )
    
    # 상위 3개 피크 날짜를 그래프에 주석(Annotation) 및 점으로 표시
    fig3.add_trace(
        go.Scatter(
            x=top3_days['날짜'],
            y=top3_days['일관객'],
            mode='markers',
            marker=dict(color='black', size=9, symbol='circle'),
            name='Top 3 관객 피크일',
            hovertemplate="<b>[Top 3 피크]</b><br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>관객 수:</b> %{y:,}명<extra></extra>"
        )
    )
    
    for idx, row in top3_days.iterrows():
        date_str = row['날짜'].strftime('%Y-%m-%d')
        audience_cnt = f"{row['일관객']:,}명"
        
        fig3.add_annotation(
            x=row['날짜'],
            y=row['일관객'],
            text=f"<b>{date_str}</b><br>({audience_cnt})",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor="black",
            ax=0,
            ay=-40,
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            borderpad=4,
            opacity=0.9
        )
        
    fig3.update_layout(
        xaxis_title="날짜",
        yaxis_title="TOP 10 총 관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=550,
        showlegend=False
    )
    
    # 그래프 출력
    st.plotly_chart(fig3, use_container_width=True)
    
    # '이 그래프로 알 수 있는 것' 문구 입력 자리
    st.info("💡 **이 그래프로 알 수 있는 것:** ")

    st.markdown("---")

    # -------------------------------------------------------------------
    # 구역 4: 추후 그래프 추가용 예시 공간
    # -------------------------------------------------------------------
    st.header("📌 Section 4. (추가 예정) 시간 흐름에 따른 추가 시각화")
    st.text("앞으로 새로운 그래프가 들어올 구역입니다.")
    st.info("💡 **이 그래프로 알 수 있는 것:** ")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
