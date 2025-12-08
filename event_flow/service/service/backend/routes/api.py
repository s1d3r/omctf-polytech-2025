from . import api_bp
from flask import request
import database.db as db
from utils.utils import make_invitecode, check_password
from utils.auth import create_jwt, verify_jwt, login_required, check_permissions


@api_bp.route('/api/events')
@login_required
def get_all_events():
    events = db.get_events()
    return events, 200


@api_bp.route('/api/event/<id>/update', methods=['POST'])
@login_required
def update_event(id):
    perm = check_permissions(id)
    if perm == 404:
        return {'message': 'Event not found!'}, 404
    if perm == 403:
        return {'message': "Access Denied!"}, 403

    data = request.get_json()
    if not data:
        return {'message': 'Bad request!'}, 400

    status = db.update_event(id, data)
    if status == 200:
        return {'message': 'Successfully updated!'}, 200
    if status == 400:
        return {'message': 'Bad request!'}, 400
    if status == 404:
        return {'message': 'Event not found!'}, 404



@api_bp.route('/api/event/<id>', methods=['GET'])
@login_required
def get_event(id):
    event = db.get_event(id)
    if not event:
        return {'message': 'Event not found!'}, 404

    event['date'] = event['date'].isoformat()
    return event, 200



@api_bp.route('/api/event/add', methods=['POST'])
@login_required
def add_event():
    auth_header = request.headers.get("Authorization")
    token = verify_jwt(auth_header.split(" ")[1])

    data = request.get_json()
    if not data:
        return {'message': 'Bad request!'}, 400

    required_keys = ['title', 'time', 'description', 'date']
    if any(key not in data or data[key] is None for key in required_keys):
        return {'message': 'Bad request!'}, 400

    invitecode = make_invitecode(token['username'], data['title'])
    event = db.add_event(data['title'], token["id"], invitecode, data['date'], data['time'], data['description'])

    if event[1] == 400:
        return {'message': f'Bad request! {event[0]}'}, 400

    return {'href': f'/event/{event[0]}'}, 200



@api_bp.route('/api/event/<id>/task/add', methods=['POST'])
@login_required
def add_task(id):
    perm = check_permissions(id)
    if perm == 404:
        return {'message': 'Event not found!'}, 404
    if perm == 403:
        return {'message': "Access Denied!"}, 403


    data = request.get_json()
    if not data:
        return {'message': 'Bad request!'}, 400

    required_keys = ['task_name', 'assigned_to', 'priority', 'deadline']
    if any(key not in data or data[key] is None for key in required_keys):
        return {'message': 'Bad request!'}, 400

    db.add_task(id, data['task_name'], data['assigned_to'], data['priority'], data['deadline'])
    return {'message': 'Successfully added!'}, 200


@api_bp.route('/api/event/<id>/tasks', methods=['GET'])
@login_required
def get_tasks(id):
    perm = check_permissions(id)
    if perm == 404:
        return {'message': 'Event not found!'}, 404
    if perm == 403:
        return {'message': "Access Denied!"}, 403

    tasks = db.get_event_tasks(id)
    return tasks, 200


@api_bp.route('/api/event/<id>/join', methods=['POST'])
@login_required
def join_event(id):
    auth_header = request.headers.get("Authorization")
    token = verify_jwt(auth_header.split(" ")[1])

    data = request.get_json()
    if not data or 'invitecode' not in data:
        return {'message': 'Bad request'}, 400

    user_id = token['id']
    status = db.add_event_org(data['invitecode'], user_id, id)

    if status == 200:
        return {'message': 'Successfully joined!'}, 200
    if status == 400:
        return {'message': 'Bad request!'}, 400
    if status == 409:
        return {'message': 'Wrong event invitecode'}, 409


@api_bp.route('/api/task/<id>', methods=['POST'])
@login_required
def task_completing(id):
    data = request.get_json()
    if not data or 'completed' not in data:
        return {'message': 'Bad request!'}, 400

    task = db.get_task(id)
    if not task:
        return {'message': 'Task not found!'}, 404

    event_id = task['event_id']
    value = data['completed']

    perm = check_permissions(event_id)
    if perm == 404:
        return {'message': 'Event not found!'}, 404
    if perm == 403:
        return {'message': "Access Denied!"}, 403

    code = db.update_task(id, value)
    return {'message': 'Successfully updated'}, code


@api_bp.route('/api/event/<id>/history', methods=['GET'])
@login_required
def get_history(id):
    auth_header = request.headers.get("Authorization")
    token = verify_jwt(auth_header.split(" ")[1])

    limit = request.args.get('limit')

    perm = check_permissions(id)
    if perm == 404:
        return {'message': 'Event not found!'}, 404
    if perm == 403:
        return {'message': "Access Denied!"}, 403

    history = db.get_history(id, limit=limit) if limit else db.get_history(id)
    if history == 400:
        return {'message': 'Bad request'}, 400

    return history, 200



@api_bp.route('/api/user/update', methods=['POST'])
@login_required
def user_update():
    auth_header = request.headers.get("Authorization")
    token = verify_jwt(auth_header.split(" ")[1])

    data = request.get_json()
    if not data:
        return {'message': 'Bad request!'}, 400

    values = {k: v for k, v in data.items() if v != ''}
    user = db.update_user(token['id'], values)
    if not user:
        return {'message': "You can't change username value"}, 400

    return {'message': 'Successfully updated', }, 200


@api_bp.route('/api/user', methods=['GET'])
@login_required
def user():
    auth_header = request.headers.get("Authorization")
    token = verify_jwt(auth_header.split(" ")[1])


    username = token['username']
    user = db.get_user(username)
    return user, 200


@api_bp.route("/api/auth")
@login_required
def check_auth():
    return {'message': 'Success!'}, 200


@api_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return {"message": "Invalid data"}, 400

    username = data['username']
    password = data['password']

    user = db.get_user(username)
    if not user or not check_password(password, user['password']):
        return {"message": "Invalid credentials"}, 401

    token = create_jwt({"id": user['id'], "username": user['username'], "role": user['role']})
    return {"message": "Login successful", "token": token}, 200


@api_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    required_fields = ['username', 'password', 'email', 'first_name', 'second_name']
    if not data or any(field not in data for field in required_fields):
        return {"message": "Missing required fields"}, 400

    username = data['username']
    email = data['email']
    password = data['password']
    first_name = data['first_name']
    second_name = data['second_name']

    if db.get_user(username):
        return {"message": "Username already exists"}, 401

    new_user = db.add_user(username, email, first_name, second_name, password)
    if not new_user:
        return {'message': 'Bad request!'}, 400

    token = create_jwt({"id": new_user['id'], "username": new_user['username'], "role": new_user['role']})
    return {"message": "Registration successful", "token": token}, 200
