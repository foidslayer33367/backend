# Лабораторная работа № 2

HTTP-методы и CRUD-операции

Студент - Осипов Герман Юрьевич  
Группа - ПИЖ-б-о-25-2  
Вариант - 10  
Уровень - продвинутый  
Технологии - Python и Flask

## Содержание

- [Цель](#цель)
- [Теория](#теория)
- [Запуск](#запуск)
- [Практический пример](#практический-пример)
- [Индивидуальное задание](#индивидуальное-задание)
- [Проверка запросов](#проверка-запросов)
- [Контрольные вопросы](#контрольные-вопросы)
- [Вывод](#вывод)
- [Источники](#источники)

## Цель

Научиться обрабатывать GET, POST, PUT, PATCH и DELETE, выполнять операции над коллекцией объектов и возвращать соответствующие HTTP-статусы.

## Теория

CRUD включает создание, чтение, обновление и удаление данных. Данные хранятся в списке Python в памяти одного процесса. При перезапуске восстанавливаются исходные записи.

| Метод | Операция | Успешный ответ |
| --- | --- | --- |
| GET | Чтение | 200 |
| POST | Создание | 201 |
| PUT | Полная замена | 200 |
| PATCH | Частичное обновление | 200 |
| DELETE | Удаление | 204, в практическом примере 200 |

GET, PUT и DELETE идемпотентны по смыслу операции. Повторное удаление может вернуть 404, но состояние коллекции после него остаётся тем же. POST может создавать новую запись при каждом повторе. PATCH с присваиванием полей в этой работе тоже идемпотентен.

Ошибки входных данных возвращают 400, неизвестная запись или маршрут - 404, неподдерживаемый метод - 405, слишком большое тело - 413, непредвиденная ошибка сервера - 500.

## Запуск

В терминале из папки lab2-crud выполнить команды.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Основной сервер работает на http://127.0.0.1:3000. Для практического примера открыть второй терминал в той же папке.

```bash
source .venv/bin/activate
python example.py
```

Пример работает на http://127.0.0.1:3001. Первая лабораторная также использует порт 3000, поэтому перед запуском второй её сервер нужно остановить через Ctrl+C.

## Практический пример

Повторён пример из методички с товарами items. Реализованы список, чтение одной записи, создание, полная замена и удаление. Обязательны name и price, количество по умолчанию равно нулю. При удалении возвращаются сообщение и удалённая запись.

Код находится в [example.py](example.py).

```python
import math
from datetime import datetime

from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.json.ensure_ascii = False

items = [
    {"id": 1, "name": "Товар 1", "price": 100, "quantity": 5},
    {"id": 2, "name": "Товар 2", "price": 200, "quantity": 3},
    {"id": 3, "name": "Товар 3", "price": 300, "quantity": 10},
]
next_id = 4


@app.before_request
def log_request():
    timestamp = datetime.now().isoformat(timespec="seconds")
    print(f"[{timestamp}] {request.method} {request.path}", flush=True)



def find_item(item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    abort(404, description="Элемент не найден")


def read_item():
    if not request.is_json:
        abort(400, description="Нужно передать JSON")
    data = request.get_json()
    if not isinstance(data, dict):
        abort(400, description="Нужен объект JSON")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        abort(400, description="Поле name обязательно")
    price = data.get("price")
    if type(price) not in (int, float) or not 0 <= price <= 10**12 or not math.isfinite(price):
        abort(400, description="price должна быть неотрицательным числом")
    quantity = data.get("quantity", 0)
    if type(quantity) is not int or quantity < 0:
        abort(400, description="quantity должна быть неотрицательным целым числом")
    return {"name": data["name"].strip(), "price": data["price"], "quantity": quantity}


@app.get("/items")
def list_items():
    return jsonify(count=len(items), items=items)


@app.get("/items/<int:item_id>")
def get_item(item_id):
    return jsonify(find_item(item_id))


@app.post("/items")
def create_item():
    global next_id
    data = read_item()
    item = {"id": next_id, **data}
    next_id += 1
    items.append(item)
    return jsonify(item), 201


@app.put("/items/<int:item_id>")
def replace_item(item_id):
    item = find_item(item_id)
    data = read_item()
    item.clear()
    item.update(id=item_id, **data)
    return jsonify(item)


@app.delete("/items/<int:item_id>")
def delete_item(item_id):
    item = find_item(item_id)
    items.remove(item)
    return jsonify(message="Элемент удалён", deleted=item)


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.description), error.code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3001)
```

## Индивидуальное задание

Для варианта 10 реализована коллекция автомобилей. Поля записи - id, brand, model, year, price. Поиск выполняется по марке, статистика считает среднюю цену, связанные записи имеют ту же марку.

| Метод | Адрес | Назначение |
| --- | --- | --- |
| GET | /cars | Список, поиск, сортировка и пагинация |
| GET | /cars/ID | Автомобиль по ID |
| POST | /cars | Создание автомобиля |
| PUT | /cars/ID | Замена всех полей |
| PATCH | /cars/ID | Изменение переданных полей |
| DELETE | /cars/ID | Удаление автомобиля |
| DELETE | /cars | Удаление всей коллекции |
| POST | /cars/bulk | Создание от 1 до 100 автомобилей |
| GET | /cars/stats | Количество и средняя цена |
| GET | /cars/ID/related | Другие автомобили той же марки |

brand и model должны быть непустыми строками. year - целое число от 1886 до следующего года включительно. price - конечное число от 0 до 1000000000000. Нулевые цены допускаются. Передавать свой id нельзя.

Пример тела POST или PUT.

```json
{
  "brand": "Kia",
  "model": "Rio",
  "year": 2019,
  "price": 1400000
}
```

PUT требует все четыре поля. PATCH принимает непустой объект с любым набором этих полей. Неизвестные поля отклоняются.

Параметры списка можно объединять.

```text
/cars?search=toyota&sort=price&order=desc&page=1&limit=2
```

Сначала применяется поиск без учёта регистра, затем сортировка и пагинация. count показывает число найденных записей до разбивки на страницы. Можно сортировать по id, brand, model, year, price. По умолчанию используются id, asc, страница 1 и лимит 10. Лимит должен быть от 1 до 100.

Массовое создание принимает массив объектов. Сначала проверяется весь массив, затем добавляются все записи. Если хотя бы один объект ошибочный, коллекция и счётчик ID сохраняют прежнее состояние.

Счётчик ID только увеличивается. Массовое удаление его не сбрасывает. Доступ к списку и счётчику защищён блокировкой для параллельных запросов в одном процессе.

Каждый ответ записывается в access.log рядом с app.py. В строке журнала находятся время, HTTP-метод, путь с параметрами и статус. Файл создаётся при запуске. Ограничение тела запроса составляет 64 КиБ. Ошибки HTTP оформляются в JSON, глобальный обработчик непредвиденных ошибок возвращает 500.

Основной код находится в [app.py](app.py).

```python
import logging
import math
from datetime import datetime
from pathlib import Path
from threading import RLock

from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

cars = [
    {"id": 1, "brand": "Toyota", "model": "Corolla", "year": 2020, "price": 1800000},
    {"id": 2, "brand": "Toyota", "model": "Camry", "year": 2022, "price": 3200000},
    {"id": 3, "brand": "Lada", "model": "Vesta", "year": 2021, "price": 1200000},
]
next_id = 4
lock = RLock()

access_logger = logging.getLogger("lab2.access")
access_logger.setLevel(logging.INFO)
access_logger.propagate = False
if not access_logger.handlers:
    handler = logging.FileHandler(Path(__file__).with_name("access.log"), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    access_logger.addHandler(handler)


@app.after_request
def log_request(response):
    access_logger.info("%s %s %s", request.method, request.full_path.rstrip("?"),
                       response.status_code)
    return response


def read_json():
    if not request.is_json:
        abort(400, description="Нужно передать JSON с Content-Type: application/json")
    return request.get_json()


def validate_car(data, partial=False):
    if not isinstance(data, dict) or not data:
        abort(400, description="Нужен непустой объект JSON")
    fields = {"brand", "model", "year", "price"}
    if set(data) - fields:
        abort(400, description="Допустимые поля: brand, model, year, price")
    if not partial and set(data) != fields:
        abort(400, description="Поля brand, model, year и price обязательны")
    result = dict(data)
    for field in ("brand", "model"):
        if field in data:
            if not isinstance(data[field], str) or not data[field].strip():
                abort(400, description=f"{field} должно быть непустой строкой")
            result[field] = data[field].strip()
    if "year" in data:
        if type(data["year"]) is not int or not 1886 <= data["year"] <= datetime.now().year + 1:
            abort(400, description="year должен быть целым числом от 1886 до следующего года")
    if "price" in data:
        price = data["price"]
        if type(price) not in (int, float) or price < 0 or price > 10**12 or not math.isfinite(price):
            abort(400, description="price должна быть числом от 0 до 1000000000000")
    return result


def find_car(car_id):
    for car in cars:
        if car["id"] == car_id:
            return car
    abort(404, description="Автомобиль не найден")


@app.get("/cars")
def list_cars():
    search = request.args.get("search", "").strip().casefold()
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    if sort not in {"id", "brand", "model", "year", "price"} or order not in {"asc", "desc"}:
        abort(400, description="Некорректное поле сортировки или порядок")
    try:
        page = int(request.args.get("page", "1"))
        limit = int(request.args.get("limit", "10"))
    except ValueError:
        abort(400, description="page и limit должны быть целыми числами")
    if page < 1 or not 1 <= limit <= 100:
        abort(400, description="page должна быть положительной, limit - от 1 до 100")
    with lock:
        result = [car.copy() for car in cars if search in car["brand"].casefold()]
    result.sort(key=lambda car: car[sort].casefold() if isinstance(car[sort], str) else car[sort],
                reverse=order == "desc")
    start = (page - 1) * limit
    return jsonify(count=len(result), page=page, limit=limit, items=result[start:start + limit])


@app.get("/cars/<int:car_id>")
def get_car(car_id):
    with lock:
        return jsonify(find_car(car_id))


@app.post("/cars")
def create_car():
    global next_id
    data = validate_car(read_json())
    with lock:
        car = {"id": next_id, **data}
        next_id += 1
        cars.append(car)
        response = jsonify(car)
    response.status_code = 201
    response.headers["Location"] = f"/cars/{car['id']}"
    return response


@app.put("/cars/<int:car_id>")
def replace_car(car_id):
    with lock:
        car = find_car(car_id)
        data = validate_car(read_json())
        car.clear()
        car.update(id=car_id, **data)
        return jsonify(car)


@app.patch("/cars/<int:car_id>")
def update_car(car_id):
    with lock:
        car = find_car(car_id)
        data = validate_car(read_json(), partial=True)
        car.update(data)
        return jsonify(car)


@app.delete("/cars/<int:car_id>")
def delete_car(car_id):
    with lock:
        cars.remove(find_car(car_id))
    return "", 204


@app.delete("/cars")
def delete_all_cars():
    with lock:
        cars.clear()
    return "", 204


@app.post("/cars/bulk")
def create_many_cars():
    global next_id
    data = read_json()
    if not isinstance(data, list) or not 1 <= len(data) <= 100:
        abort(400, description="Нужен массив от 1 до 100 автомобилей")
    validated = [validate_car(item) for item in data]
    with lock:
        created = [{"id": next_id + i, **item} for i, item in enumerate(validated)]
        cars.extend(created)
        next_id += len(created)
        return jsonify(count=len(created), items=created), 201


@app.get("/cars/stats")
def car_stats():
    with lock:
        count = len(cars)
        average = round(sum(car["price"] for car in cars) / count, 2) if count else 0
    return jsonify(count=count, average_price=average)


@app.get("/cars/<int:car_id>/related")
def related_cars(car_id):
    with lock:
        car = find_car(car_id)
        related = [item for item in cars
                   if item["id"] != car_id and item["brand"].casefold() == car["brand"].casefold()]
        return jsonify(count=len(related), items=related)


@app.errorhandler(HTTPException)
def http_error(error):
    response = error.get_response()
    response.data = app.json.dumps({"error": error.description})
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def server_error(error):
    app.logger.exception("Ошибка при обработке запроса")
    return jsonify(error="Внутренняя ошибка сервера"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000)
```

## Проверка запросов

В Postman импортировать [Lab2.postman_collection.json](Lab2.postman_collection.json). В коллекции заданы base_url для основного сервера и example_url для практического примера. Оба сервера должны быть запущены.

Коллекция содержит 35 запросов в двух папках. В запросах есть проверки статусов и содержимого ответов. В начале проверки автомобилей коллекция очищает данные, затем создаёт исходные записи и сохраняет полученные ID в переменных. В конце возвращает три исходных автомобиля.

Для запуска выбрать коллекцию, нажать Run и выполнить один проход. Переменные ID заполняются автоматически. При повторном проходе номера записей могут отличаться.

Проверки коллекции в Postman Collection Runner и через Newman завершились без ошибок. Выполнены 35 запросов и 84 проверки. Для каждого запроса в экспортированной коллекции сохранён пример фактического ответа. Для журнала проверены успешные ответы, ошибки 400, 404, 405, 413 и обработчик 500. Непредвиденная ошибка проверена временной подменой функции поиска в отдельном процессе.

Ниже приведены статусы полного прогона коллекции.

| Запрос | Метод | Статус |
| --- | --- | --- |
| Все товары | GET | 200 |
| Один товар | GET | 200 |
| Создание товара | POST | 201 |
| Замена товара | PUT | 200 |
| Удаление товара | DELETE | 200 |
| Товар после удаления | GET | 404 |
| Неверные данные товара | POST | 400 |
| Очистка перед запуском | DELETE | 204 |
| Создание трёх автомобилей | POST | 201 |
| Список автомобилей | GET | 200 |
| Один автомобиль | GET | 200 |
| Поиск Toyota | GET | 200 |
| Сортировка по цене | GET | 200 |
| Вторая страница | GET | 200 |
| Средняя цена | GET | 200 |
| Связь по марке | GET | 200 |
| Создание автомобиля | POST | 201 |
| Полная замена | PUT | 200 |
| Частичное обновление | PATCH | 200 |
| Нет обязательных полей | POST | 400 |
| Цена строкой | POST | 400 |
| Отрицательная цена | POST | 400 |
| Неверный год | POST | 400 |
| PUT без всех полей | PUT | 400 |
| Чужое поле в PATCH | PATCH | 400 |
| Неверная страница | GET | 400 |
| Неверное поле сортировки | GET | 400 |
| Bulk с ошибкой | POST | 400 |
| После ошибочного bulk | GET | 200 |
| Автомобиль не найден | GET | 404 |
| Удаление автомобиля | DELETE | 204 |
| Повторное удаление | DELETE | 404 |
| Удаление всех автомобилей | DELETE | 204 |
| Статистика пустого списка | GET | 200 |
| Возврат исходных данных | POST | 201 |

### Скриншоты Postman

Получение списка автомобилей.

![GET автомобилей](screenshots/cars-get.png)

Создание автомобиля. Переданы поля brand, model, year и price. Получен статус 201 и ID новой записи.

![POST автомобиля](screenshots/cars-post.png)

Проверки создания прошли успешно.

![Проверки POST](screenshots/postman-tests.png)

Общий результат Collection Runner - 84 пройденные проверки, 0 ошибок.

![Collection Runner](screenshots/collection-runner.png)

Все запросы прогона приведены ниже. Скриншоты показывают сохранённые в Runner ответы. ID увеличиваются при повторных прогонах.

<details>
<summary>1. Все товары</summary>

![Все товары](screenshots/request-01.png)

</details>

<details>
<summary>2. Один товар</summary>

![Один товар](screenshots/request-02.png)

</details>

<details>
<summary>3. Создание товара</summary>

![Создание товара](screenshots/request-03.png)

</details>

<details>
<summary>4. Замена товара</summary>

![Замена товара](screenshots/request-04.png)

</details>

<details>
<summary>5. Удаление товара</summary>

![Удаление товара](screenshots/request-05.png)

</details>

<details>
<summary>6. Товар после удаления</summary>

![Товар после удаления](screenshots/request-06.png)

</details>

<details>
<summary>7. Неверные данные товара</summary>

![Неверные данные товара](screenshots/request-07.png)

</details>

<details>
<summary>8. Очистка перед запуском</summary>

![Очистка перед запуском](screenshots/request-08.png)

</details>

<details>
<summary>9. Создание трёх автомобилей</summary>

![Создание трёх автомобилей](screenshots/request-09.png)

</details>

<details>
<summary>10. Список автомобилей</summary>

![Список автомобилей](screenshots/request-10.png)

</details>

<details>
<summary>11. Один автомобиль</summary>

![Один автомобиль](screenshots/request-11.png)

</details>

<details>
<summary>12. Поиск Toyota</summary>

![Поиск Toyota](screenshots/request-12.png)

</details>

<details>
<summary>13. Сортировка по цене</summary>

![Сортировка по цене](screenshots/request-13.png)

</details>

<details>
<summary>14. Вторая страница</summary>

![Вторая страница](screenshots/request-14.png)

</details>

<details>
<summary>15. Средняя цена</summary>

![Средняя цена](screenshots/request-15.png)

</details>

<details>
<summary>16. Связь по марке</summary>

![Связь по марке](screenshots/request-16.png)

</details>

<details>
<summary>17. Создание автомобиля</summary>

![Создание автомобиля](screenshots/request-17.png)

</details>

<details>
<summary>18. Полная замена</summary>

![Полная замена](screenshots/request-18.png)

</details>

<details>
<summary>19. Частичное обновление</summary>

![Частичное обновление](screenshots/request-19.png)

</details>

<details>
<summary>20. Нет обязательных полей</summary>

![Нет обязательных полей](screenshots/request-20.png)

</details>

<details>
<summary>21. Цена строкой</summary>

![Цена строкой](screenshots/request-21.png)

</details>

<details>
<summary>22. Отрицательная цена</summary>

![Отрицательная цена](screenshots/request-22.png)

</details>

<details>
<summary>23. Неверный год</summary>

![Неверный год](screenshots/request-23.png)

</details>

<details>
<summary>24. PUT без всех полей</summary>

![PUT без всех полей](screenshots/request-24.png)

</details>

<details>
<summary>25. Чужое поле в PATCH</summary>

![Чужое поле в PATCH](screenshots/request-25.png)

</details>

<details>
<summary>26. Неверная страница</summary>

![Неверная страница](screenshots/request-26.png)

</details>

<details>
<summary>27. Неверное поле сортировки</summary>

![Неверное поле сортировки](screenshots/request-27.png)

</details>

<details>
<summary>28. Bulk с ошибкой</summary>

![Bulk с ошибкой](screenshots/request-28.png)

</details>

<details>
<summary>29. После ошибочного bulk</summary>

![После ошибочного bulk](screenshots/request-29.png)

</details>

<details>
<summary>30. Автомобиль не найден</summary>

![Автомобиль не найден](screenshots/request-30.png)

</details>

<details>
<summary>31. Удаление автомобиля</summary>

![Удаление автомобиля](screenshots/request-31.png)

</details>

<details>
<summary>32. Повторное удаление</summary>

![Повторное удаление](screenshots/request-32.png)

</details>

<details>
<summary>33. Удаление всех автомобилей</summary>

![Удаление всех автомобилей](screenshots/request-33.png)

</details>

<details>
<summary>34. Статистика пустого списка</summary>

![Статистика пустого списка](screenshots/request-34.png)

</details>

<details>
<summary>35. Возврат исходных данных</summary>

![Возврат исходных данных](screenshots/request-35.png)

</details>

## Контрольные вопросы

### Базовый уровень

1. CRUD расшифровывается как Create, Read, Update, Delete - создание, чтение, обновление и удаление.
2. Для этих операций применяются POST, GET, PUT или PATCH и DELETE.
3. Идемпотентная операция при повторении оставляет ресурс в том же состоянии. GET, PUT и DELETE идемпотентны. POST обычно нет.
4. При успешном создании возвращается 201 Created.
5. Успешное удаление может вернуть 200 с результатом или 204 с пустым телом.
6. Middleware в Express обрабатывает запрос между его получением и ответом. express.json() разбирает JSON. Во Flask похожие задачи выполняют before_request, after_request и request.get_json().
7. В Express тело читается из req.body после express.json(), во Flask - через request.get_json().
8. В Express используется req.params.id. Во Flask параметр из маршрута /cars/<int:car_id> передаётся аргументом функции.
9. В JavaScript можно применить find(), в Python - перебрать список и сравнить поле id.
10. Если ресурс не найден, возвращается 404.
11. В Express JSON отправляется через res.json(), во Flask через jsonify().
12. В Express используется res.status(201).json(data), во Flask - return jsonify(data), 201.
13. Изменения в памяти теряются при перезапуске. В этой работе снова загружаются исходные записи.
14. В JavaScript используется push(), в Python - append().
15. В JavaScript можно найти индекс и вызвать splice(), в Python - найти объект и вызвать remove().

### Средний уровень

1. PUT полностью заменяет поля ресурса. PATCH меняет только переданную часть.
2. Параметр search читается из query-строки, после чего коллекция фильтруется по выбранному полю. В работе сравнение марок выполняется после casefold().
3. Сначала проверяется имя поля, затем список сортируется через sort() с функцией key. Для убывания используется reverse=True.
4. Для страницы page и размера limit начало равно (page - 1) * limit. Из списка берётся соответствующий срез.
5. Проверяются наличие полей, типы и ограничения. Для Python bool нужно проверять отдельно от int, поскольку bool является подклассом int.
6. Ошибка валидации возвращает 400 Bad Request.
7. Во Flask используется return "", 204. Ответ не содержит JSON.
8. res.json() сериализует значение в JSON. res.send() умеет отправлять разные типы содержимого, например строку, буфер или объект.
9. Для учебного сервера можно использовать возрастающий счётчик. Его изменение и добавление записи выполняются под одной блокировкой.
10. express.json() разбирает JSON-тело и заполняет req.body. Без соответствующего парсера JSON автоматически не превращается в объект req.body.

### Продвинутый уровень

1. Для PATCH проверяются переданные поля, затем обновляются только они. Остальные значения сохраняются.
2. DELETE /cars очищает список под блокировкой и возвращает 204.
3. POST /cars/bulk принимает массив. Все объекты проверяются до изменения коллекции, затем получают разные ID и добавляются вместе.
4. Во Flask используется errorhandler(Exception). HTTP-ошибки обрабатываются отдельно, чтобы 400 и 404 сохраняли свои статусы.
5. Через logging.FileHandler сообщения записываются в access.log. after_request получает готовый ответ и добавляет его статус в запись журнала.
6. REST организует работу вокруг ресурсов и стандартных методов HTTP. Каждый запрос содержит сведения, необходимые для его обработки. API в работе возвращает JSON.
7. При росте проекта маршруты можно разделить на Blueprint, отдельно хранить проверки данных и слой хранения. Для одной учебной сущности достаточно app.py.
8. Можно использовать счётчик, последовательность в БД или UUID. Для параллельных процессов нужны согласованный источник ID и общее хранилище.
9. MAX_CONTENT_LENGTH ограничивает тело запроса. Дополнительно в работе ограничено количество объектов в bulk и число элементов на странице.
10. Связь задаётся общим полем или идентификатором. Здесь связанные автомобили находятся по одинаковой марке, исходная запись исключается из результата.

## Вывод

Реализован API автомобилей с хранением данных в памяти. Отработаны основные HTTP-методы, поиск, сортировка, пагинация и массовые операции. Добавлены проверка данных, журнал запросов и обработка ошибок.

## Источники

- [Flask API](https://flask.palletsprojects.com/en/stable/api/)
- [Обработка ошибок Flask](https://flask.palletsprojects.com/en/stable/errorhandling/)
- [HTTP-методы](https://developer.mozilla.org/ru/docs/Web/HTTP/Methods)
- [Коды состояния HTTP](https://developer.mozilla.org/ru/docs/Web/HTTP/Status)
- [Collection Runner](https://learning.postman.com/latest-v-12/docs/tests-and-scripts/running-collections/intro-to-collection-runs)
- [Репозиторий работы](https://github.com/foidslayer33367/backend/tree/main/lab2-crud)
