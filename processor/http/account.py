from dataclasses import dataclass
import base64
from fastapi import Form, File, UploadFile
from fastapi import APIRouter, responses, Depends
from pydantic import BaseModel
import os
from security import encode_jwt, verify_password, hash_password
from middleware.envelope import enveloped
from middleware.headers import get_auth_token
import persistence.database as db
import exceptions as exc
import uuid

from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

router = APIRouter(
    tags=['Account'],
    default_response_class=responses.JSONResponse,
    dependencies=[Depends(get_auth_token)]
)


class AddAccountInput(BaseModel):
    username: str
    password: str
    pub_key: UploadFile = File(...)
    

@dataclass
class AddAccountOutput:
    id: uuid.UUID


@router.post('/account')
@enveloped
async def add_account(username: str = Form(...),
                      password: str = Form(...),
                      pub_key: UploadFile = File(...)):
    print("username:", username)
    print("password:", password)
    print("pub_key filename:", pub_key.filename)
    print("pub_key content type:", pub_key.content_type)
    pub_key_origin = await pub_key.read()
    print("pub_key file:", pub_key_origin)
    
    pub_key_str = pub_key_origin.decode('utf-8')
    # Load the public key from the string
    pub_key = serialization.load_pem_public_key(pub_key_str.encode(), backend=default_backend())

    # Serialize the public key to PEM-encoded string
    pub_key_pem = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # Encode the PEM-encoded bytes as a base64 string
    pub_key_base64 = base64.b64encode(pub_key_pem).decode('utf-8')

    # Print the base64-encoded public key
    print(pub_key_base64)
    
    # Testing the public key
    await test_encrypt(pub_key_base64)
    
    if await db.account.is_duplicate_username(username=username):
        raise exc.DuplicateUsername

    account_id = await db.account.add(username=username,
                                      password=hash_password(password),
                                      pub_key=pub_key_base64)

    return AddAccountOutput(id=account_id)


class LoginInput(BaseModel):
    username: str
    password: str


@dataclass
class LoginOutput:
    account_id: str
    token: str


@router.post('/login')
@enveloped
async def login(data: LoginInput) -> LoginOutput:
    try:
        account_id, pass_hash = await db.account.read_by_username(data.username)
    except TypeError:
        raise exc.LoginFailed

    if not verify_password(data.password, pass_hash):
        raise exc.LoginFailed

    token = encode_jwt(account_id=account_id)
    return LoginOutput(account_id=account_id, token=token)


async def test_encrypt(pub_key_base64):
    # Decode the base64-encoded public key string to a bytes object
    pub_key_bytes = base64.b64decode(pub_key_base64)

    # Load the public key from the bytes object
    pub_key = serialization.load_pem_public_key(pub_key_bytes, backend=default_backend())

    # Create random file
    file_bytes = os.urandom(32)

    # Encrypt the file using the public key
    encrypted = pub_key.encrypt(file_bytes, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

    # Print the encrypted message
    print(f"Encrypted: {str(encrypted)}")