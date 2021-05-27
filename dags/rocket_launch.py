import json
import pathlib

import airflow
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="download_rocket_launches",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval=None,
)
download_launches = BashOperator(
    task_id="download_launches",
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'", dag=dag,
)
def _get_pictures():
    #Ensure directory exists and creates a directory if it doesn't exist
    pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True)

    #Download all pictures in launches.json
    with open("/tmp/launches.json") as f:  #Open the result from the previous task
        launches = json.load(f)            #Read as a dictionary
        images_urls = [launch["image"] for launch in launches["results"]] #For every launch fetch the element image
        for image_url in images_urls:       #Loop over all image URLs
            try:
                response = requests.get(image_url)   #Download each image           
                #Get only the filename. https://host/RocketImages/Electron.jpg -> Electron.jpg
                image_filename = image_url.split("/")[-1]  
                #Construct the target file path
                target_file = f"/tmp/images/{image_filename}"
                with open(target_file, "wb") as f:   #Open target file handle  
                    f.write(response.content)        #Write image to file path
                print (f"Downloaded {image_url} to {target_file}") #Print to stdout
            except requests_exceptions.MissingSchema:
                print(f"{image_url} appears to be an invalid URL.")
            except request_exceptions.ConnectionError:
                print(f"Could not connect to {image_url}.")
get_pictures = PythonOperator(
    task_id="get_pictures",
    python_callable=_get_pictures,
    dag=dag,
)
notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    dag=dag,
)

download_launches >> get_pictures >> notify

#download_launches.set_downstream(get_pictures)
#get pictures.set_downstream(notify)