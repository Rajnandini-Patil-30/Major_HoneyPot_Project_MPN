"""
HoneyShield — Final Module: Live Threat Watcher

Real-time SOC console. Tails the honeypot database and prints every NEW
attack event as it lands, with geo enrichment, credential details, payload
analysis, and MITRE ATT&CK technique tagging.

Run this AFTER the honeypot engine is live. Every real connection to
2222 / 8080 / 2121 / 2323 — localhost, LAN, or public internet — shows up
here within 2 seconds.

Usage:
    python -m tests.live_threat_watcher
    python -m tests.live_threat_watcher --since 1h   # replay last hour first
"""
import argparse
import ctypes
import io
import sys
import time
from datetime import datetime, timedelta

# Force UTF-8 stdout on Windows so colored arrows/flags render
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from database.connection import get_db_manager, init_db
from database.models import (
    AttackEvent, Credential, Command, HTTPRequest, GeoData,
    Session as AttackSession,
)

# ---- ANSI colors ----
RESET, BOLD, DIM = "\033[0m", "\033[1m", "\033[2m"
RED, GREEN, YELLOW = "\033[91m", "\033[92m", "\033[93m"
BLUE, MAGENTA, CYAN, WHITE = "\033[94m", "\033[95m", "\033[96m", "\033[97m"

PROTO_COLOR = {"SSH": RED, "HTTP": MAGENTA, "FTP": YELLOW, "Telnet": CYAN, "SMTP": BLUE}


def enable_windows_ansi():
    """Turn on VT100 processing so Windows consoles render colors."""
    if sys.platform != "win32":
        return
    try:
        k32 = ctypes.windll.kernel32
        handle = k32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if k32.GetConsoleMode(handle, ctypes.byref(mode)):
            k32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VT
    except Exception:
        pass


def classify_threat(evt, cred, http_req, cmd):
    """Map event to a MITRE ATT&CK technique."""
    if cmd:
        c = (cmd.command or "").lower()
        if any(x in c for x in ("wget", "curl", "tftp")):
            return "T1105 Ingress Tool Transfer"
        if "passwd" in c or "shadow" in c:
            return "T1003 OS Credential Dumping"
        if c in ("whoami", "id", "uname -a"):
            return "T1082 System Info Discovery"
        if c.startswith(("ls", "cd")):
            return "T1083 File/Directory Discovery"
        if "rm -rf" in c or "chmod" in c:
            return "T1222 File Permissions Modification"
        return "T1059 Command Execution"
    if http_req:
        p = (http_req.path or "").lower()
        if any(x in p for x in (".env", ".git", "config.php", "web.config", "backup")):
            return "T1592 Gather Victim Information"
        if "../" in p or "%2e" in p:
            return "T1083 Path Traversal"
        if any(x in p for x in ("union select", "' or", "1=1", "'--")):
            return "T1190 SQL Injection"
        if "<script" in p or "onerror=" in p:
            return "T1059.007 Cross-Site Scripting"
        if any(x in p for x in ("/admin", "/wp-admin", "/phpmyadmin", "/solr")):
            return "T1190 Exploit Public App"
        return "T1595 Active Scanning"
    if cred:
        return "T1110 Brute Force"
    return "T1021 Remote Services"


def fmt_geo(geo):
    if not geo:
        return f"{DIM}geo: unknown (private/unresolved IP){RESET}"
    return (f"{BOLD}{geo.country_code or '??'}{RESET} "
            f"{geo.country or '?'}/{geo.city or '?'} · "
            f"{DIM}{geo.isp or ''}{RESET}")


def print_banner(args):
    print(f"\n{BOLD}{CYAN}{'='*78}{RESET}")
    print(f"{BOLD}{CYAN}  HoneyShield — Live Threat Watcher{RESET}")
    print(f"{BOLD}{CYAN}  Real-time SOC feed. New attacks print within 2s of capture.{RESET}")
    print(f"{BOLD}{CYAN}{'='*78}{RESET}")
    if args.since:
        print(f"{DIM}  Replaying events from last {args.since}…{RESET}")
    print(f"{DIM}  Polling every {args.interval}s  ·  Ctrl+C to stop{RESET}\n")


