#!/usr/bin/env python3
import requests
from utils import *
import sys


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
PORT = 1337
USER_AGENT = get_user_agent()


def result(code, message=''):
    if message:
        print(message)
    print(f'Exit with code {code}', file=sys.stderr)
    sys.exit(code)


def register(host):
    try:
        while True:
            username, password = get_creds()
            first_name, second_name = username.split(' ')[0], ' '.join([i for i in username.split(' ')[1:]])
            email = username.replace(' ', '_') + '@' + get_random_domain()

            response = requests.post(
                f'http://{host}:{PORT}/api/register',
                json={
                    'username': username,
                    'password': password,
                    'email':  email,
                    'first_name': first_name,
                    'second_name': second_name
                },
                headers={'Content-Type': 'application/json', 'User-Agent': USER_AGENT}
            )

            data = response.json()
            if 'Username already exists' not in data['message']:
                return data['token'], username, password


    except requests.Timeout as e:
        print(f'register: {e}', file=sys.stderr)
        result(DOWN, 'Registration Timed Out')
    except requests.exceptions.ConnectionError as e:
        print(f'register: {e}', file=sys.stderr)
        result(DOWN, 'Connection error')
    except Exception as e:
        print(f'register: {e}', file=sys.stderr)
        result(MUMBLE, 'Registration failed')



def login(host, username, password):
    try:
        while True:


            response = requests.post(
                f'http://{host}:{PORT}/api/login',
                json={
                    'username': username,
                    'password': password
                },
                headers={'Content-Type': 'application/json', 'User-Agent': USER_AGENT}
            )

            data = response.json()
            if 'Username already exists' not in data['message']:

                return data['token']

    except requests.Timeout as e:
        print(f'login: {e}', file=sys.stderr)
        result(DOWN, 'Login Timed Out')
    except requests.exceptions.ConnectionError as e:
        print(f'login: {e}', file=sys.stderr)
        result(DOWN, 'Login error')
    except Exception as e:
        print(f'login: {e}', file=sys.stderr)
        result(MUMBLE, 'Login failed')



def make_event(host, token):
    try:
        
        title = random_title()
        date = random_date()
        time = random_time()
        description = f'{title}, will take place on {date} at {time}'
        
        response = requests.post(
            f'http://{host}:{PORT}/api/event/add',
            json={
                'title': title,
                'time': time,
                'date':  date,
                'description': description
            },
            headers={'Content-Type': 'application/json', 'User-Agent': USER_AGENT, 'Authorization': f'Bareer {token}'}
        )

        data = response.json()
        if 'href' in data:
            return data['href'], date

    except requests.Timeout as e:
        print(f'make_event: {e}', file=sys.stderr)
        result(DOWN, 'Make Event Timed Out')
    except requests.exceptions.ConnectionError as e:
        print(f'make_event: {e}', file=sys.stderr)
        result(DOWN, 'Make Event error')
    except Exception as e:
        print(f'make_event: {e}', file=sys.stderr)
        result(MUMBLE, 'Make Event failed')  


def make_task(url, flag, username, to_deadline, token):
    try:
        
        text = flag
        assigned_to = username
        priority = get_priority()
        deadline = random_date_until(to_deadline)

        response = requests.post(
            url,
            json={
                'task_name': text,
                'assigned_to': assigned_to,
                'priority':  priority,
                'deadline': deadline
            },
            headers={'Content-Type': 'application/json', 'User-Agent': USER_AGENT, 'Authorization': f'Bareer {token}'}
        )

    except requests.Timeout as e:
        print(f'make_task: {e}', file=sys.stderr)
        result(DOWN, 'Make Task Timed Out')
    except requests.exceptions.ConnectionError as e:
        print(f'make_task: {e}', file=sys.stderr)
        result(DOWN, 'Make Task error')
    except Exception as e:
        print(f'make_task: {e}', file=sys.stderr)
        result(MUMBLE, 'Make Task failed')     


def get_tasks(url, token):
    try:
    
        response = requests.get(
            url,
            headers={'User-Agent': USER_AGENT, 'Authorization': f'Bareer {token}'}
        )
        
        return response.json()

    except requests.Timeout as e:
        print(f'get_tasks: {e}', file=sys.stderr)
        result(DOWN, 'Get Tasks Timed Out')
    except requests.exceptions.ConnectionError as e:
        print(f'get_tasks: {e}', file=sys.stderr)
        result(DOWN, 'Get Tasks error')
    except Exception as e:
        print(f'get_tasks: {e}', file=sys.stderr)
        result(MUMBLE, 'Get Tasks failed')     
        


    except requests.Timeout as e:
        print(f'make_task: {e}', file=sys.stderr)
        result(DOWN, 'Make Task Timed Out')
    except requests.exceptions.ConnectionError as e:
        print(f'make_task: {e}', file=sys.stderr)
        result(DOWN, 'Make Task error')
    except Exception as e:
        print(f'make_task: {e}', file=sys.stderr)
        result(MUMBLE, 'Make Task failed')     


def get(*argv):
    try:
        host, flag_id, flag = argv[:3]

        username, password, href = flag_id.split(':')[0].replace('_', ' '), flag_id.split(':')[1], flag_id.split(':')[2]
        token = login(host,username, password)

        
        url = f'http://{host}:{PORT}/api{href}/tasks'
        data = get_tasks(url, token)
        for i in data:
            if flag == i['text']:
                result(OK, "SUCCESS")
            else:
                result(CORRUPT, "Flag check failed")

    except Exception as e:
        print(f"GET error: {e}", file=sys.stderr)
        result(MUMBLE, "GET flag failed")


def put(*args):
    try:

        host, flag_id, flag = args[:3]

        token, username, password = register(host)

        href, to_deadline = make_event(host, token)

        url = f'http://{host}:{PORT}/api{href}/task/add'
        make_task(url, flag, username, to_deadline, token)

        flag_id = f'{username.replace(" ", "_")}:{password}:{href}'
        result(OK, flag_id)

    except Exception as e:
        print(f"Action PUT error: {e}", file=sys.stderr)
        result(MUMBLE, "PUT flag failed")

def check(*args):
    try:
        host = args[0]

        response = requests.get(f"http://{host}:5000/")
        if response.status_code != 200:
            print(f'Action CHECK Frontend error {e}', file=sys.stderr)
            result(MUMBLE, "CHECK failed")
        token, username, password= register(host)
        
        result(OK, "SUCCESS")
    except Exception as e:
        print(f"Action CHECK error: {e}", file=sys.stderr)
        result(MUMBLE, "CHECK failed")


COMMANDS = {
    'get': get,
    'check': check,
    'put' : put
}

if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1])(*sys.argv[2:])
    except Exception as e:
        result(CHECKER_ERROR, f'INTERNAL ERROR: {e}')
