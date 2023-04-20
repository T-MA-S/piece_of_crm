from storages.backends.s3boto3 import S3Boto3Storage

from SalesTech.settings import BUCKET_NAME


class MediaStorage(S3Boto3Storage):
    location = 'media'
    bucket_name = BUCKET_NAME


class StaticStorage(S3Boto3Storage):
    location = 'static'
    bucket_name = 'sales-tech-static'
