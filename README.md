# File Server
A file server implemented in Python, while the server doesn't know the content of the files.

## Set up
### Backend Server
1. Fill in the environment variables in the `.env` file.
    ```shell
    cp .env.example .env
    # Fill in variables
    ```
2. Start backend service.
    ```shell
    docker-compose up -d
    ```

### Client
**Note: Client CLI is in `client/`**

Client CLI is implemented in Python, and the program doesn't require any setup besides installing `prettytable` package and `openssl` are installed in your system environment, you may install it directly or in the environment you prefer, for example:
```shell
pip install prettytable
```
#### Usage:
1. Login / Register
    ```shell
    ./main
    ```
    1. If you haven't set up configuration in your local environment, you will be required to specify the configuration directory, default is set `~/.fileserver`
    2. Then you will be required to set up username and password, the configuration will be stored in configuration directory you assigned in step i.
2. Get your user id
    ```shell
    ./main --get-id
    ```
    1. If you want to provide your uuid to others for file transaction, you may get your user uuid through this command.
3. Upload file
    ```shell
    ./main --upload --user <user_uuid> <filepath>
    ```
    1. <user_uuid> is the receiver's user uuid, while filepath is the path of the file you want to send.
4. Download file
    ```shell
    ./main --download
    ```
    1. This command will show you all transactions that you receive, and you may enter the transaction uuid to retrieve the file.