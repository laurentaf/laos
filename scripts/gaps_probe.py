#!/usr/bin/env python3
"""Probe dashboard (8 itens) + console send + project detail (custo/duracao).
Writes .laos/gaps-probe.log"""

from __future__ import annotations

import pathlib
import urllib.request
import urllib.parse

LOG = pathlib.Path(r"F:\projects\laos-v2\.laos\gaps-probe.log")


def probe(label, url, method="GET", data=None):
    try:
        if method == "POST":
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                         headers={"Content-Type": "application/x-www-form-urlencoded"})
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", errors="replace")
            markers = [m for m in ["Entrega por projeto", "custo total", "duração total",
                                   "console", "enviar", "pronto", "faltando"] if m in body]
            LOG.parent.mkdir(parents=True, exist_ok=True)
            with LOG.open("a", encoding="utf-8") as f:
                f.write(f"{label}: HTTP {r.status} ({len(body)}B) markers={markers}\n")
            return True
    except Exception as e:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{label}: ERR {type(e).__name__} {str(e)[:150]}\n")
        return False


def main() -> int:
    probe("dashboard", "http://127.0.0.1:7331/dashboard")
    probe("detail", "http://127.0.0.1:7331/projects/limpeza-casa")
    probe("console", "http://127.0.0.1:7331/projects/limpeza-casa/console")
    probe("console-send", "http://127.0.0.1:7331/projects/limpeza-casa/console/send",
          method="POST", data={"message": "teste console"})
    probe("handoff", "http://127.0.0.1:7331/projects/limpeza-casa/handoff")
    print("DONE (see .laos/gaps-probe.log)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
