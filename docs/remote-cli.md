# Remote CLI (mosh + tmux)

This guide shows a resilient SSH workflow for mobile connections using mosh + tmux. It keeps sessions alive when your network drops or your phone sleeps.

## Install

macOS:

```bash
brew install mosh tmux
```

Ubuntu/Debian:

```bash
sudo apt-get update && sudo apt-get install -y mosh tmux
```

## Connect with mosh

Replace `your-host` with a Headscale IP or MagicDNS name.

```bash
mosh your-user@your-host
```

If your SSH server uses a non-default port:

```bash
mosh --ssh="ssh -p 2222" your-user@your-host
```

## Keep sessions with tmux

Start a named session:

```bash
tmux new -s codebeep
```

Detach:

```bash
tmux detach
```

Reattach later:

```bash
tmux attach -t codebeep
```

## Why this helps

- mosh survives network changes (Wi-Fi to cellular).
- tmux keeps your session alive across disconnects.
- Together, you can resume long-running tasks safely.
