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

## Local configuration

NextEp reads optional local configuration from a `.env` file in the repository root.
The file is ignored by Git so secrets stay local.

Copy `.env.example` to `.env` and set `TMDB_API_TOKEN` to a TMDB API read access token
to enable Italian metadata and streaming availability powered by TMDB/JustWatch.
Environment variables already exported in the shell take precedence over `.env` values.

## Run the web app

```bash
make run
```

Then open `http://127.0.0.1:8010` in a browser. The first web slice can search TVmaze,
show provider results, add a selected series to the local library, and list imported media.

By default Reelore stores its SQLite database in `data/reelore.db`. Override it with the
`REELORE_DB_PATH` environment variable when needed.

Personal tracking data remains authoritative locally. External metadata providers are
replaceable sources, not the owner of the user's library.
