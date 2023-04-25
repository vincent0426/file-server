from dataclasses import dataclass
from fastapi import UploadFile, File
from fastapi import APIRouter, responses, Depends
from pydantic import BaseModel

from middleware.envelope import enveloped
from middleware.headers import get_auth_token
import persistence.database as db
from persistence.s3 import s3_handler
import exceptions as exc
import uuid

from starlette_context import context

router = APIRouter(
    tags=['Transaction'],
    default_response_class=responses.JSONResponse,
    dependencies=[Depends(get_auth_token)]
)

# Add Transaction
class AddTransactionInput(BaseModel):
    file_id: uuid.UUID
    from_uid: uuid.UUID
    to_uid: uuid.UUID

@dataclass
class AddTransactionOutput:
    id: uuid.UUID


@router.post('/transaction')
@enveloped
async def add_transaction(file_id: uuid.UUID,
                           to_uid: uuid.UUID) -> AddTransactionOutput:
    print(f'PostTransactionInput: {file_id}')
    account = context['account']
    transaction_id = await db.transaction.add(file_id, account.id, to_uid)
    print(f'PostTransactionOutput: {transaction_id}')
    return AddTransactionOutput(id=transaction_id)


@dataclass
class GetTransactionsOutput:
    transactions: list
    
@router.get('/transactions')
@enveloped
async def get_transactions() -> GetTransactionsOutput:
    account = context['account']
    print(f'GetTransactionsInput: {account.id}')
    transactions = await db.transaction.get_all(account.id)
    print(f'GetTransactionsOutput: {transactions}')
    return GetTransactionsOutput(transactions=transactions)
