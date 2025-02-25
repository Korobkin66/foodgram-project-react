### praktikum_new_diplom

```https://korpraktikum.ddns.net/```

#  Foodgram
Cервис предоставляющий пользователям возможность публиковать рецепты, подписываться на других пользователей, добавлять любимые рецепты в список "Избранное" и скачивать список продуктов перед походом в магазин для приготовления выбранных блюд. 

## Пользовательские возможности:

Регистрация.
Авторизация.
Просмотр рецептов других пользователей.
Создание, редактирование и удаление рецептов.
Подписка на авторов. 
Добавление рецептов в избранное.
Просмотр необходимого количества ингридиентов для выбранных рецептов и скачивание этого списка.

## Стек технологий:

Python, Django, Django REST Framework, PostgresQL, Docker

## Как запустить проект:

### Клонировать репозиторий:

```bash
git clone https://github.com/Korobkin66/foodgram-project-react.git
```

### Для работы workflow необходимо добавить переменные окружения в Secrets GitHub:

```makefile
ALLOWED_HOSTS=<Список доменных имен или IP-адресов, которые Django разрешает для обработки запросов>
DB_ENGINE=<Движок базы данных, который будет использоваться>
DB_HOST=<Хост базы данных>
DB_PORT=<Порт для подключения к базе данных>
DOCKER_PASSWORD=<пароль DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>
HOST=<ip-адрес сервера>
POSTGRES_DB=<Название базы данных PostgreSQL>
POSTGRES_PASSWORD=<Пароль для пользователя PostgreSQL>
POSTGRES_USER=<Имя пользователя PostgreSQL>
SECRET_KEY=<Секретный ключ Django>
SSH_KEY=<SSH-ключ (для получения команды: cat ~/.ssh/id_rsa)>
SSH_PASSPHRASE=<пароль для сервера (если установлен)>
USER=<username для подключения к удаленному серверу>
```