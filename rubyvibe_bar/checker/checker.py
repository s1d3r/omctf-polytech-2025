#!/usr/bin/env python3
"""
Checker for Tavern service.
Actions:
  check host
  put host flag_id flag vuln
  get host flag_id flag vuln
"""

import argparse
import json
import os
import random
import re
import string
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110


@dataclass
class UserData:
    username: str
    password: str
    task_id: int
    task_type: str
    host: str


def rnd_string(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


TITLES = [
    "Ember Coil Passage",
    "Glitchstone Relay",
    "Iron Veil Labyrinth",
    "Void Lantern Circuit",
    "Crimson Mirror Halls",
    "Static Loop Network",
    "Lunar Echo Passage",
    "Cobalt Drift Maze",
    "Plasma Spiral Grounds",
    "Arcane Junction Walk",
    "Obsidian Twist Route",
    "Quantum Dust Corridors",
    "Neon Pulse Run",
    "Forgotten Relay Paths",
    "Silent Echo Conflux",
    "Chrome Gutter Circuit",
    "Shadow Loom Track",
    "Midnight Pulse Alley",
    "Ghostwire Chambers",
    "Ruined Neon Fold",
    "Phantom Ember Crossing",
    "Omega Coil Rim",
    "Nexus Thread Run",
    "Prism Gate Spiral",
    "Specter Coil Tangle",
    "Binary Lantern Drift",
    "Frostbite Arc Passage",
    "Kinetic Flux Maze",
    "Driftglass Channel",
    "Helix Ember Wards",
    "Paradox Node Trail",
    "Ion Singularity Walk",
    "Crystal Dusk Passage",
    "Hollow Chrome Circuit",
    "Glimmer Mazework",
    "Obscura Gear Tunnels",
    "Radiant Circuit Web",
    "Alloy Whisper Route",
    "Driftstone Crypt",
    "Plasmic Coil Walk",
    "Ethereal Gate Row",
    "Diesel Mist Maze",
    "Ferrum Winding Arches",
    "Neon Sundial Route",
    "Warden’s Coil Track",
    "Rune Flux Alley",
    "Ashen Circuit Slope",
    "Emberline Crawl",
    "Rogue Lantern Drift",
    "Phantom Gear Spiral",
    "Terminal Dust Expanse",
    "Embercore Shift Maze",
    "Driftshadow Loop",
    "Silent Coil Passage",
    "Rift Gate Columns",
    "Nexus Thread Vault",
    "Aurora Fragment Paths",
    "Fractal Ember Roads",
    "Veilstone Hollows",
    "Rift Lantern Ring",
    "Static Prism Basin",
    "Viridian Circuit Court",
    "Crimson Drift Hollow",
    "Glitchline Coil Pass",
    "Obsidian Gateworks",
    "Helix Corridor Web",
    "Radiant Depthway",
    "Cobalt Ion Curve",
    "Shadowglass Breath",
    "Arc Circuit Labyrinth",
    "Neon Warp Halls",
    "Etherbound Crossing",
    "Plasma Rune Array",
    "Luminous Drift Maze",
    "Horizon Coil Channel",
    "Phantom Pulse Loop",
    "Whisperline Track",
    "Ember Rift Chamber",
    "Driftlight Scape",
    "Chrome Fracture Halls",
    "Voidgate Steps",
    "Nova Coil Terrace",
    "Rustpulse Route",
    "Silent Verge Hallways",
    "Circuitbreaker Maze",
    "Static Web Span",
    "Lunar Haze Labyrinth",
    "Ion Thread Tunnels",
    "Quantum Verge Relay",
    "Sundown Coil Cradle",
    "Plasma Mirage Alley",
    "Solitude Gear Trail",
    "Neon Cradle Junction",
    "Mirror Rift Pass",
    "Dustward Tangle",
    "Prismwind Tracks",
    "Shadecoil Run",
    "Driftroot Passage",
    "Arc-Spire Netways",
    "Echo Helix Wards",
    "Phantom Lantern Basin",
    "Embergeist Labyrinth",
    "Frostcoil Passages",
    "Obsidian Pulse Loop",
    "Chromaline Circuits",
    "Fluxgate Shellway",
    "Whispered Dusk Maze",
    "Nova Run Archways",
    "Gloomwire Track",
    "Spectral Ionworks",
    "Neon Crest Hollows",
    "Labyrinth of the Broken Gear",
    "Hollow Lantern Bend",
    "Spiral Gate Fringe",
    "Driftward Ruins",
    "Embercast Maze",
    "Arc Reactor Pit",
    "Woven Gear Channels",
    "Looming Ion Passage",
    "Static Gutter Paths",
    "Chrome Circuit Hollows",
    "Shatterline Drift",
    "Radiant Ember Net",
    "Vortex Prism Halls",
    "Gatecoil Sector",
    "Quiet Fractal Span",
    "Hex Lantern Grounds",
    "Plasma Ridge Lines",
    "Echoing Stair Maze",
    "Dawncoil Pass",
    "Voltfrost Channels",
    "Shadowbend Weave",
    "Cobalt Pulse Works",
    "Glowing Verge Tunnels",
    "Nova Ashward Rings",
    "Emberwrought Circuit",
    "Driftrune Hollow",
    "Phantom Neon Divide",
    "Vaporlock Maze",
    "Prism Echo Gallery",
    "Mirage Gear Cleft",
    "Static Tide Pass",
    "Runeweave Tracks",
    "Obscure Ion Range",
    "Emberfall Thread",
    "Whisper Gate Labyrinth",
    "Chrome Rift Zone",
    "Neon Echo Bastion",
    "Ionflare Channel",
    "Driftstep Sector",
    "Glitchshard Basin",
    "Lantern Coil Paths",
    "Nova Prism Chambers",
    "Cobalt Maze Stacks",
    "Plasmacast Hollows",
    "Shadow Weave Network",
    "Gearbound Depths",
    "Ember Spiral Crest",
    "Quantum Lit Spiral",
    "Frosted Nexus Tracks",
    "Dustlight Corridor",
    "Prism Gate Hollows",
    "Fluxstone Route",
    "Silent Verge Crossing",
    "Static Lantern Ring",
    "Riftwind Drift",
    "Arc Halo Trail",
    "Phantom Crestway",
    "Cobalt Rune Tunnels",
    "Nightglass Circuit",
    "Shardcoil Steps",
    "Solar Drift Lines",
    "Neon Fathom Maze",
    "Ember Coil Lattice",
    "Chronicle Gear Maze",
    "Voidspark Passage",
    "Driftglow Crown",
    "Frostbridge Halls",
    "Synthex Gate Path",
    "Radiant Obsidian Spiral",
    "Fracture Coil Chamber",
    "Glimmer Rift Passage",
    "Ember Pulse Loop",
    "Horizon Prism Drift",
    "Ionshift Hallway",
    "Luminous Gear Vines",
    "Neon Shatter Circuit",
    "Flux Spiral Gutter",
    "Static Run Nexus",
    "Arcane Crown Walk",
    "Shadowline Fold",
    "Ethercoil Passage",
    "Driftgloom Hollow",
    "Emberhowl Chambers",
    "Quantum Shardworks",
    "Chrome Dust Gallery",
    "Plasmarift Aisles",
    "Lantern Pulse Cradle",
    "Mirage Circuit Bend",
    "Obsidian Drift Run",
]

DESCS = [
    "Тени двигаются быстрее тебя — выбирай путь, где они медлят.",
    "Пульсации стены подскажут, где выход ближе.",
    "Холодный ветер дует только из правильного коридора.",
    "Платформы меняют форму, когда ты не смотришь.",
    "Мигающие руны показывают тайные развилки.",
    "Под ногами дрожит металл — обходи шумные участки.",
    "Дальний звон означает неверное направление.",
    "Время замедляется в тупиках — чувствуй ритм.",
    "Слабый свет дрейфует к выходу — следуй за ним.",
    "Коридоры расширяются, если выбран путь верный.",
    "Стены шепчут, когда ты поворачиваешь не туда.",
    "Заземлённые панели безопаснее блестящих.",
    "Скребущий звук ведёт к ловушкам — держись подальше.",
    "Невидимые нити вибрируют рядом с правильными поворотами.",
    "Пыль на полу скрывает следы предыдущих странников.",
    "Кривые тени указывают направление света — и выхода.",
    "Разломы в стенах подают импульсы: один — верно, два — в тупик.",
    "Пространство сжимается, если слишком долго стоять.",
    "Лёгкая неоновая дымка показывает безопасную зону.",
    "Где воздух жарче — там прячется ловушка.",
    "Холодный металл указывает путь вглубь.",
    "Эхо шагов исчезает в правильном тоннеле.",
    "Аномалии дрожат сильнее возле развилок.",
    "Платформы складываются в нужную сторону.",
    "Осколки света отражают истинный маршрут.",
    "Ловушки всегда ставят рядом с яркими стенами.",
    "Длинные коридоры редко бывают безопасны.",
    "Светящиеся руны гаснут, если выбрать неверно.",
    "Монотонный гул — признак тупика.",
    "Лёгкий сквозняк ведёт к выходу.",
    "Коридоры плывут, если идти слишком быстро.",
    "Шаги звучат громче около опасных мест.",
    "Правильный путь всегда темнее остальных.",
    "Мигающие панели предупреждают об ошибке.",
    "Пыль на полу скрывает механизмы — будь аккуратен.",
    "В воздухе мерцают подсказки, если присмотреться.",
    "Энергетический шум усиливается перед разгадкой.",
    "Тонкие линии на стенах ведут к центру лабиринта.",
    "Платформы исчезают за спиной — двигайся вперёд.",
    "Потоки энергии отображают путь в ритме шагов.",
    "Где нет звука — там нет выхода.",
    "Витые узоры скрывают решения головоломок.",
    "Ледяная дымка покрывает тупиковые зоны.",
    "Неоновый туман раздвигается перед тем, кто идёт правильно.",
    "Механические рычаги активируются только в нужной комнате.",
    "Цвет стен меняется при выборе правильного направления.",
    "Невидимые панели реагируют на твоё присутствие.",
    "Слишком тихие коридоры — самые опасные.",
    "Свет не падает в тупиках.",
    "Стены пульсируют, когда ты приближаешься к разгадке.",
    "Когда стены становятся гладкими, значит ты близко к цели.",
    "Лёгкая вибрация пола намекает на скрытый проход.",
    "Потускневший свет всегда ведёт к следующим испытаниям.",
    "Если шаги звучат глухо — ты идёшь правильно.",
    "Меж стен пробегают искры, отмечая безопасные тропы.",
    "Потоки пыли двигаются против ветра — следуй за ними.",
    "В углах лабиринта прячутся подсказки в виде дрожащего света.",
    "Ловушки активируются только при неверном повороте.",
    "Металлический запах усиливается там, где стоит избегать.",
    "Чем ровнее линии на стенах — тем ближе выход.",
    "Флуоресцентные следы прошлого путешественника указывают путь.",
    "Время идёт быстрее в тупиковых коридорах.",
    "Некоторые стены дышат — они отмечают опасность.",
    "Лёгкий звон появляется перед правильной развилкой.",
    "Дрейфующие частицы света отклоняются к нужному маршруту.",
    "Если туман густеет — поверни назад.",
    "Магнитные поля меняют направление компаса специально.",
    "Эхо повторяет лишь верные шаги.",
    "Платформы дрожат при приближении к ложной дороге.",
    "Тусклая вибропанель означает скрытый переход.",
    "Не приближайся к стенам, где воздух горячий.",
    "Подсвеченные узоры появляются только в зоне безопасности.",
    "Лабиринт слушает тебя — двигайся плавно.",
    "Кривизна потолка указывает на верные коридоры.",
    "Энергетические нити собираются над правильным туннелем.",
    "Затхлый запах — верный признак тупика.",
    "Платформы поют при наступлении в нужном месте.",
    "Дымка рассеивается, если идти к выходу.",
    "Внезапная тишина говорит, что путь выбран верный.",
    "Цвет пола тускнеет, когда ты отклоняешься.",
    "Острая тень на стенах намекает на ловушки впереди.",
    "Механические шестерни вращаются лишь в направлении выхода.",
    "Слабый холод исходит от ложных дверей.",
    "Живые стены сдвигаются, скрывая правильный путь.",
    "Запотевшие панели открывают секретные маршруты.",
    "Светящийся мох растёт вдоль безопасного пути.",
    "Слух подскажет, когда коридор меняет форму.",
    "Гладкие полы — зона спокойствия.",
    "Шероховатые — зона риска.",
    "Вращающиеся кристаллы указывают направление, если присмотреться.",
    "Скопления пыли образуют стрелки в воздухе.",
    "Желтоватый свет — верный знак опасности.",
    "Голубой свет зовёт вперёд.",
    "Сердцебиение лабиринта ощущается ближе к центру.",
    "Иногда шаг назад открывает новый проход.",
    "Прислушайся к механикам — они подскажут ритм пути.",
    "Потоки воздуха невидимы, но ощутимы.",
    "Скрытые платформы появляются только при движении вперёд.",
    "В темноте иногда блестит верная развилка.",
    "Лабиринт любит тех, кто не спешит.",
    "Чем меньше следов на полу — тем безопаснее.",
    "Стены запоминают твои ошибки и корректируют путь.",
    "Всё, что кажется прямым, обычно ведёт в тупик.",
    "Изломанные коридоры чаще всего выходят к цели.",
    "Следуй туда, где меньше всего слышно твои шаги.",
    "Лабиринт ненавидит шум.",
    "Неровные стены скрывают подсказки.",
    "Пары над полом закручиваются в сторону выхода.",
    "Дорожки становятся шире при верном направлении.",
    "Тонкий писк сигнализирует о невидимых ловушках.",
    "Если потолок низкий — будь осторожен.",
    "Высокий потолок — знак правильного хода.",
    "Крошечные вибрации стены означают приближение к развилке.",
    "Потоки света бегут вдоль пола, если путь верен.",
    "Углы дышат, когда рядом скрытый проход.",
    "Ощути тепло под ногами — оно ведёт к разгадке.",
    "Остывший металл означает путь назад.",
    "Следы предыдущих странников появляются на мгновение.",
    "Смотри на отражения — они никогда не врут.",
    "Тени двигаются иначе у выхода.",
    "Коридоры усложняются, если сомневаешься.",
    "Уверенные шаги упрощают маршрут.",
    "Лабиринт чувствует уверенность.",
    "И реагирует.",
    "Иногда безопасный путь скрыт за самым пугающим порогом.",
    "Иногда ловушка прячется там, где уютно.",
    "Длинный коридор всегда проверка.",
    "Короткий — шанс.",
    "Потоки света двигаются вместе с тобой, если идёшь верно.",
    "Против тебя — если ошибаешься.",
    "Игнорируй шум — он чаще всего ложный.",
    "Прислушивайся к вибрациям — они правдивы.",
    "Тепло стены означает, что рядом скрытый объект.",
    "Холод означает пустоту.",
    "Иногда пространство пульсирует вокруг тебя — используй это.",
    "Блики на полу показывают поворот заранее.",
    "Ровный пол — безопаснее, чем текстурный.",
    "Текстурный пол предупреждает о ловушках.",
    "Двоящиеся контуры уводят в сторону.",
    "Чёткие контуры ведут к выходу.",
    "Пятна света мерцают над короткими путями.",
    "Мерцание исчезает перед тупиками.",
    "Лабиринт защищается от поспешности.",
    "И помогает терпеливым.",
    "Помни: каждая ошибка — новая подсказка.",
    "Иногда нужно повернуть туда, куда совсем не хочется.",
    "Иногда нужно игнорировать очевидное.",
    "Но всегда нужно доверять ощущению правильности — лабиринт это чувствует.",
]


USERNAME_ADJECTIVES = [
    "cyber",
    "neon",
    "shadow",
    "rune",
    "arcane",
    "ember",
    "cobalt",
    "drift",
    "quantum",
    "midnight",
    "chrome",
    "glitch",
    "void",
    "crimson",
    "static",
    "stellar",
    "lunar",
    "plasma",
    "spectral",
    "optic",
    "matrix",
    "ion",
    "delta",
    "nova",
    "phantom",
    "silent",
    "rogue",
    "terminal",
    "synthetic",
    "oblivion",
    "nexus",
    "binary",
    "pixel",
    "nano",
    "astral",
    "prismatic",
    "obsidian",
    "radial",
    "aurora",
    "kinetic",
    "ashen",
    "frost",
    "wired",
    "circuit",
    "hollow",
    "helix",
    "paradox",
    "vortex",
    "zenith",
    "gamma",
    "omega",
    "infra",
    "ultra",
    "toxic",
    "diesel",
    "ferro",
    "viral",
    "radiant",
    "psi",
    "ionized",
]

USERNAME_NOUNS = [
    "runner",
    "wanderer",
    "scribe",
    "hacker",
    "caster",
    "rider",
    "seer",
    "raider",
    "scout",
    "smith",
    "nomad",
    "cipher",
    "ghost",
    "ronin",
    "operator",
    "sentinel",
    "vagrant",
    "mancer",
    "breaker",
    "stalker",
    "lurker",
    "weaver",
    "chemist",
    "architect",
    "oracle",
    "ranger",
    "harbinger",
    "pilgrim",
    "viper",
    "broker",
    "drifter",
    "tactician",
    "infiltrator",
    "saboteur",
    "engineer",
    "surgeon",
    "tracer",
    "strider",
    "watcher",
    "warden",
    "handler",
    "analyst",
    "observer",
    "conspirator",
    "agent",
    "envoy",
    "emissary",
    "courier",
    "smuggler",
    "proxy",
    "daemon",
    "construct",
    "puppeteer",
    "mechanic",
    "protector",
    "marshal",
    "reaper",
    "navigator",
    "overseer",
    "arbiter",
]


STATE_FILE = "/home/nobody/.checker_state.json"
PER_HOST_LIMIT = 6


def normalize_host(host: str) -> str:
    if not host.startswith("http"):
        host = f"http://{host}"
    parsed = urlparse(host)
    if parsed.port is None:
        host = f"{parsed.scheme}://{parsed.hostname}:3000"
    return host


def build_url(host: str, path: str) -> str:
    host = normalize_host(host)
    return urljoin(host, path)


def get_csrf(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name": "csrf-token"})
    if meta and meta.get("content"):
        return meta["content"]
    token_input = soup.find("input", attrs={"name": "authenticity_token"})
    return token_input["value"] if token_input else None


def session_with_host(host: str) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Upgrade-Insecure-Requests": "1",
        }
    )
    return s


