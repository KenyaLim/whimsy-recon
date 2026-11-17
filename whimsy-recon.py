#!/usr/bin/env python3
"""
Whimsy Recon 🌸 - a beginner-friendly network recon LEARNING tool.

Scope: loopback and private (LAN) addresses only. Public IPs are refused.
Only use on machines and networks you own or have written permission to test.
"""

import concurrent.futures
import ipaddress
import shutil
import socket
import subprocess
import sys


# ---------- whimsy theme (ANSI colors) ----------
class Theme:
    PINK = "\033[95m"
    CYAN = "\033[96m"
    GOLD = "\033[93m"
    MINT = "\033[92m"
    ROSE = "\033[91m"
    LAVENDER = "\033[94m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


T = Theme

BANNER = r"""
   ✿ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ✿
        W H I M S Y   R E C O N
   ✿ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ✿
"""

MAX_PORT = 1024
PORT_TIMEOUT = 0.5
SERVICE_NAMES = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 139: "netbios", 143: "imap", 443: "https",
    445: "smb", 631: "ipp (printing)", 3306: "mysql", 3389: "rdp",
    5432: "postgres", 8080: "http-alt",
}

LESSONS = {
    "ip": "An IP address is like a house number for a device on a network. "
          "Private ranges (10.x, 172.16-31.x, 192.168.x) are only reachable "
          "inside your home or office network.",
    "ports": "A port is a numbered door on a device. Services like web servers "
             "listen on known ports (80 for HTTP, 443 for HTTPS, 22 for SSH). "
             "An 'open' port means something is listening there.",
    "sweep": "A ping sweep sends a tiny 'are you there?' message to every "
             "address in a range. Devices that answer are alive. This is how "
             "you map what is on your network.",
    "banner": "A banner is the greeting a service sends when you connect. "
              "It often reveals the software and version, which is why "
              "keeping software updated matters.",
    "ethics": "Recon on systems you do not own or have permission to test is "
              "illegal in most countries. Always get written permission first, "
              "and practice in your own lab.",
}


def color(text, c):
    return f"{c}{text}{T.RESET}"


def print_banner():
    print(color(BANNER, T.PINK + T.BOLD))
    print(color("  learn networking · scan only what you own ♡\n", T.DIM))


# ---------- scope and safety ----------
def in_scope(ip_str):
    """Only loopback and private addresses are allowed."""
    ip = ipaddress.ip_address(ip_str)
    return ip.is_loopback or ip.is_private


def authorize(target):
    """Resolve a target and make sure it is in scope. Returns IP or None."""
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(color("  ✗ Could not resolve that name.", T.ROSE))
        return None

    if not in_scope(ip):
        print(color(f"  ✗ {ip} is a public address. Whimsy Recon only touches "
                    "your own machine or private network.", T.ROSE))
        return None

    print(color(f"  ✓ {target} → {ip} is local/private. Good to go.", T.MINT))
    return ip


def confirm_permission():
    print(color("Before we start:", T.GOLD))
    print("  This tool is for YOUR machine, YOUR lab, or a network you have")
    print("  permission to test.\n")
    answer = input(color("  Type 'i agree' to continue: ", T.CYAN)).strip().lower()
    return answer == "i agree"


# ---------- features ----------
def show_local_info():
    hostname = socket.gethostname()
    try:
        # Opening a UDP socket does not send packets. It just asks the OS
        # which local address would be used to reach the network.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            local_ip = s.getsockname()[0]
    except OSError:
        local_ip = "127.0.0.1"

    print(color("\n🌷 Your machine", T.PINK + T.BOLD))
    print(f"  Hostname : {hostname}")
    print(f"  Local IP : {local_ip}")
    print(color("\n  Tip: " + LESSONS["ip"], T.DIM))


