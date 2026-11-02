from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False


@app.before_request
def log_request():
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {request.method} {request.url}", flush=True)


@app.get('/')
def home():
    return 'Backend is ready', 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.get('/api/employees')
def employees():
    return jsonify([
        {'id': 1, 'name': 'Иван Иванов', 'position': 'Developer'},
        {'id': 2, 'name': 'Анна Петрова', 'position': 'Designer'},
        {'id': 3, 'name': 'Сергей Смирнов', 'position': 'Manager'},
    ])


@app.get('/api/offices')
def offices():
    return jsonify([
        {'id': 1, 'city': 'Ставрополь', 'address': 'ул. Мира, 10'},
        {'id': 2, 'city': 'Москва', 'address': 'ул. Центральная, 15'},
    ])


@app.get('/api/employees/<int:employee_id>')
def get_employee(employee_id):
    return jsonify({'requestedId': employee_id, 'status': 'success'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)
