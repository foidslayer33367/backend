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
