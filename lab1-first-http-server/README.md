# Лабораторная работа № 1

## Настройка среды разработки и первый HTTP-сервер

**Студент:** Осипов Герман Юрьевич  
**Группа:** ПИЖ-б-о-25-2  
**Вариант:** 10  
**Уровень:** повышенный  
**Дисциплина:** Разработка web-приложений  
**Преподаватель:** Новикова Е.Н.  
**Технология:** Python + Flask  
**Год:** 2026

## Цель работы

Освоить настройку среды для backend-разработки, создать HTTP-сервер, который обрабатывает GET-запросы и возвращает текст и JSON. Разобраться с маршрутами, параметрами URL, обработкой ошибки 404 и автоматическим перезапуском при изменении кода.

## Теоретическое обоснование

В клиент-серверной архитектуре клиент отправляет запрос, а сервер его обрабатывает и возвращает ответ. Для взаимодействия используется HTTP. В этой работе используется метод GET, который предназначен для получения данных. Запрос включает метод, адрес, заголовки и при необходимости тело. Ответ содержит код состояния, заголовки и тело.

Эндпоинт определяется HTTP-методом и адресом ресурса, например GET /api/employees. Во Flask декоратор связывает маршрут с функцией Python. Если подходящего маршрута нет, сервер возвращает ошибку 404. Часть адреса можно сделать параметром и передавать её значение в функцию.

JSON представляет данные в виде объектов, массивов, строк, чисел и логических значений. Во Flask для формирования таких ответов используется jsonify(). Для автоматического перезапуска во время разработки предусмотрен debug=True. Этот режим используется только на локальном компьютере.

## Выполнение практического примера

### Подготовка среды

Для проекта нужно создать виртуальное окружение и установить зависимости:

```bash
python -m venv .venv
```

Активация в Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Активация в macOS и Linux:

```bash
source .venv/bin/activate
```

Установка зависимостей:

```bash
python -m pip install -r requirements.txt
```

### Код примера

Практический пример находится в example.py. Для него выбран порт 3001, чтобы он не мешал запуску индивидуального задания на порту 3000.

```python
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
```

Запуск:

```bash
python example.py
```

Проверка:

```bash
curl -i http://127.0.0.1:3001/
curl -i http://127.0.0.1:3001/api/status
curl -i http://127.0.0.1:3001/api/info
curl -i http://127.0.0.1:3001/api/users/5
curl -i http://127.0.0.1:3001/anything-else
```

Корневой маршрут возвращает приветствие. /api/status сообщает о состоянии сервера, /api/info содержит имя автора и версию. /api/users/5 возвращает переданный ID. Для неизвестного адреса возвращается JSON с ошибкой и кодом 404.

## Выполнение индивидуального задания

Для повышенного уровня варианта 10 нужны две коллекции: сотрудники и офисы. Дополнительно нужен маршрут с ID сотрудника, собственный обработчик 404 и журналирование входящих запросов.

| Метод | Путь | Результат |
|---|---|---|
| GET | / | Текст Backend is ready |
| GET | /api/employees | JSON со списком сотрудников |
| GET | /api/offices | JSON со списком офисов |
| GET | /api/employees/5 | Подтверждение переданного ID |
| GET | /not-found | JSON с ошибкой и статусом 404 |

Обработчик 404 не является отдельным маршрутом: он вызывается для адресов, которые не найдены. Данные списков заданы в коде, как разрешено в задании. Параметризованный маршрут подтверждает ID, но не ищет сотрудника в списке.

### Код сервера

```python
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
```

Запуск индивидуального задания:

```bash
python app.py
```

Команды проверки:

```bash
curl -i http://127.0.0.1:3000/
curl -i http://127.0.0.1:3000/api/employees
curl -i http://127.0.0.1:3000/api/offices
curl -i http://127.0.0.1:3000/api/employees/5
curl -i http://127.0.0.1:3000/not-found
```

### Проверка ответов

Обработчики проверены встроенным тест-клиентом Flask, без открытия сетевого порта. Проверены коды ответа, тип JSON, содержимое списков, передача ID, ошибка для строкового ID и журналирование полного URL. Все 12 проверенных запросов обработаны правильно. Результаты сохранены в checks.txt, записи журнала - в requests.txt.

