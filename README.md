# 🌸 Whimsy Recon

A beginner-friendly **network reconnaissance learning tool** for Linux, with a
whimsical terminal theme and a Cinnamon panel applet.

It teaches the basics of networking and recon: your IP and interfaces, host
discovery (ping sweeps), port scanning, banner grabbing, and what each finding
means.

> ⚠️ **Ethics first.** Whimsy Recon only touches **loopback (127.0.0.0/8)** and
> **private LAN** addresses (10.x, 172.16–31.x, 192.168.x). It refuses public
> IPs on purpose. Only use it on machines and networks you own or have written
> permission to test. Good places to practice:
> - your own computer (`127.0.0.1`)
> - your home router and devices
> - virtual machines or Docker containers in your own lab

## Features

- 🌷 Show your machine's hostname and local IP
- 🌿 Discover live hosts on a private subnet (max /24)
- 🍄 Scan common ports (1–1024) on an allowed target
- 🦋 Grab service banners to see what is running
- 🌙 Built-in "learn" mode that explains each concept
- 🎀 Cinnamon panel applet that shows your IP and launches the tool

## Requirements

- Linux Mint with Cinnamon (tested on Cinnamon 5.8+ / 6.x)
- Python 3.8+ (preinstalled on Mint)
- `ping` (preinstalled, from `iputils-ping`)

## Install

```bash
git clone https://github.com/yourname/whimsy-recon.git
cd whimsy-recon

# 1. Install the CLI tool
mkdir -p ~/.local/share/whimsy-recon
cp whimsy_recon.py ~/.local/share/whimsy-recon/
chmod +x ~/.local/share/whimsy-recon/whimsy_recon.py

# 2. Install the Cinnamon applet
cp -r whimsy-recon@yourname ~/.local/share/cinnamon/applets/
```

Then right-click your panel → **Applets** → find **Whimsy Recon** → add it.
If it does not appear, press `Alt+F2`, type `r`, and press Enter to restart Cinnamon.

## Usage

Run the CLI directly:

```bash
python3 ~/.local/share/whimsy-recon/whimsy_recon.py
```

Or click the 🌸 applet in your panel.

## Project structure

| File | Purpose |
|------|---------|
| `whimsy_recon.py` | CLI learning tool and whimsy theme |
| `whimsy-recon@yourname/applet.js` | Cinnamon panel applet logic |
| `whimsy-recon@yourname/metadata.json` | Applet metadata for Cinnamon |

## Customizing the theme

Edit the `Theme` class in `whimsy_recon.py`. Each value is an ANSI color code,
so you can swap in your own palette.

## Roadmap

- [ ] Export scan results to a text file
- [ ] Add a `--quiet` flag for scripting
- [ ] Add more "learn" lessons

## Disclaimer

This tool is for education and authorized testing only. The author is not
responsible for misuse. Scanning networks you do not own or have permission to
test may be illegal.

## License

MIT
