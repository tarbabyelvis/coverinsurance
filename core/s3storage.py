import logging
import boto3
from storages.backends.s3boto3 import S3Boto3Storage

from FinCover import settings

logger = logging.getLogger(__name__)

aws_bucket_name = settings.FINCOVER_AWS_S3_STORAGE_BUCKET_NAME
aws_access_key_id = settings.AWS_S3_ACCESS_KEY_ID
aws_secret_access_key = settings.AWS_S3_SECRET_ACCESS_KEY
region_name = settings.AWS_S3_REGION_NAME
boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
s3 = boto3.resource('s3')


class S3MediaStorage(S3Boto3Storage):
    bucket_name = settings.FINCOVER_AWS_S3_STORAGE_BUCKET_NAME


def upload_file(file_name, file):
    try:
        s3object = s3.Object(aws_bucket_name, file_name)
        s3object.put(Body=file, Key=file_name)
        logger.info("File with file name {file_name} is successfully uploaded to S3 bucket {bucket_name}"
                    .format(file_name=file_name, bucket_name=aws_bucket_name))
        return True
    except Exception as ex:
        logger.error("Failed to upload file {file_name} to AWS S3 bucket {bucket_name}"
                     .format(file_name=file_name, bucket_name=aws_bucket_name), ex)
        return False


def download_file(file_name):
    try:
        file_name = file_name.name
        print("---------------File path---------------")
        print(file_name)
        print("================================")
        file_name = file_name if file_name is not None else "No file found"
        file_path = file_name.replace(" ", "_")
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=aws_bucket_name, Key=file_name)
        file_content = response['Body'].read()
        print("File content:")
        print(file_content)

        # downloaded = s3.Bucket(aws_bucket_name).download_file(file_name,"/upoads")
        # logger.info("File with file name {file_name} is successfully downloaded from S3 bucket {bucket_name}"
        #             .format(file_name=file_path, bucket_name=aws_bucket_name))
        return file_content,file_name
    except Exception as ex:
        logger.error("Failed to download file {file_name} from AWS S3 bucket {bucket_name}"
                     .format(file_name=file_name, bucket_name=aws_bucket_name), ex)
        return ex


def create_pre_signed_url(file_name):
    try:
        file_name = file_name if file_name is not None else "No file found"
        file_path = file_name.replace(" ", "_")
        absolute_url = boto3.client('s3').generate_presigned_url('get_object', ExpiresIn=3600,
                                                                 Params={'Bucket': aws_bucket_name, 'Key': file_path})
        logger.info(
            "Pre-signed URL for file name {file_name} is successfully generated from S3 bucket {bucket_name}".format(
                file_name=file_path, bucket_name=aws_bucket_name))
        return absolute_url
    except Exception as ex:
        logger.error("Failed to generate S3 URL for file {file_name} from AWS S3 bucket {bucket_name}"
                     .format(file_name=file_name, bucket_name=aws_bucket_name), ex)
        return ex
