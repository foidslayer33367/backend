from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)
app.json.ensure_ascii = False


@app.before_request
def log_request():
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {request.method} {request.url}", flush=True)


@app.get('/')
def home():
    return 'Добро пожаловать на базовый сервер!'


@app.get('/api/status')
def status():
    return jsonify({'status': 'ok', 'framework': 'Flask'})


@app.get('/api/info')
def info():
    return jsonify({'author': 'Осипов Герман Юрьевич', 'version': '1.0.0'})


@app.get('/api/users/<int:user_id>')
def get_user(user_id):
    return jsonify({'message': 'Информация о пользователе', 'userId': user_id})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3001, debug=True)
