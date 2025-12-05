#!/usr/bin/env python3

from urllib.parse import urljoin, urlparse
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
import requests
import string
import random
import sys
import re


HOST = sys.argv[1]
PORT = 3000


def rnd_string(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def normalize_host(host: str) -> str:
    if not host.startswith("http"):
        host = f"http://{host}"
    parsed = urlparse(host)
    port = parsed.port or PORT
    host = f"{parsed.scheme}://{parsed.hostname}:{port}"
    return host


def session_with_defaults() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
        }
    )
    return s


def get_csrf(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name": "csrf-token"})
    if meta and meta.get("content"):
        return meta["content"]
    token_input = soup.find("input", attrs={"name": "authenticity_token"})
    return token_input["value"] if token_input else None


def register_and_login(session: requests.Session, host: str) -> Tuple[str, str]:
    host = normalize_host(host)
    username = f"{rnd_string(6)}_{rnd_string(4)}"
    email = f"{username}@example.com"
    password = rnd_string(random.randint(10, 14))

    sign_up = session.get(urljoin(host, "/users/sign_up.html"))
    sign_up.raise_for_status()
    token = get_csrf(sign_up.text)
    if not token:
        raise RuntimeError("No CSRF token on sign up page")

    payload = {
        "authenticity_token": token,
        "user[email]": email,
        "user[password]": password,
        "user[password_confirmation]": password,
        "commit": "Зарегистрироваться",
    }
    resp = session.post(urljoin(host, "/users"), data=payload, allow_redirects=True)
    resp.raise_for_status()

    login_page = session.get(urljoin(host, "/users/sign_in.html"))
    login_page.raise_for_status()
    token = get_csrf(login_page.text)
    if not token:
        raise RuntimeError("No CSRF token on sign in page")
    login_payload = {
        "authenticity_token": token,
        "user[email]": email,
        "user[password]": password,
        "commit": "Войти",
    }
    login_resp = session.post(urljoin(host, "/users/sign_in"), data=login_payload, allow_redirects=True)
    login_resp.raise_for_status()
    return email, password


def parse_labyrinth(html: str) -> Tuple[List[List[int]], Tuple[int, int], Tuple[int, int], str]:
    soup = BeautifulSoup(html, "html.parser")
    grid_el = soup.find(class_="labyrinth-grid")
    if not grid_el:
        raise RuntimeError("No labyrinth grid found")
    style = grid_el.get("style", "")
    m = re.search(r"repeat\((\d+)", style)
    if not m:
        raise RuntimeError("Cannot find grid width")
    width = int(m.group(1))
    cells = grid_el.find_all("span")
    if not cells:
        raise RuntimeError("No labyrinth cells")
    height = len(cells) // width
    grid = [[0] * width for _ in range(height)]
    start = finish = None
    for idx, cell in enumerate(cells):
        r, c = divmod(idx, width)
        classes = cell.get("class", [])
        if "labyrinth-cell--wall" in classes:
            grid[r][c] = 1
        if "labyrinth-cell--start" in classes:
            start = (r, c)
        if "labyrinth-cell--finish" in classes:
            finish = (r, c)
    if start is None or finish is None:
        raise RuntimeError("Start/finish not found")
    token = get_csrf(html)
    if not token:
        raise RuntimeError("No CSRF token on labyrinth page")
    return grid, start, finish, token


def bfs_path(grid: List[List[int]], start: Tuple[int, int], finish: Tuple[int, int]) -> str:
    h, w = len(grid), len(grid[0])
    dirs = [(-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")]
    q = [start]
    prev = {start: None}
    move_dir = {}
    while q:
        r, c = q.pop(0)
        if (r, c) == finish:
            break
        for dr, dc, ch in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 0 and (nr, nc) not in prev:
                prev[(nr, nc)] = (r, c)
                move_dir[(nr, nc)] = ch
                q.append((nr, nc))
    if finish not in prev:
        raise RuntimeError("No path to finish")
    path = []
    cur = finish
    while cur != start:
        path.append(move_dir[cur])
        cur = prev[cur]
    return "".join(reversed(path))


def extract_reward(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one(".reward-panel__text")
    return el.get_text(strip=True) if el else None


def solve_task(session: requests.Session, host: str, task_id: int) -> Optional[str]:
    page = session.get(urljoin(host, f"/tasks/{task_id}"))
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")
    if not soup.find(class_="labyrinth-grid"):
        return None

    grid, start, finish, token = parse_labyrinth(page.text)
    moves = bfs_path(grid, start, finish)

    solve_resp = session.post(
        urljoin(host, f"/tasks/{task_id}/solve"),
        data={"authenticity_token": token, "moves": moves, "commit": "Проверить маршрут"},
        headers={"Accept": "text/html, text/vnd.turbo-stream.html"},
        allow_redirects=True,
    )
    solve_resp.raise_for_status()

    reward = extract_reward(solve_resp.text)
    if reward:
        return reward

    final = session.get(urljoin(host, f"/tasks/{task_id}"))
    final.raise_for_status()
    reward = extract_reward(final.text)
    return reward


def collect_task_ids(html: str) -> List[int]:
    soup = BeautifulSoup(html, "html.parser")
    ids = set()
    for a in soup.find_all("a", href=True):
        m = re.match(r"/tasks/(\d+)", a["href"])
        if m:
            ids.add(int(m.group(1)))
    return sorted(ids)


def main():
    host_arg = sys.argv[1] if len(sys.argv) > 1 else HOST
    host = normalize_host(host_arg)
    session = session_with_defaults()

    try:
        register_and_login(session, host)
    except Exception as e:
        print(f"Register/Login error: {e}", file=sys.stderr)
        sys.exit(1)

    index = session.get(urljoin(host, "/tasks"))
    index.raise_for_status()
    task_ids = collect_task_ids(index.text)
    rewards = []
    for task_id in task_ids:
        try:
            reward = solve_task(session, host, task_id)
            if reward:
                rewards.append((task_id, reward))
        except Exception as e:
            print(f"Task {task_id} error: {e}", file=sys.stderr)
            continue

    if rewards:
        for _, reward in rewards:
            print(reward, flush=True)
    else:
        print("No rewards collected.", flush=True)


if __name__ == "__main__":
    main()

