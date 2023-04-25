```shell
conda create --name backend python=3.9
conda activate backend
pip install -r requirements.txt
cp .env.example .env
```

paste environment variables

```shell
pip install uvicorn
uvicorn main:app --reload
```

go to localhost:8000/docs and you will see backend swagger

## Docker

```shell
docker compose up

docker compose down

# rebuild
docker compose up --build
```

## Generate RSA keys

```shell
openssl genrsa -out private_key.pem 2048

openssl rsa -in private_key.pem -pubout -out public_key.pem

# you should see private_key.pem and public_key.pem
ls
```

## Example
1. Create two user A & B using POST /account
2. Login A using POST /login
3. Encrypt a file using pregenerated symmetric key
3. Upload the encrypt file using POST /file
4. Get the public key of B using GET /pub_key/{uid}
5. Encrypt the symmetric key using B's public key
6. Upload the encrypted symmetric key using POST /file (specify the bucket_name to enc-sym and receiver_id to B's uid)
7. Add the transaction using POST /transaction (need to upload the receiver's encrypted symmetric key)
8. Login B using POST /login
9. Get all the transaction using GET /transactions
10. Get both the symmetric key and the file using GET /file/{file_id}
11. Decrypt the symmetric key using B's private key
12. Decrypt the file using the symmetric key

