
import boto3
import os
import logging
import tempfile
from botocore.exceptions import ClientError
import json
import contextlib
from multiprocessing import Pool
import time

server_token="notsecured"   # todo: change it to get from env
sleep_time=30
sqs_client = boto3.client("sqs",
    region_name="us-east-1",#os.environ.get('AWS_DEFAULT_REGION'),
    endpoint_url="http://localhost.localstack.cloud:4566",#os.environ.get('AWS_ENDPOINT'),
    aws_access_key_id="test", #os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key="test")#os.environ.get('AWS_SECRET_ACCESS_KEY'))
queue_url = sqs_client.get_queue_url(
        QueueName="checkpoint-SQS",
    )["QueueUrl"]
s3_client = boto3.client("s3",
    region_name="us-east-1",#os.environ.get('AWS_DEFAULT_REGION'),
    endpoint_url="http://localhost.localstack.cloud:4566",#os.environ.get('AWS_ENDPOINT'),
    aws_access_key_id="test", #os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key="test")#os.environ.get('AWS_SECRET_ACCESS_KEY'))
bucket_name="checkpoint-s3"

#This function read messages from sqs in bulk of 5, then for each message it create a new process and handle it 
def read_messages_from_sqs():
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=5
    )
    try:
        response["Messages"]
        with Pool(5) as p:
            p.map(manage_message,response["Messages"])
        return True
    except:
        return False


#This function handle a message first it upload to s3 and then delete it from sqs
def manage_message(message):
    try:
        upload_message_to_s3(message)
        delete_message_from_sqs(message)
    except:
        return False
    return True

#This function delete a message from sqs
def delete_message_from_sqs(message):
    response = sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message["ReceiptHandle"]
    ) 
#This function upload the message as new object in s3 with name of md5, It uses tempfile to create a temporary file and delete it at the end     
def upload_message_to_s3(message):
    tfile=tempfile.NamedTemporaryFile(mode='w',dir=os.getcwd(), suffix=".tmp.json", delete=False)
    tf_name=tfile.name
    json.dump(json.loads(message["Body"]), tfile)
    tfile.close()
    upload_file_to_s3(file_name=tfile.name, bucket=bucket_name, object_name=message["MD5OfBody"])
    with contextlib.suppress(FileNotFoundError):
        os.remove(tf_name)

# this function get a file and upload it s3
def upload_file_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    
    """this loop checks if there were messages in sqs, 
       handles them, then checks to see if there are still massages in the SQS
       if there no messages in the SQS it goes to sleep
    """
    while True:
        any_messages=read_messages_from_sqs()
        if any_messages==True:
            logging.info("handeled messages")
            continue
        else:
            logging.info(f"sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
            