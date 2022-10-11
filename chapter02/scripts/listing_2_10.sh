#!/bin/bash

# Note: 아래와 같이 하나의 도커 컨테이너 안에 여러 프로세스를 실행하는것은 예제를 위한 간단한 데모 환경을 위해서임
# 웹 서버, 스케줄러, 메타스토어를 별도 컨테이너에서 실행하는 프로덕션 상의 설정 방법은 10장에 나와있음

set -x

SCRIPT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

# -t: 터미널 -i: 상호작용
# -p: 호스트 포트:컨테이너 포트
# 컨테이너 8080 포트 개방한 뒤 호스트의 8080포트와 연결
# -v: 호스트 경로:컨테이너 내의 경로로 마운트
# 컨테이너에서 메타스토어 초기화 후 웹서버와 스케줄러 시작

docker run \
-ti \
-p 8060:8080 \
-v ${SCRIPT_DIR}/../dags/download_rocket_launches.py:/opt/airflow/dags/download_rocket_launches.py \
--name airflow \
--entrypoint=/bin/bash \
apache/airflow:2.0.0-python3.8 \
-c '( \
airflow db init && \
airflow users create --username admin --password admin --firstname Anonymous --lastname Admin --role Admin --email admin@example.org \
); \
airflow webserver & \
airflow scheduler \
'
