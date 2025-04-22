### Social Message Viewer
Цей проект дозволяє переглядати повідомлення з Telegram через інтеграцію з API та відображати їх на веб-сторінці.

### Запуск проекту
- Клонуйте репозиторій на свій локальний комп'ютер:

```
git clone git@github.com:legobpc/social-msg-viewer.git
cd social-msg-viewer
```

### Налаштування змінних середовища
Перед тим, як запускати проект, вам потрібно налаштувати середовище

```
cp /backend/.env.secret.example /backend/.env.secret
cp /backend/.env.example /backend/.env
cp /frontend/.env.example /frontend/.env
```

Відредагуйте файл ```/backend/.env.secret``` та внесіть ваші власні дані, зокрема:

- API_ID — ваш Telegram API ID.
- API_HASH — ваш Telegram API Hash.
- PHONE — ваш номер телефону для Telegram.
- TG_PASSWORD — ваш Telegram пароль, якщо включена двофакторна аутентифікація.

Також, налаштуйте порти у файлах:
```
.env
backend/.env
frontend/.env
```

### Запуск проекту
Після налаштування всіх змінних середовища, запустіть проект за допомогою Docker:

```
docker-compose up --build
```
Ця команда збере та запустить ваш проект, використовуючи Docker.

### Доступ до проекту
Після запуску проекту ви зможете звертатися до нього через браузер, наприклад:
- Frontend: http://localhost:3000/
- Backend: http://localhost:8000/

### Admin
```
admin@example.com
admin
```