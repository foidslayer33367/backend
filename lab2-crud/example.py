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