def _check_port(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(PORT_TIMEOUT)
        return port if s.connect_ex((ip, port)) == 0 else None


def scan_ports(ip, start=1, end=MAX_PORT):
    if start < 1 or end > MAX_PORT or start > end:
        print(color(f"  ✗ Ports must be between 1 and {MAX_PORT}.", T.ROSE))
        return

    ports = range(start, end + 1)
    print(color(f"\n🍄 Scanning {ip} ports {start}-{end}...", T.LAVENDER))

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        results = [p for p in ex.map(lambda p: _check_port(ip, p), ports) if p]

    if not results:
        print(color("  No open ports found in that range.", T.DIM))
        return

    for port in results:
        name = SERVICE_NAMES.get(port, "unknown")
        print(color(f"  ● {port:<6} open   ({name})", T.MINT))
    print(color("\n  Tip: " + LESSONS["ports"], T.DIM))


def grab_banner(ip, port, timeout=2):
    try:
        with socket.create_connection((ip, port), timeout=timeout) as s:
            if port in (80, 8080):
                s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            data = s.recv(256)
            first_line = data.decode(errors="replace").strip().splitlines()[0]
            return first_line
    except (OSError, IndexError):
        return "(no banner)"


def banner_check(ip):
    port = input(color("  Port to check (e.g. 22, 80): ", T.CYAN)).strip()
    if not port.isdigit() or not (1 <= int(port) <= MAX_PORT):
        print(color("  ✗ Enter a port between 1 and 1024.", T.ROSE))
        return
    print(color(f"\n🦋 Grabbing banner from {ip}:{port}...", T.LAVENDER))
    print(f"  {grab_banner(ip, int(port))}")
    print(color("\n  Tip: " + LESSONS["banner"], T.DIM))


def _ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
        return ip if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def sweep_subnet(cidr):
    if shutil.which("ping") is None:
        print(color("  ✗ 'ping' not found. Install it with: sudo apt install iputils-ping", T.ROSE))
        return

    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        print(color("  ✗ That is not a valid network. Example: 192.168.1.0/24", T.ROSE))
        return

    if not net.is_private:
        print(color("  ✗ Only private networks are allowed.", T.ROSE))
        return

    hosts = [str(h) for h in net.hosts()]
    if len(hosts) > 254:
        print(color("  ✗ Keep it to a /24 or smaller (254 hosts max).", T.ROSE))
        return

    print(color(f"\n🌿 Sweeping {net} ({len(hosts)} addresses)...", T.LAVENDER))
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as ex:
        alive = [h for h in ex.map(_ping, hosts) if h]

    if not alive:
        print(color("  No devices responded.", T.DIM))
    else:
        for ip in alive:
            print(color(f"  ● {ip} is alive", T.MINT))
    print(color("\n  Tip: " + LESSONS["sweep"], T.DIM))


def show_lessons():
    print(color("\n🌙 Learn mode", T.PINK + T.BOLD))
    for topic, text in LESSONS.items():
        print(color(f"\n  [{topic}]", T.GOLD))
        print(f"  {text}")
    print()


# ---------- menu ----------
MENU = """
  1) 🌷 Show my machine info
  2) 🌿 Sweep a private network (ping)
  3) 🍄 Scan ports on a target
  4) 🦋 Grab a service banner
  5) 🌙 Learn mode
  0) 🌸 Quit
"""


def main():
    print_banner()

    if not confirm_permission():
        print(color("\nNo permission confirmed. Goodbye! 🌸\n", T.DIM))
        sys.exit(0)

    while True:
        print(color(MENU, T.CYAN))
        choice = input(color("  Choose: ", T.PINK + T.BOLD)).strip()

        if choice == "1":
            show_local_info()

        elif choice == "2":
            cidr = input(color("  Network (e.g. 192.168.1.0/24): ", T.CYAN)).strip()
            sweep_subnet(cidr)

        elif choice in ("3", "4"):
            target = input(color("  Target (e.g. 127.0.0.1 or 192.168.1.10): ", T.CYAN)).strip()
            ip = authorize(target)
            if ip:
                if choice == "3":
                    start = input(color("  Start port [1]: ", T.CYAN)).strip() or "1"
                    end = input(color(f"  End port [{MAX_PORT}]: ", T.CYAN)).strip() or str(MAX_PORT)
                    if start.isdigit() and end.isdigit():
                        scan_ports(ip, int(start), int(end))
                    else:
                        print(color("  ✗ Ports must be numbers.", T.ROSE))
                else:
                    banner_check(ip)

        elif choice == "5":
            show_lessons()

        elif choice == "0":
            print(color("\nStay curious and stay ethical. 🌸✿\n", T.PINK))
            break

        else:
            print(color("  Hmm, that is not an option. Try again!", T.ROSE))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(color("\n\nInterrupted. Bye! 🌸\n", T.PINK))
