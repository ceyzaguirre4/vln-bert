import os
import sys
import threading
import boto3
from boto3.s3.transfer import TransferConfig

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
REGION_NAME = os.environ['REGION_NAME']
AWS_S3_ENDPOINT = os.environ['AWS_S3_ENDPOINT']
AWS_BUCKET_NAME = os.environ['AWS_BUCKET_NAME']


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


def upload_file_to_aws_s3(file_path, prefix=''):
    file_name = file_path.split('/')[-1]
    file_url = ''
    # get the connection of AWS S3 Bucket
    s3 = boto3.resource(
        's3',
        endpoint_url=f'https://{AWS_BUCKET_NAME}.{REGION_NAME}.{AWS_S3_ENDPOINT}',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
    )

    try:
        # Open the server file as read mode and upload in AWS S3 Bucket.
        data = open(file_path, 'rb')

        if prefix: file_name = os.path.join(prefix, file_name)
        s3.Bucket(AWS_BUCKET_NAME).put_object(
            Key=file_name,
            Body=data,
            # ContentType='image',
            ACL='public-read',
            )
        data.close()

        # Format the return URL of upload file in S3 Bucjet
        file_url = f'https://{AWS_BUCKET_NAME}.{REGION_NAME}.{AWS_S3_ENDPOINT}/{file_name}'
    except Exception as e:
        print("Error in file upload %s." % (str(e)))

    return file_url


def multipart_upload_file_to_aws_s3(file_path, prefix=''):
    file_name = file_path.split('/')[-1]

    s3_client = boto3.client(
        's3',
        endpoint_url=f'https://{AWS_BUCKET_NAME}.{REGION_NAME}.{AWS_S3_ENDPOINT}',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
        )

    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)

    if prefix: file_name = os.path.join(prefix, file_name)
    s3_client.upload_file(
        file_path, AWS_BUCKET_NAME, file_name,
        ExtraArgs={ 'ACL': 'public-read'},
        Config=config,
        # Callback=ProgressPercentage(file_path),
    )


def multipart_download_file_from_aws_s3(file_path, prefix=''):
    file_name = file_path.split('/')[-1]

    s3_client = boto3.client(
        's3',
        endpoint_url=f'https://{AWS_BUCKET_NAME}.{REGION_NAME}.{AWS_S3_ENDPOINT}',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
        )

    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)

    if prefix: file_name = os.path.join(prefix, file_name)
    with open(file_path, 'wb') as data:
        s3_client.download_fileobj(
            AWS_BUCKET_NAME,
            file_name,
            data,
            Config=config,
        )

if __name__ == '__main__':
    # download all files needed
    multipart_download_file_from_aws_s3('vilbert_pytorch_model_9.bin')
    multipart_download_file_from_aws_s3('pretrained_model.bin')
    multipart_download_file_from_aws_s3('multi_task_model.bin')
    multipart_download_file_from_aws_s3('matterport-ResNet-101-faster-rcnn-genome.lmdb.zip')
    multipart_download_file_from_aws_s3('data.zip')
