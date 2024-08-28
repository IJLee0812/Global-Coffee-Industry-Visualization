import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="커피 데이터 시각화", page_icon="☕", layout="wide")

# 배경 이미지 추가
st.image("./image/bg.jpg", use_column_width=True)


# 데이터 로드 및 전처리 함수들
@st.cache_data
def load_production_data():
    data = pd.read_csv('./data/productions.csv', encoding="ISO-8859-1")
    df = pd.DataFrame(data)
    new_columns = df.columns[:2].tolist() + [col[:4] for col in df.columns[2:]]
    df.columns = new_columns
    df = df.loc[:, ~df.columns.duplicated()]
    df_filtered = df[~(df == 0.0).any(axis=1)]
    df_filtered.reset_index(inplace=True)
    df_filtered = df_filtered.drop('index', axis=1)
    df_filtered.rename(columns={'Tota': 'Total_Production'}, inplace=True)
    top_20_countries = df_filtered.nlargest(20, 'Total_Production')
    top_20_countries['Coffee type'] = top_20_countries['Coffee type'].replace('Robusta/Arabica', 'Arabica/Robusta')
    return top_20_countries

@st.cache_data
def load_import_data():
    data = pd.read_csv('./data/imports.csv', encoding="ISO-8859-1")
    df = pd.DataFrame(data)
    df_filtered = df[~(df == 0).any(axis=1)]
    df_filtered.reset_index(inplace=True)
    df_filtered = df_filtered.drop('index', axis=1)
    top_20_countries = df_filtered.nlargest(20, 'Total_import')
    return top_20_countries

@st.cache_data
def load_export_data():
    data = pd.read_csv('./data/exports.csv', encoding="ISO-8859-1")
    df = pd.DataFrame(data)
    df_filtered = df[~(df == 0).any(axis=1)]
    df_filtered.reset_index(inplace=True)
    df_filtered = df_filtered.drop('index', axis=1)
    top_20_countries = df_filtered.nlargest(20, 'Total_export')
    return top_20_countries

@st.cache_data
def load_consumption_data():
    data = pd.read_csv('./data/consumptions.csv', encoding="ISO-8859-1")
    df = pd.DataFrame(data)
    df_filtered = df[~(df == 0).any(axis=1)]
    df_filtered.reset_index(inplace=True)
    df_filtered = df_filtered.drop('index', axis=1)
    top_20_countries = df_filtered.nlargest(20, 'Total_import_consumption')
    return top_20_countries

# 타이틀 및 설명
st.title("☕ 세계 커피 데이터 시각화 🌍")
st.markdown("""
1990년부터 2019년까지의 커피 산업 데이터를 분석한 streamlit 페이지입니다.
이 시각화 도구를 통해 전 세계 커피 산업의 다양한 측면을 탐색할 수 있습니다.
사이드바에서 데이터를 선택하고 원하는 방식으로 맞춤 설정하세요!
""")

# 사이드바 컨트롤
st.sidebar.header("데이터 선택")
dataset = st.sidebar.selectbox(
    "데이터셋 선택",
    options=["생산량", "수입량", "수출량", "소비량"]
)

st.sidebar.header("보기 맞춤 설정")
color_scheme = st.sidebar.selectbox(
    "색상 스키마 선택",
    options=["선명한 색상", "파스텔", "차가운 색상"]
)

show_values = st.sidebar.checkbox("값 표시", value=True)

# 색상 스키마 정의
color_schemes = {
    "선명한 색상": px.colors.qualitative.Vivid,
    "파스텔": px.colors.qualitative.Pastel,
    "차가운 색상": px.colors.qualitative.Set3
}

