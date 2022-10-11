from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="01_unscheduled", start_date=datetime(2019, 1, 1), schedule_interval=None # 스케줄되지 않는 DAG으로 지정
)

fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data/events && "
        "curl -o /data/events.json http://events_api:5000/events" # API에서 이벤트를 가져온 후 저장
    ),
    dag=dag,
)


def _calculate_stats(input_path, output_path):
    """이벤트 통계 계산하기"""

    Path(output_path).parent.mkdir(exist_ok=True)

    # 이벤트 데이터 로드하고 필요한 통계 계산
    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    # 결과 csv로 저장
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={"input_path": "/data/events.json", "output_path": "/data/stats.csv"},
    dag=dag,
)

# 태스크 실행 순서 지정
fetch_events >> calculate_stats
