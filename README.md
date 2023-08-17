# ПРОДУКТОВЫЙ ПОМОЩНИК

## ОПИСАНИЕ
«Продуктовый помощник» - сайт, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. 

### ОСОБЕННОСТИ
Проект запускается, как сеть контейнеров Docker

### ЭНДПОИНТЫ
| Маршрут | HTTP методы | Описание |
|:---|:---|:---|
| `/api/auth/token/login/` | `POST` | вход в систему, получение токена |
| `/api/auth/token/logout/` | `POST` | выход из системы, удаление токена |
| `/api/users/` | `GET`, `POST` | получение списка учетных записей пользователей и создание учетной записи пользователя |
| `/api/users/{id}/` | `GET` | получение учетной записи пользователя |
| `/api/users/me/` | `GET` | получение данных учетной записи текущего пользователя |
| `/api/users/set_password/` | `POST` | изменение пароля учетной записи текущего пользователя |
| `/api/users/subscriptions/` | `GET` | получение списка подписок текущего пользователя |
| `/api/users/{id}/subscribe/` | `POST`, `DELETE` | создание, удаление подписки текущего пользователя |
| `/api/tags/` | `GET` | получение списка тэгов |
| `/api/tags/{id}` | `GET` | получение тэга |
| `/api/ingredients/` | `GET` | получене списка ингредиентов |
| `/api/ingredients/{id}/` | `GET` | получение ингредиента |
| `/api/recipes/` | `GET`, `POST` | получние списка и создание рецепта |
| `/api/recipes/{id}/` | `GET`, `PATCH`, `DELETE` | получение, изменениеб удаление рецепта |
| `/api/recipes/{id}/favorite/` | `POST`, `DELETE` | добавление, удаление рецепта из списка "избанное" текущего пользователя |
| `/api/recipes/{id}/shopping_cart/` | `POST`, `DELETE` | добавление, удаление рецепта из списка покупок текущего пользователя |
| `/api/recipes/download_shopping_cart/` | `GET` | загрузка файла со списком покупок для текущего пользователя |

## ЗАПУСК ПРОЕКТА
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/monteg179/foodgram-project-react.git
cd foodgram-project-react
```
Создать образы и запустить контейнеры Docker:
```
sudo bash setup.sh install
```

## ИСПОЛЬЗОВАНИЕ API

### РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
```
POST http://localhost:9000/api/users/ HTTP/1.1
content-type: application/json

{
    "username": str,
    "email": str,
    "password": str,
    "first_name": str,
    "last_name": str
}
```

### ИЗМЕНЕНИЕ ПАРОЛЯ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
```
POST http://localhost:9000/api/users/set_password/ HTTP/1.1
Authorization: Token <token>
content-type: application/json

{
    "current_password": str,
    "new_password": str"
}
```

### АУДЕНТИФИКАЦИЯ ПОЛЬЗОВАТЕЛЯ
```
POST http://localhost:9000/api/auth/token/login/ HTTP/1.1
content-type: application/json

{
    "email": str,
    "password": str
}
```

### ПОЛУЧЕНИЕ СПИСКА РЕЦЕПТОВ
```
GET http://localhost:9000/api/recipes/ HTTP/1.1
```

### СОЗДАНИЕ РЕЦЕПТА
```
POST http://localhost:9000/api/recipes/ HTTP/1.1
Authorization: Token <token>
content-type: application/json

{
    "name": str,
    "text": str,
    "image": str,
    "cooking_time": int,
    "tags": [int,int],
    "ingredients": [
        {"id": int, "amount": int},
        {"id": int, "amount": int}
    ]
}
```

### ДОБАВЛЕНИЕ РЕЦЕПТА В "ИЗБРАННОЕ" ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
```
POST http://localhost:9000/api/recipes/111/favorite/ HTTP/1.1
Authorization: Token <token>
```

### ДОБАВЛЕНИЕ РЕЦЕПТА В СПИСОК ПОКУПОК ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
```
POST http://localhost:9000/api/recipes/11/shopping_cart/ HTTP/1.1
Authorization: Token <token>
```

### ПОЛУЧЕНИЕ СПИСКА ПОДПИСОК ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
```
GET http://localhost:9000/api/users/subscriptions/ HTTP/1.1
Authorization: Token <token>
```

### СОЗДАНИЕ ПОДПИСКИ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ
```
POST http://localhost:9000/api/users/103/subscribe/ HTTP/1.1
Authorization: Token <token>
```

## ИСПОЛЬЗОВАННЫЕ ТЕХНОЛОГИИ
- Python 3.9
- Django 3.2
- Django REST Framework 3.14
- Postgres
- Nginx
- Docker
- GitGub Actions

## АВТОРЫ
* Сергей Кузнецов - monteg179@yandex.ru

## ДОСТУП

### СЕРВЕР
monteg179.chickenkiller.com

### АДМИНКА
| username | пароль |
|:---|:---|
| `admin1` | `vjyntu` |