def result(code: int, message: str = ""):
    if message:
        print(message)
    print(f"Exit with code {code}", file=sys.stderr)
    sys.exit(code)


def register_user(session: requests.Session, host: str, username: str, password: str):
    url = build_url(host, "/users")
    resp = session.get(build_url(host, "/users/sign_up.html"), headers={"Accept": session.headers["Accept"]})
    resp.raise_for_status()
    token = get_csrf(resp.text)
    if not token:
        result(MUMBLE, "CSRF token not found on sign up")
    payload = {
        "authenticity_token": token,
        "user[email]": username,
        "user[password]": password,
        "user[password_confirmation]": password,
        "commit": "Зарегистрироваться",
    }
    r = session.post(url, data=payload, allow_redirects=True)
    r.raise_for_status()
    if "Выйти" not in r.text and "Logout" not in r.text:
        result(MUMBLE, "Registration failed")


def login_user(session: requests.Session, host: str, username: str, password: str):
    resp = session.get(build_url(host, "/users/sign_in.html"), headers={"Accept": session.headers["Accept"]})
    resp.raise_for_status()
    token = get_csrf(resp.text)
    if not token:
        result(MUMBLE, "CSRF token not found on sign in")
    payload = {
        "authenticity_token": token,
        "user[email]": username,
        "user[password]": password,
        "commit": "Войти",
    }
    r = session.post(build_url(host, "/users/sign_in"), data=payload, allow_redirects=True, headers={"Accept": session.headers["Accept"]})
    r.raise_for_status()
    if "Выйти" not in r.text and "Logout" not in r.text:
        result(MUMBLE, "Login failed")


