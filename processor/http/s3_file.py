from dataclasses import dataclass
from fastapi import Form, UploadFile, File
from fastapi import Request
from fastapi import APIRouter, responses, Depends
from fastapi.responses import StreamingResponse
from fastapi import HTTPException

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
from config import AppConfig
from config import S3Config

router = APIRouter(
    tags=['Files'],
    default_response_class=responses.JSONResponse,
    dependencies=[Depends(get_auth_token)]
)


# class AddFileInput(BaseModel):
#     file: UploadFile = File(...)
    

# @dataclass
# class AddFileOutput:
#     id: uuid.UUID

# @router.post('/file')
# @enveloped
# async def add_file(file: UploadFile = File(...)):
#     file_id = str(uuid.uuid4())
#     key = str(file_id)
        
#     await s3_handler.upload(file, key=key)
#     return AddFileOutput(id=file_id)


class GetFileInput(BaseModel):
    file_id: uuid.UUID
    

@dataclass
class GetFileOutput:
    enc_file: str
    enc_sym: str

@router.get("/file/{file_id}")
async def get_file(file_id: uuid.UUID):
    account = context['account']
    # if no account, raise 401
    if not account:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Only the owner of the file can get the file
    if not await db.transaction.is_file_sender(file_id, account.id) and not await db.transaction.is_file_receiver(file_id, account.id):
        raise HTTPException(status_code=403, detail="No permission")
    
    
    filename = await db.transaction.get_filename(file_id)
    enc_sym_filename = f"{file_id}-sym.enc"
    key = str(file_id)
    
    try:
        file_sign_url = await s3_handler.sign_url(key=key, filename=filename, bucket_name=S3Config.files_bucket)
        enc_sym_sign_url = await s3_handler.sign_url(key=key, filename=enc_sym_filename, bucket_name=S3Config.symmetric_keys_bucket)
        # replace the first minio with the domain
        file_sign_url = file_sign_url.replace('minio', AppConfig.domain, 1)
        enc_sym_sign_url = enc_sym_sign_url.replace('minio', AppConfig.domain, 1)
    except exc.NotFound:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return GetFileOutput(enc_file=file_sign_url, enc_sym=enc_sym_sign_url)