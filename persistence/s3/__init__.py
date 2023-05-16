import aioboto3
import typing
from uuid import UUID

from base import mcs
from config import S3Config
import exceptions as exc

import io

class S3Handler(metaclass=mcs.Singleton):
    def __init__(self):
        self._session = aioboto3.Session()
        self._client = None
        self._resource = None

    async def initialize(self, s3_config: S3Config):
        self._client = await self._session.client(
            's3',
            endpoint_url=s3_config.endpoint,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region
        ).__aenter__()

        self._resource = await self._session.resource(
            's3',
            endpoint_url=s3_config.endpoint,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region
        ).__aenter__()

    async def close(self):
        await self._client.close()
        await self._resource.close()

    async def sign_url(self, bucket_name: str, key: str, filename: str) -> str:
        try:
            # check if the object exists
            await self._client.head_object(Bucket=bucket_name, Key=key)
        except Exception as e:
            if e.response['Error']['Code'] == '404':
                raise exc.NotFound
            else:
                raise exc.InternalServerError
        return await self._client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ResponseContentDisposition': f"attachment; filename={filename};"
            },
            ExpiresIn=3600,
        )

    async def upload(self, file: typing.IO, key: UUID, bucket_name: str):
        bucket = await self._resource.Bucket(bucket_name)
        await bucket.upload_fileobj(file, str(key))
        
    async def download(self, key: str, bucket_name: str) -> bytes:
        file_obj = io.BytesIO()
        await self._client.download_fileobj(bucket_name, key, file_obj)
        return file_obj.getvalue()


s3_handler = S3Handler()
