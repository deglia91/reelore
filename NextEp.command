#!/bin/zsh
set -e

cd "$(dirname "$0")"

if [[ ! -x ".venv/bin/uvicorn" ]]; then
  echo "NextEp: ambiente virtuale non pronto."
  echo "Esegui prima: source .venv/bin/activate && make install"
  read "?Premi Invio per chiudere..."
  exit 1
fi

LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"

echo "NextEp in avvio..."
echo "Mac:    http://127.0.0.1:8010"
if [[ -n "$LAN_IP" ]]; then
  echo "iPhone: http://$LAN_IP:8010"
fi

(sleep 1; open "http://127.0.0.1:8010") &

export PATH="$PWD/.venv/bin:$PATH"
exec make run-lan
