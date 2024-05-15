
import boto3
import os
import logging
from botocore.exceptions import ClientError

server_token="notsecured"   # todo: change it to get from env

sqs_client = boto3.client("sqs",
    region_name="us-east-1",#os.environ.get('AWS_DEFAULT_REGION'),
    endpoint_url="http://localhost:4566",#os.environ.get('AWS_ENDPOINT'),
    aws_access_key_id="my_access_key", #os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key="my_secret_key")#os.environ.get('AWS_SECRET_ACCESS_KEY'))
queue_url = sqs_client.get_queue_url(
        QueueName="checkpoint-SQS",
    )["QueueUrl"]

s3_client = boto3.client("s3",
    region_name="us-east-1",#os.environ.get('AWS_DEFAULT_REGION'),
    endpoint_url="http://localhost:4566",#os.environ.get('AWS_ENDPOINT'),
    aws_access_key_id="my_access_key", #os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key="my_secret_key")#os.environ.get('AWS_SECRET_ACCESS_KEY'))

bucket_name="checkpoint-s3"

def read_message_from_sqs():
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=2
    )




    
def upload_message_to_s3(message):
    pass



def upload_file_tos3(file_name, bucket, object_name=None):
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
    read_message_from_sqs()