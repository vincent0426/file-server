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
    tags=['PubKey'],
    default_response_class=responses.JSONResponse,
    dependencies=[Depends(get_auth_token)]
)

# Get Public Key by UserID
class GetPubKeyInput(BaseModel):
    uid: str

@dataclass
class GetPubKeyOutput:
    pub_key: str


@router.get('/pub_key/{uid}')
@enveloped
async def get_pub_key(uid: str) -> GetPubKeyOutput:
    print(f'GetPubKeyInput: {uid}')
    
    pub_key = await db.pub_key.get_by_uid(uid)
    
    return GetPubKeyOutput(pub_key=pub_key)
    