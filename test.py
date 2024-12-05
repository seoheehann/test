import panel as pn
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import hvplot.pandas

CSV_FILE = "C:/RESEARCH/Research/class/P-실무/data/ladybug_final.csv"

pn.extension("plotly", "tabulator", sizing_mode="stretch_width")

@pn.cache
def get_data():
    return pd.read_csv(CSV_FILE)

data = get_data()

############### 1. 무당이와 도보의 비율 및 수량 (파이 차트) ###############
mode_counts = data['transportation'].value_counts()

def create_pie_chart(counts):
    fig = go.Figure(data=[go.Pie(labels=counts.index, values=counts.values, hole=0.3)])
    fig.update_layout(title="무당이와 도보의 비율", template="plotly_dark", width=400, height=400)
    return fig

mode_ratio_chart = pn.pane.Plotly(create_pie_chart(mode_counts))

############### 2. 무당이와 도보 평균 통행 시간 ###############

# 사용자 정의 색상 설정
colors = {'ladybug': 'blue', 'foot': 'red'}

avg_time = data.copy()

avg_time['duration'] = avg_time.apply(
    lambda row: row['ladybug_total_duration'] if row['transportation'] == 'ladybug' else row['foot_total_duration'],
    axis=1
)

avg_time_chart_data = avg_time.groupby('transportation')['duration'].mean().reset_index()

# Plotly 막대 그래프 생성
fig = go.Figure()

# 막대 추가 (각 이동 방식에 대해)
for transport in ['ladybug', 'foot']:
    filtered_data = avg_time_chart_data[avg_time_chart_data['transportation'] == transport]
    fig.add_trace(
        go.Bar(
            x=filtered_data['transportation'],
            y=filtered_data['duration'],
            name=transport.capitalize(),  # 범례 이름 설정
            marker=dict(color=colors[transport])  # 색상 지정
        )
    )

# 레이아웃 설정
fig.update_layout(
    title="평균 통행 시간 (분)",
    xaxis=dict(title="이동 방식"),
    yaxis=dict(title="평균 통행 시간 (분)"),
    barmode='group',  # 막대를 그룹화
    legend=dict(title="Transportation", x=1.05, y=1),  # 범례 위치 및 제목 설정
    template='plotly_dark',  # 다크 테마
    width=400,
    height=400
)

# Panel에서 사용하기 위한 Plotly Pane 생성
avg_time_chart = pn.pane.Plotly(fig)

############### 3. 무당이와 도보 평균 통행 거리 비교 ###############
avg_distance = data.copy()

# 이동 속도 (m/min)
foot_speed_m_min = 5 * (1000 / 60)  # 도보 속도
ladybug_speed_m_min = 17 * (1000 / 60)  # 무당벌레 속도

# 거리 계산 (미터 단위로 변환)
avg_distance['distance'] = avg_distance.apply(
    lambda row: row['ladybug_total_duration'] * ladybug_speed_m_min
    if row['transportation'] == 'ladybug'
    else row['foot_total_duration'] * foot_speed_m_min,
    axis=1
)

avg_distance_chart_data = avg_distance.groupby('transportation')['distance'].mean().reset_index()

# Plotly 막대 그래프 생성
fig = go.Figure()

# 막대 추가 (각 이동 방식에 대해)
for transport, color in zip(['ladybug', 'foot'], ['blue', 'red']):
    filtered_data = avg_distance_chart_data[avg_distance_chart_data['transportation'] == transport]
    fig.add_trace(
        go.Bar(
            x=filtered_data['transportation'],
            y=filtered_data['distance'],
            name=transport.capitalize(),  # 범례 이름 설정
            marker=dict(color=color)  # 색상 지정
        )
    )

# 레이아웃 설정
fig.update_layout(
    title="평균 통행 거리 (m)",
    xaxis=dict(title="이동 방식"),
    yaxis=dict(title="평균 통행 거리 (m)"),
    barmode='group',  # 막대를 그룹화
    template='plotly_dark',  # 다크 테마
    width=400,
    height=400
)

# Panel에서 사용하기 위한 Plotly Pane 생성
avg_distance_chart = pn.pane.Plotly(fig)

############### 4. 시간별 인원수 계산 ###############
data['hour'] = data['start_time'].apply(lambda x: int(x // 60))
hourly_count = data.groupby('hour').size().reset_index(name='count')

# Plotly 선 그래프 생성
fig = go.Figure()

# 선 그래프 추가
fig.add_trace(
    go.Scatter(
        x=hourly_count['hour'],
        y=hourly_count['count'],
        mode='lines',  # 선 그래프
        line=dict(color='blue', width=2),  # 선 색상과 두께
        name='Line'
    )
)

# 산점도 추가
fig.add_trace(
    go.Scatter(
        x=hourly_count['hour'],
        y=hourly_count['count'],
        mode='markers',  # 점만 표시
        marker=dict(color='red', size=10),  # 점 색상과 크기
        name='Scatter'
    )
)

# 레이아웃 설정
fig.update_layout(
    title="시간별 인원수",
    xaxis=dict(title="시간대 (시)", range=[9, 18]),  # x축 범위 설정
    yaxis=dict(title="인원수"),
    template='plotly_dark',  # 다크 테마
    width=400,
    height=400
)

# Panel에서 사용하기 위한 Plotly Pane 생성
hourly_count_chart = pn.pane.Plotly(fig)

############### 5. 데이터 테이블
data_table = pn.widgets.Tabulator(
    data,
    pagination="remote",
    page_size=6,
    layout="fit_data_fill"
)

#################################################
ACCENT = "#BB2649"
RED = "#D94467"
GREEN = "#5AD534"
############### 대시보드 생성 함수 ###############
def create_dashboard():
    grid = pn.GridSpec(sizing_mode='scale_both', max_width=1200)
    grid[0:3, 0:3] = mode_ratio_chart
    grid[0:3, 3:6] = hourly_count_chart
    grid[0:3, 6:9] = avg_distance_chart
    grid[0:3, 9:12] = avg_time_chart
    grid[3:5, :] = data_table

    dashboard = pn.template.FastGridTemplate(
        title="무당이 대시보드",
        accent_base_color=ACCENT,
        header_background=ACCENT,
        prevent_collision=True,
        save_layout=True,
        theme_toggle=False,
        theme='dark',
        main=grid,
    )

    return dashboard

############### 대시보드 실행
dashboard = create_dashboard()
dashboard.servable()


# panel serve test.py --show --dev