#!/usr/bin/env python3
"""Check relays.json: the same rules as the official relays apply (og-relay registry.go), then probe each active entry.
check_relays.py relays.json            -> exit 1 on a rule error or a dead NEW entry (pull requests)
check_relays.py relays.json --nightly  -> marks entries down / back up, drops those down for 30 days (rewrites the file)"""
import datetime, json, re, socket, sys

OFFICIAL = {"EU", "US", "AS", "SA", "OC", "AF"}
ID = re.compile(r"^[A-Z][A-Z0-9]{1,5}$")

def probe(e):
    try:
        with socket.create_connection((e["host"], int(e["port"])), timeout=4) as s:
            s.settimeout(4)
            s.sendall(b"OGR1 PROBE\n")
            return s.recv(256).decode(errors="replace").strip() == "PROBE " + e["id"]
    except (OSError, ValueError, KeyError):
        return False

def main():
    path, nightly = sys.argv[1], "--nightly" in sys.argv
    data = json.load(open(path))
    errs, seen = [], set()
    for e in data.get("relays", []):
        i = str(e.get("id", ""))
        if not ID.match(i): errs.append(f"{i!r}: bad id")
        elif i in OFFICIAL: errs.append(f"{i}: an official id")
        elif i in seen: errs.append(f"{i}: listed twice")
        host, port = str(e.get("host", "")), e.get("port")
        if not host or any(ch in host for ch in " /:,=") or not isinstance(port, int) or not 0 < port < 65536:
            errs.append(f"{i}: bad host or port")
        seen.add(i)
    if errs:
        print("\n".join(errs)); return 1
    today = datetime.date.today().isoformat()
    bad, keep = [], []
    for e in data["relays"]:
        if e.get("status") == "disabled":
            keep.append(e); continue
        ok = probe(e)
        print(f"{e['id']:7} {e['host']}:{e['port']}  {'live' if ok else 'NOT ANSWERING'}")
        if nightly:
            if ok:
                e.pop("down_since", None); e.pop("status", None)
            else:
                e["status"] = "down"; e.setdefault("down_since", today)
                if (datetime.date.today() - datetime.date.fromisoformat(e["down_since"])).days > 30:
                    print(f"  {e['id']}: down for a month, removed"); continue
        elif not ok and e.get("status") != "down":
            bad.append(e["id"])
        keep.append(e)
    if nightly:
        data["relays"] = keep
        with open(path, "w") as f: json.dump(data, f, indent=2); f.write("\n")
    if bad:
        print("not answering PROBE <id>:", ", ".join(bad)); return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
