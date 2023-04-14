from dataclasses import dataclass
from fastapi import Form
from fastapi import APIRouter, responses, Depends
from pydantic import BaseModel

from middleware.envelope import enveloped
from middleware.headers import get_auth_token
import persistence.database as db
import exceptions as exc
import uuid

router = APIRouter(
    tags=['Files'],
    default_response_class=responses.JSONResponse,
    dependencies=[Depends(get_auth_token)]
)


class AddFileInput(BaseModel):
    user_id: str
    file_id: str
    

@dataclass
class AddFileOutput:
    id: uuid.UUID


@router.post('/file')
@enveloped
async def add_file(user_id: str = Form(...),
                     file_id: str = Form(...)):
    print("user_id:", user_id)
    print("file_id:", file_id)
    
    if await db.file.is_duplicate_file_id(file_id=file_id):
        raise exc.DuplicateFileId
    
    file_id = await db.file.add(user_id=user_id,
                                        file_id=file_id)
    
    return AddFileOutput(id=file_id)