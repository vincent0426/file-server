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

## Generate RSA keys

```shell
openssl genrsa -out private_key.pem 2048

openssl rsa -in private_key.pem -pubout -out public_key.pem

# you should see private_key.pem and public_key.pem
ls
```

## Docker

```shell
docker compose up

docker compose down

# rebuild
docker compose up --build
```