def create_task(session: requests.Session, host: str, title: str, desc: str, reward: str, task_type: str) -> int:
    resp = session.get(build_url(host, "/tasks/new"), headers={"Accept": session.headers["Accept"]})
    resp.raise_for_status()
    token = get_csrf(resp.text)
    if not token:
        result(MUMBLE, "No CSRF on task form")
    payload = {
        "authenticity_token": token,
        "task[title]": title,
        "task[task_type]": task_type,
        "task[description]": desc,
        "task[reward]": reward,
        "task[reward_visibility]": "private_reward",
        "commit": "Предложить задание",
    }
    r = session.post(build_url(host, "/tasks"), data=payload, allow_redirects=False, headers={"Accept": session.headers["Accept"]})
    if r.status_code not in (302, 303):
        result(MUMBLE, f"Task create failed status {r.status_code}")
    loc = r.headers.get("Location", "")
    m = re.search(r"/tasks/(\d+)", loc)
    if not m:
        result(MUMBLE, "Cannot parse task id")
    return int(m.group(1))


def parse_labyrinth(html: str) -> Tuple[List[List[int]], Tuple[int, int], Tuple[int, int], str]:
    soup = BeautifulSoup(html, "html.parser")
    grid_el = soup.find(class_="labyrinth-grid")
    if not grid_el:
        result(MUMBLE, "Labyrinth grid not found")
    style = grid_el.get("style", "")
    m = re.search(r"repeat\((\d+)", style)
    if not m:
        result(MUMBLE, "Width not found")
    width = int(m.group(1))
    cells = grid_el.find_all("span")
    if not cells:
        result(MUMBLE, "Cells not found")
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
        result(MUMBLE, "Start/finish missing")
    token = get_csrf(html)
    if not token:
        result(MUMBLE, "No CSRF on labyrinth page")
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
        result(MUMBLE, "No path found")
    path = []
    cur = finish
    while cur != start:
        path.append(move_dir[cur])
        cur = prev[cur]
    return "".join(reversed(path))