def print_event(evt, session, cred, http_req, cmd, geo):
    ts = evt.timestamp.strftime("%H:%M:%S")
    proto_col = PROTO_COLOR.get(evt.protocol, WHITE)
    technique = classify_threat(evt, cred, http_req, cmd)
    severity_col = RED if any(x in technique for x in ("Injection", "Credential", "Transfer")) else YELLOW

    print(f"{DIM}{ts}{RESET} "
          f"{proto_col}{BOLD}[{evt.protocol:<6}]{RESET} "
          f"{BOLD}{evt.ip:<15}{RESET} -> {fmt_geo(geo)}")
    print(f"           {severity_col}! {technique}{RESET}")

    if cred:
        status = f"{GREEN}SUCCESS{RESET}" if evt.success else f"{RED}FAILED{RESET}"
        print(f"           {DIM}creds:{RESET} {CYAN}{cred.username}{RESET} / "
              f"{YELLOW}{cred.password or '<empty>'}{RESET}  [{status}]")
    if http_req:
        body_preview = f"  body={http_req.payload[:60]}" if http_req.payload else ""
        print(f"           {DIM}http :{RESET} {MAGENTA}{http_req.method}{RESET} "
              f"{http_req.path}{DIM}{body_preview}{RESET}")
    if cmd:
        out = (cmd.output or "")[:70].replace("\n", " | ")
        print(f"           {DIM}cmd  :{RESET} {WHITE}$ {cmd.command}{RESET}")
        if out:
            print(f"           {DIM}out  : {out}{RESET}")
    if session and session.session_id:
        print(f"           {DIM}session: {session.session_id[:50]}{RESET}")
    print()


def fetch_new_events(db, last_id):
    events = (db.query(AttackEvent)
                .filter(AttackEvent.id > last_id)
                .order_by(AttackEvent.id.asc())
                .limit(200).all())
    enriched = []
    for evt in events:
        cred = db.query(Credential).filter_by(event_id=evt.id).first()
        http_req = db.query(HTTPRequest).filter_by(event_id=evt.id).first()
        cmd = db.query(Command).filter_by(event_id=evt.id).first()
        geo = db.query(GeoData).filter_by(ip=evt.ip).first()
        sess = (db.query(AttackSession).filter_by(id=evt.session_id).first()
                if evt.session_id else None)
        enriched.append((evt, sess, cred, http_req, cmd, geo))
    return enriched


def starting_event_id(db, since_arg):
    if not since_arg:
        last = db.query(AttackEvent).order_by(AttackEvent.id.desc()).first()
        return last.id if last else 0

    unit = since_arg[-1].lower()
    val = int(since_arg[:-1])
    delta = {"s": timedelta(seconds=val),
             "m": timedelta(minutes=val),
             "h": timedelta(hours=val)}[unit]
    cutoff = datetime.utcnow() - delta
    row = (db.query(AttackEvent)
             .filter(AttackEvent.timestamp < cutoff)
             .order_by(AttackEvent.id.desc()).first())
    return row.id if row else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="Replay events from last N[s|m|h]")
    ap.add_argument("--interval", type=float, default=2.0)
    args = ap.parse_args()

    enable_windows_ansi()
    init_db()
    mgr = get_db_manager()

    print_banner(args)
    with mgr.get_db_session() as db:
        last_id = starting_event_id(db, args.since)
        if args.since:
            print(f"{DIM}  Cursor: event id > {last_id}{RESET}\n")

    total = 0
    try:
        while True:
            with mgr.get_db_session() as db:
                for tup in fetch_new_events(db, last_id):
                    print_event(*tup)
                    last_id = tup[0].id
                    total += 1
            sys.stdout.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n{BOLD}{GREEN}[stopped] Saw {total} new events this session.{RESET}\n")


if __name__ == "__main__":
    main()
