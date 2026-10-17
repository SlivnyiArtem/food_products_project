# Food Shop API

API интернет-магазина продуктов на Django REST Framework.

## Функционал

- Создание, редактирование и удаление категорий и подкатегорий, а также продуктов через админку
- Добавление продукта пользователем в корзину
- Изменение количества продукта в корзине/удаление продукта
- Полная очистка корзины
- Вывод состава корзины с подсчётом количества товаров и общей суммы
- Авторизация по токену
- Swagger
- Автотесты (GET и POST)

## Технологии

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Pillow](https://pypi.org/project/pillow/)
- [pytest](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)

# Как запустить проект после установки:

# Клонировать репозиторий
bash ``` git clone <repo-url>```

## При необходимости активровать виртуальную среду

```
source venv/Scripts/activate
```

## Перейти в каталог backend (backend_test_project/food_shop/backend)

```
cd backend
```

## Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

## Собрать и запустить контейнер с <L

```
docker compose up --build -d
```

## Сделать миграции

```
python manage.py migrate
```

## Установить фикстуры

```
python manage.py loaddata data/fixtures.json
```

## Запустить проект локально
```
python manage.py runserver
```

## Запустить тесты

```
pytest
```

## Автор
- [flamberg](https://github.com/SlivnyiArtem)