```text
Проверка встроенным тест-клиентом Flask (без сетевого сервера)

app.py: GET /
HTTP 200
Content-Type: text/plain; charset=utf-8
Backend is ready

app.py: GET /api/employees
HTTP 200
Content-Type: application/json
[{"id":1,"name":"Иван Иванов","position":"Developer"},{"id":2,"name":"Анна Петрова","position":"Designer"},{"id":3,"name":"Сергей Смирнов","position":"Manager"}]

app.py: GET /api/offices
HTTP 200
Content-Type: application/json
[{"address":"ул. Мира, 10","city":"Ставрополь","id":1},{"address":"ул. Центральная, 15","city":"Москва","id":2}]

app.py: GET /api/employees/5
HTTP 200
Content-Type: application/json
{"requestedId":5,"status":"success"}

app.py: GET /not-found
HTTP 404
Content-Type: application/json
{"error":"Not Found"}

app.py: GET /api/employees/ivan
HTTP 404
Content-Type: application/json
{"error":"Not Found"}

app.py: GET /api/employees/5?view=short
HTTP 200
Content-Type: application/json
{"requestedId":5,"status":"success"}

example.py: GET /
HTTP 200
Content-Type: text/html; charset=utf-8
Добро пожаловать на базовый сервер!

example.py: GET /api/status
HTTP 200
Content-Type: application/json
{"framework":"Flask","status":"ok"}

example.py: GET /api/info
HTTP 200
Content-Type: application/json
{"author":"Осипов Герман Юрьевич","version":"1.0.0"}

example.py: GET /api/users/5
HTTP 200
Content-Type: application/json
{"message":"Информация о пользователе","userId":5}

example.py: GET /anything-else
HTTP 404
Content-Type: application/json
{"error":"Not Found"}

Итого: 12 запросов, все проверки пройдены.
Автоперезапуск задан debug=True; запуск reloader в этой среде недоступен.
```

### Автоматический перезапуск

В точке запуска app.run() указан debug=True. После запуска python app.py изменение и сохранение app.py должно приводить к автоматическому перезапуску. Для ручной проверки можно изменить строку приветствия, сохранить файл и обновить корневую страницу. После проверки нужно вернуть исходный текст.

### Скриншоты результатов

Для завершения этого раздела требуется локально запустить оба сервера и сохранить снимки ответов из браузера или curl. Команды перечислены в curl_commands.txt. Нужны снимки пяти ответов индивидуального задания и ответов практического примера. Также нужно сохранить вывод терминала с журналом запросов и автоматическим перезапуском. Сетевой запуск и перезапуск в текущей среде проверки недоступны, поэтому снимки работающего сервера пока не приложены.

## Контрольные вопросы

### 1. Что такое клиент-серверная архитектура?

Это взаимодействие двух сторон: клиент отправляет запрос, сервер обрабатывает его и возвращает ответ. Например, браузер запрашивает список сотрудников, а сервер возвращает JSON.

### 2. Какой протокол используется для общения клиента и сервера в вебе?

HTTP. Для защищённого соединения используется HTTPS, который передаёт HTTP по зашифрованному соединению TLS.

### 3. Что такое эндпоинт?

Конкретный адрес вместе с HTTP-методом. Например, GET /api/offices получает список офисов.

### 4. Как устроены HTTP-запрос и HTTP-ответ? Что такое код состояния?

В HTTP/1.1 запрос содержит стартовую строку с методом, путём и версией протокола, заголовки, пустую строку и необязательное тело. Ответ содержит строку статуса, заголовки и тело. Код состояния сообщает результат обработки: например, 200 означает успешный ответ, 404 - отсутствие ресурса.

### 5. Что такое JSON и почему он популярен?

JSON - текстовый формат обмена данными. Он удобен для API, потому что поддерживает привычные структуры и обрабатывается во многих языках программирования. jsonify() формирует JSON-ответ и устанавливает нужный Content-Type.

### 6. Как запустить сервер Flask?

Активировать виртуальное окружение, установить зависимости и выполнить python app.py. В проекте сервер настроен на адрес 127.0.0.1 и порт 3000.

### 7. Что такое автоматический перезапуск и зачем он нужен?

Он позволяет применять изменения кода без ручного выключения и запуска сервера. Во Flask используется режим debug=True. Для Node.js в методичке рассматривается nodemon.

### 8. Какие коды состояния HTTP известны? За что отвечает 404?

200 - успешный запрос, 201 - создание ресурса, 400 - некорректный запрос, 401 - требуется аутентификация, 403 - доступ запрещён, 404 - ресурс не найден, 405 - метод не разрешён, 500 - внутренняя ошибка сервера. В работе неизвестные адреса возвращают 404 и объект error.

### 9. Для чего нужны middleware и декораторы запросов?

Middleware в Express выполняют промежуточную обработку запроса. Во Flask декораторы регистрируют обработчики: @app.get() связывает URL с функцией, @app.before_request вызывает функцию перед обработкой запроса, @app.errorhandler(404) задаёт ответ для ошибки. В этой работе before_request используется для вывода времени, метода и URL.

### 10. Как получить параметр из пути URL во Flask?

Указать его в маршруте, например /api/employees/<int:employee_id>. Flask преобразует подходящий сегмент URL в целое число и передаст employee_id в функцию. Строка вместо числа не подойдёт маршруту и получит 404.

## Вывод

Подготовлены практический пример и сервер для варианта 10. Реализованы текстовый ответ, две JSON-коллекции, маршрут с параметром и обработчик 404. Добавлен журнал запросов и настроен режим автоматического перезапуска. При проверке разобрана разница между обычным текстом и JSON, а также передача целого числа через URL. Ответы проверены тест-клиентом Flask; остаётся проверить сетевой запуск, перезапуск и приложить скриншоты.

## Использованные источники

1. Методические указания «Лабораторная работа1-2.pdf».
2. [Flask Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/).
3. [HTTP, MDN](https://developer.mozilla.org/ru/docs/Web/HTTP).
4. [JSON, MDN](https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/JSON).
