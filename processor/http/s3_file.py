from dataclasses import dataclass
from fastapi import Form, UploadFile, File
from fastapi import Request
from fastapi import APIRouter, responses, Depends
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from middleware.envelope import enveloped
from middleware.headers import get_auth_token
import persistence.database as db
from persistence.s3 import s3_handler
import exceptions as exc
import uuid
from base import do

from starlette_context import context

router = APIRouter(
    tags=['Files'],
    default_response_class=responses.JSONResponse,
    dependencies=[Depends(get_auth_token)]
)


class AddFileInput(BaseModel):
    file: UploadFile = File(...)
    bucket_name: str
    receiver_id: uuid.UUID = None
    

@dataclass
class AddFileOutput:
    id: uuid.UUID

@router.post('/file')
@enveloped
async def add_file(file: UploadFile = File(...), bucket_name: str = 'files', receiver_id: uuid.UUID = None):
    file_id = str(uuid.uuid4())
    key = str(file_id)
    
    if(bucket_name != 'files' and receiver_id is None):
        raise exc.BadRequestException("receiver_id is required for enc-sym files")
    
    if(bucket_name != 'files'):
        key = f"{file_id}/{receiver_id}"
        
    await s3_handler.upload(file, key=key, bucket_name=bucket_name)
    return AddFileOutput(id=file_id)


class GetFileInput(BaseModel):
    file_id: uuid.UUID
    bucket_name: str
    

@dataclass
class GetFileOutput:
    url: str
# Get File from S3 with file_id and bucket_name
@router.get("/file/{file_id}")
async def get_file(file_id: uuid.UUID, bucket_name: str = 'files'):
    account = context['account']
    
    filename = f"{file_id}.enc"
    key = str(file_id)
    
    if(bucket_name != 'files'):
        filename = f"{file_id}-sym.enc"
        key = f"{file_id}/{account.id}"
        
    sign_url = await s3_handler.sign_url(key=key, bucket_name='files', filename=filename)
    return GetFileOutput(url=sign_url)
    