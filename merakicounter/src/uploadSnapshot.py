import boto3
from botocore.exceptions import ClientError
import schedule
import time
import datetime

def uploadS3():
    #setup the bucket
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file('snapshot.png', 'labnatanteltec','snapshot.png', ExtraArgs={'ACL':'public-read'})
    except ClientError as e:
        logging.error(e)
        return False

    #Definindo Tempo
    currentDt = datetime.datetime.now()

    print ("Upload Realizado", currentDt.strftime("%d-%m-%Y %H:%M:%S"))

uploadS3()

#schedulando
schedule.every(10).seconds.do(uploadS3)

while 1:
    schedule.run_pending()
    time.sleep(1)