# Reelore

Reelore is a local-first personal media tracker for TV series, films, books, audiobooks,
manga, and comics.

The first vertical slice focuses on TV series while the domain remains media-agnostic.

## Development

Requires Python 3.13+.

```bash
python -m venv .venv
source .venv/bin/activate
make install
make verify
```

Personal tracking data will remain authoritative locally. External metadata providers are
replaceable sources, not the owner of the user's library.