def solve_labyrinth(session: requests.Session, host: str, task_id: int):
    page = session.get(build_url(host, f"/tasks/{task_id}"))
    page.raise_for_status()
    grid, start, finish, token = parse_labyrinth(page.text)
    moves = bfs_path(grid, start, finish)
    solve_resp = session.post(
        build_url(host, f"/tasks/{task_id}/solve"),
        data={"authenticity_token": token, "moves": moves, "commit": "Проверить маршрут"},
        headers={"Accept": "text/vnd.turbo-stream.html, text/html"},
    )
    solve_resp.raise_for_status()
    check = session.get(build_url(host, f"/tasks/{task_id}"))
    check.raise_for_status()
    if "Награда открыта" not in check.text and "reward-panel__text" not in check.text:
        result(CORRUPT, "Solve did not unlock reward")
    return check.text


def extract_reward(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one(".reward-panel__text")
    return el.get_text(strip=True) if el else None


def playwright_visit(host: str, path: str, cookies: Dict[str, str]):
    url = build_url(host, path)
    parsed = urlparse(url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(
            [
                {"name": k, "value": v, "domain": parsed.hostname, "path": "/"}
                for k, v in cookies.items()
            ]
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(2000)
        browser.close()


def do_check(host: str):
    session = session_with_host(host)
    resp = session.get(build_url(host, "/"), headers={"Accept": session.headers["Accept"]})
    if resp.status_code != 200:
        result(MUMBLE, "Main page unreachable")
    if "Задания таверны" not in resp.text:
        result(MUMBLE, "Main page content missing")
    result(OK, "SUCCESS")


def do_put(host: str, flag_id: str, flag: str, vuln: int):
    session = session_with_host(host)
    username = believable_username()
    password = password_string()
    register_user(session, host, username, password)
    login_user(session, host, username, password)
    title = random.choice(TITLES)
    desc = random.choice(DESCS)
    task_type = "labyrinth" if vuln == 1 else "standard"
    task_id = create_task(session, host, title, desc, flag, task_type)
    playwright_visit(host, f"/tasks/{task_id}", session.cookies.get_dict())
    data = UserData(username=username, password=password, task_id=task_id, task_type=task_type, host=normalize_host(host))
    
    # XSS
    for i in range(0, 5):
        playwright_visit(host, f"/tasks/{task_id-i}", session.cookies.get_dict())

    result(OK, json.dumps(data.__dict__))

def do_get(host: str, flag_id: str, flag: str, vuln: int):
    try:
        data = json.loads(flag_id)
        user = UserData(**data)
    except Exception:
        result(CORRUPT, "Bad flag id")

    session = session_with_host(host)
    login_user(session, host, user.username, user.password)

    if user.task_type == "labyrinth":
        html = solve_labyrinth(session, host, user.task_id)
    else:
        resp = session.get(build_url(host, f"/tasks/{user.task_id}"))
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("h4", class_="comment-title") or not soup.find("textarea", id="comment_body"):
        result(MUMBLE, "Comment view error")

    reward = extract_reward(html)
    if reward != flag:
        result(CORRUPT, "Flag mismatch")

    result(OK, "SUCCESS")


def believable_username() -> str:
    adj = random.choice(USERNAME_ADJECTIVES)
    noun = random.choice(USERNAME_NOUNS)
    suffix = random.randint(10, 999)
    return f"{adj}{noun}{suffix}"


def password_string() -> str:
    length = random.randint(8, 14)
    return rnd_string(length)


def load_state() -> List[UserData]:
    if not os.path.exists(STATE_FILE):
        return []
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        users = []
        for line in lines:
            try:
                item = json.loads(line)
                users.append(UserData(**item))
            except Exception:
                continue
        return trim_per_host(users)
    except Exception:
        return []


def save_state(users: List[UserData]):
    users = trim_per_host(users)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        for u in users:
            f.write(json.dumps(u.__dict__) + "\n")


def trim_per_host(users: List[UserData]) -> List[UserData]:
    """Keep only the last PER_HOST_LIMIT users per host, preserving overall order."""
    seen = {}
    kept_reversed: List[UserData] = []
    for u in reversed(users):
        count = seen.get(u.host, 0)
        if count < PER_HOST_LIMIT:
            kept_reversed.append(u)
            seen[u.host] = count + 1
    return list(reversed(kept_reversed))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["check", "put", "get"])
    parser.add_argument("host")
    parser.add_argument("flag_id", nargs="?")
    parser.add_argument("flag", nargs="?")
    parser.add_argument("vuln", nargs="?", type=int)
    args = parser.parse_args()

    try:
        if args.action == "check":
            do_check(args.host)
        elif args.action == "put":
            if not args.flag_id or not args.flag or args.vuln is None:
                result(CHECKER_ERROR, "put requires flag_id flag vuln")
            do_put(args.host, args.flag_id, args.flag, args.vuln)
        elif args.action == "get":
            if not args.flag_id or not args.flag or args.vuln is None:
                result(CHECKER_ERROR, "get requires flag_id flag vuln")
            do_get(args.host, args.flag_id, args.flag, args.vuln)
        else:
            result(CHECKER_ERROR, "Unknown action")
    except requests.Timeout as e:
        print(f"requests timeout: {e}", file=sys.stderr)
        result(DOWN, "Timeout")
    except requests.exceptions.ConnectionError as e:
        print(f"connection error: {e}", file=sys.stderr)
        result(DOWN, "Connection error")
    except SystemExit:
        raise
    except Exception as e:
        print(f"INTERNAL ERROR: {e}", file=sys.stderr)
        result(CHECKER_ERROR, "INTERNAL ERROR")


if __name__ == "__main__":
    main()