# 그래프 생성 함수
def create_bar_graph(data, x, y, title, color_scheme, show_values):
    fig = px.bar(
        data, 
        x=x, 
        y=y,
        title=title,
        labels={y: y.replace('_', ' ').title()},
        template='plotly_white',
        color='Country' if dataset != "생산량" else 'Coffee type',
        color_discrete_sequence=color_schemes[color_scheme]
    )

    fig.update_layout(
        xaxis_title="국가",
        yaxis_title=y.replace('_', ' ').title(),
        font=dict(family="Arial", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        showlegend=(dataset == "생산량")
    )

    fig.update_xaxes(tickangle=45)

    if show_values:
        for i, row in data.iterrows():
            fig.add_annotation(
                x=row[x],
                y=row[y],
                text=f"{row[y]:,.0f}",
                showarrow=False,
                yshift=10,
                font=dict(size=8)
            )

    return fig

def create_line_graph(data, country, title):
    years = [str(year) for year in range(1990, 2020)]
    country_data = data[data['Country'] == country]
    if dataset == "생산량":
        y_data = country_data[years].iloc[0].values
    else:
        y_data = country_data[years].sum(axis=0).values

    fig = px.line(
        x=years, 
        y=y_data,
        title=f"{country}의 {title}",
        labels={'x': '년도', 'y': '수치'},
        template='plotly_white'
    )

    fig.update_layout(
        xaxis_title="년도",
        yaxis_title="수치",
        font=dict(family="Arial", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        height=600
    )

    return fig

st.markdown("<br><br>", unsafe_allow_html=True)

# 데이터 로드 및 그래프 생성
if dataset == "생산량":
    st.subheader("상위 20개 커피 생산국 데이터 그래프")
    data = load_production_data()
    fig = create_bar_graph(data, 'Country', 'Total_Production', '상위 20개 커피 생산국', color_scheme, show_values)
elif dataset == "수입량":
    st.subheader("상위 20개 커피 수입국 데이터 그래프")
    data = load_import_data()
    fig = create_bar_graph(data, 'Country', 'Total_import', '상위 20개 커피 수입국', color_scheme, show_values)
elif dataset == "수출량":
    st.subheader("상위 20개 커피 수출국 데이터 그래프")
    data = load_export_data()
    fig = create_bar_graph(data, 'Country', 'Total_export', '상위 20개 커피 수출국', color_scheme, show_values)
else:  # 소비량
    st.subheader("상위 20개 커피 소비국 데이터 그래프")
    data = load_consumption_data()
    fig = create_bar_graph(data, 'Country', 'Total_import_consumption', '상위 20개 커피 소비국', color_scheme, show_values)

# 그래프 표시
st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 국가 선택
st.subheader("국가별 시계열 데이터 그래프")
selected_country = st.selectbox("국가 선택", data['Country'])

# 시계열 그래프 생성 및 표시
if dataset == "생산량":
    line_fig = create_line_graph(data, selected_country, "생산량 시계열 데이터")
elif dataset == "수입량":
    line_fig = create_line_graph(data, selected_country, "수입량 시계열 데이터")
elif dataset == "수출량":
    line_fig = create_line_graph(data, selected_country, "수출량 시계열 데이터")
else:  # 소비량
    line_fig = create_line_graph(data, selected_country, "소비량 시계열 데이터")

st.plotly_chart(line_fig, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 데이터 테이블 표시
st.subheader("원본 데이터 테이블")
st.dataframe(data.style.background_gradient(cmap='YlOrRd', subset=[data.columns[-1]]))

st.markdown("<br><br>", unsafe_allow_html=True)

# 데이터셋 별 추가 정보
if dataset == "생산량":
    st.markdown("""
    ### 생산 데이터에 대하여
    이 시각화는 상위 20개 커피 생산국과 그들의 커피 종류별 생산량(아라비카, 로부스타 또는 혼합)을 보여줍니다.

    <br>

    ### 인사이트
    - 브라질은 가장 큰 커피 생산국이며 다른 나라들보다 현저히 앞서 있습니다.
    - 상위 생산국 대부분은 아라비카 커피에 집중하고 있습니다.
    - 베트남은 상위 국가 중 가장 큰 로부스타 생산국으로 주목받고 있습니다.
    """, unsafe_allow_html=True)
elif dataset == "수입량":
    st.markdown("""
    ### 수입 데이터에 대하여
    이 시각화는 상위 20개 커피 수입국과 그들의 수입량을 보여줍니다.

    <br>

    ### 인사이트
    - 미국은 가장 큰 커피 수입국으로, 다른 국가들보다 현저히 앞서 있습니다.
    - 독일, 이탈리아, 프랑스와 같은 유럽 국가들이 주요 커피 수입국입니다.
    - 일본은 아시아에서 주요 커피 수입국으로 두드러집니다.
    """, unsafe_allow_html=True)
elif dataset == "수출량":
    st.markdown("""
    ### 수출 데이터에 대하여
    이 시각화는 상위 20개 커피 수출국과 그들의 수출량을 보여줍니다.

    <br>

    ### 인사이트
    - 브라질은 가장 큰 커피 수출국으로, 다른 국가들보다 현저히 앞서 있습니다.
    - 베트남과 콜롬비아도 주요 커피 수출국입니다.
    - 에티오피아와 우간다와 같은 몇몇 아프리카 국가들이 상위 20개 리스트에 두드러집니다.
    """, unsafe_allow_html=True)
else:  # 소비량
    st.markdown("""
    ### 소비 데이터에 대하여
    이 시각화는 커피 수입 소비량 기준 상위 20개 국가와 그들의 소비량을 보여줍니다.

    <br>

    ### 인사이트
    - 미국이 커피 수입 소비량에서 다른 국가들보다 현저히 앞서 있습니다.
    - 독일, 이탈리아, 프랑스와 같은 유럽 국가들이 주요 커피 소비국입니다.
    - 일본은 아시아에서 주요 커피 소비국으로 두드러집니다.
    - 이 데이터는 이러한 국가들의 인구 규모와 커피 음용 문화를 반영합니다.
    """, unsafe_allow_html=True)

st.markdown("전 세계 커피 무역, 생산 및 소비에 대한 추가 정보를 원하시면 [국제 커피 기구](https://www.ico.org/)를 방문하세요.")

# 푸터
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit and Plotly")