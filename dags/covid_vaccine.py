import json
import pathlib

import airflow
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.operators.email_operator import EmailOperator

dag = DAG(
    dag_id="vaccine_details",
    start_date=airflow.utils.dates.days_ago(2),
    schedule_interval=None,
)
download_vaccine_details = BashOperator(
    task_id="download_vaccine_details",
    bash_command="curl -X GET 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=263601&date=17-05-2021' -H  'accept: application/json' | jq >> /tmp/vaccine.json",
    dag=dag, 
)
notify_user = BashOperator(
    task_id="notify_user",
    bash_command='cat /tmp/vaccine.json',
    dag=dag,
)
email = EmailOperator(
        task_id='send_email',
        to='vidushi.bansal@knoldus.com',
        subject='Vaccine Updates in your area',
        html_content=""" <h3>Vaccine updates in your area</h3> """,
        files=['/tmp/vaccine.json'],
        dag=dag
)

download_vaccine_details >> notify_user >> email