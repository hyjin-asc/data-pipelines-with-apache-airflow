import json
import pathlib
import random

import airflow.utils.dates
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG( # 객체의 인스턴스 생성
    dag_id="download_rocket_launches", # Airflow UI에 표시되는 DAG 이름
    description="Download rocket pictures of recently launched rockets.",
    start_date=airflow.utils.dates.days_ago(14), # 워크플로가 처음 실행되는 날짜/시간
    schedule_interval="@daily", # DAG 실행 간격
)

download_launches = BashOperator( # BashOperator를 이용해 curl로 URL 결과값 다운로드
    task_id="download_launches", # 태스크 이름
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",  # noqa: E501
    dag=dag,
)

# 파이썬 함수는 결괏값을 파싱하고 모든 로켓 사진을 다운로드
def _get_pictures():
    if random.randint(0, 10) % 2:
        raise Exception()
    # 경로가 존재하는지 확인
    pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True)

    # launches.json 파일에 있는 모든 그림 파일을 다운로드
    with open("/tmp/launches.json") as f:
        launches = json.load(f)
        image_urls = [launch["image"] for launch in launches["results"]]
        for image_url in image_urls:
            try:
                response = requests.get(image_url)
                image_filename = image_url.split("/")[-1]
                target_file = f"/tmp/images/{image_filename}"
                with open(target_file, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded {image_url} to {target_file}") # Airflow 로그에 저장하기 위해 stdout으로 출력
            except requests_exceptions.MissingSchema:
                print(f"{image_url} appears to be an invalid URL.")
            except requests_exceptions.ConnectionError:
                print(f"Could not connect to {image_url}.")


get_pictures = PythonOperator( # DAG에서 PythonOperator를 사용하여 파이썬 함수 호출
    task_id="get_pictures", python_callable=_get_pictures, dag=dag
)

notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    dag=dag,
)

# 태스크 실행 순서 지정
download_launches >> get_pictures >> notify
