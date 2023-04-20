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
    

@dataclass
class AddFileOutput:
    id: uuid.UUID

@router.post('/file')
@enveloped
async def add_file(file: UploadFile = File(...)):
    account = context['account']
    file_id = str(uuid.uuid4())
    await s3_handler.upload(file, file_id)
    return AddFileOutput(id=file_id)


# Get File from S3 with file_id and bucket_name
@router.get("/file/{file_id}")
async def get_file(file_id: uuid.UUID):
    obj_bytes = await s3_handler.download(key=str(file_id), bucket_name='files')

    # Write object bytes to your directory
    # if upload app.enc, we will get file_id in directory
    # we then add the suffix to the file_id
    # try with .png to see the image
    with open(f"{file_id}.enc", "wb") as f:
        f.write(obj_bytes)
    
    account = context['account']
    enc_sym = await s3_handler.download(key=f'{file_id}/{account.id}', bucket_name='enc-sym')
    with open(f"{file_id}-sym.enc", "wb") as f:
        f.write(enc_sym)
    