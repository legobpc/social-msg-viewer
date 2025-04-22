### Social Message Viewer
This project allows you to view messages from Telegram through API integration and display them on a web page.
It can be extended for additional features such as channel management, automated message processing, chat monitoring, or even building a custom Telegram dashboard for personal or administrative use.


### Project Launch
- Clone the repository to your local machine:

```
git clone git@github.com:legobpc/social-msg-viewer.git
cd social-msg-viewer
```

### Environment Variables Setup
Before running the project, you need to set up the environment:

```
cp /backend/.env.secret.example /backend/.env.secret
cp /backend/.env.example /backend/.env
cp /frontend/.env.example /frontend/.env
```

Edit the file `/backend/.env.secret` and provide your own data, including:

- SECRET_KEY — A secret key used for cryptographic operations.
- DATABASE_URL — The main database connection string. Defaults to SQLite. You can use another database, but some code adjustments may be required.
- TEST_DATABASE_URL — The test database connection string. Defaults to SQLite. Switching to another database may also require minor code changes.
- API_ID — Your Telegram API ID obtained from my.telegram.org.
- API_HASH — Your Telegram API Hash obtained from my.telegram.org.
- PHONE — The phone number linked to your Telegram account.
- TG_PASSWORD — Your Telegram account password (used if two-factor authentication is enabled).

Also, configure the ports in the following files:
```
.env
backend/.env
frontend/.env
```

### Running the Project
After setting up all environment variables, start the project using Docker:

```
docker-compose up --build
```
This command will build and launch your project using Docker.

### Accessing the Project
Once the project is running, you can access it in your browser, for example:
- Frontend: http://localhost:3000/
- Backend: http://localhost:8000/

### Admin
```
admin@example.com
admin
```

### Telegram API
- Go to the Telegram developer website:
```
https://my.telegram.org
```

- Log in with your phone number (the one linked to Telegram).
- Confirm the login using the code from Telegram.
- Go to the **API development tools** section.
- Create a new application.
- Retrieve your **API ID** and **API Hash**.