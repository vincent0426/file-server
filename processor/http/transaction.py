from dataclasses import dataclass
from fastapi import UploadFile, File
from fastapi import APIRouter, responses, Depends
from fastapi import HTTPException
from pydantic import BaseModel

from middleware.envelope import enveloped
from middleware.headers import get_auth_token
import persistence.database as db
from persistence.s3 import s3_handler
import exceptions as exc
import uuid

from starlette_context import context

from config import S3Config

router = APIRouter(
    tags=['Transaction'],
    default_response_class=responses.JSONResponse,
    dependencies=[Depends(get_auth_token)]
)

# Add Transaction
class AddTransactionInput(BaseModel):
    to_uid: uuid.UUID
    file: UploadFile = File(...)
    enc_sym: UploadFile = File(...)

@dataclass
class AddTransactionOutput:
    id: uuid.UUID


@router.post('/transaction')
@enveloped
async def add_transaction(to_uid: uuid.UUID,
                            file: UploadFile = File(...),
                            enc_sym: UploadFile = File(...)) -> AddTransactionOutput:
    
    account = context['account']
    # If no account, raise 401
    if not account:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    fid = str(uuid.uuid4())
    key = str(fid)
    # Upload file to S3
    await s3_handler.upload(file, key=key, bucket_name=S3Config.files_bucket)
    # Upload encrypted symmetric key to S3
    await s3_handler.upload(enc_sym, key=key, bucket_name=S3Config.symmetric_keys_bucket)
    
    filename = file.filename
    transaction_id = await db.transaction.add(fid, filename, account.id, to_uid)
    return AddTransactionOutput(id=transaction_id)


@dataclass
class GetTransactionsOutput:
    transactions: list
    
@router.get('/transactions')
async def get_transactions() -> GetTransactionsOutput:
    account = context['account']
    # If no account, raise 401
    if not account:
        raise HTTPException(status_code=401, detail="Not authenticated")

    transactions = await db.transaction.get_all(account.id)
    return GetTransactionsOutput(transactions=transactions)


@dataclass
class GetTransactionOutput:
    transaction: dict
    
@router.get('/transaction/{transaction_id}')
async def get_transaction(transaction_id: uuid.UUID) -> GetTransactionOutput:
    account = context['account']
    # If no account, raise 401
    if not account:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Only the sender or receiver of the transaction can get the transaction
    if not await db.transaction.is_sender(transaction_id, account.id) and not await db.transaction.is_receiver(transaction_id, account.id):
        raise HTTPException(status_code=403, detail="No permission")

    transaction = await db.transaction.get(transaction_id)
    return GetTransactionOutput(transaction=transaction)
