# NextEp

NextEp is a local-first personal TV series tracker. The repository and Python package keep the
technical name `reelore`, while the product is called **NextEp**.

> NextEp è il tuo tracker personale di serie TV: ricorda cosa hai visto, dove sei arrivato e cosa
> esce dopo.

## Version 1.0

NextEp 1.0 includes:

- TV series search and import through TVmaze;
- optional Italian metadata and streaming availability through TMDB;
- personal library states: planned, in progress, up to date, completed, paused and dropped;
- episode-by-episode progress tracking with future-episode protection;
- automatic completion handling and status reconciliation after catalog refreshes;
- append-only watch history with distinct rewatches;
- personal Top 10;
- upcoming-release calendar with direct episode links and provider information;
- recent and upcoming releases on the home page;
- release reminder preferences and macOS notifications when available;
- related and franchise titles;
- personal watch statistics, including total watch time, total views, unique episodes and
  rewatches;
- responsive desktop and mobile web interface.

Personal tracking data is authoritative in the local SQLite database. External services provide
replaceable metadata and availability information; they do not own the user's library or watch
history.

## Development

Requires Python 3.13+.

```bash
python -m venv .venv
source .venv/bin/activate
make install
make verify
```

`make verify` checks formatting, linting, typing and the complete automated test suite.

## Local configuration

NextEp reads optional local configuration from a `.env` file in the repository root. The file is
ignored by Git so secrets stay local.

Copy `.env.example` to `.env` and set `TMDB_API_TOKEN` to a TMDB API read access token to enable
Italian metadata and streaming availability powered by TMDB/JustWatch. Environment variables
already exported in the shell take precedence over `.env` values.

## Run the web app

```bash
make run
```

Then open `http://127.0.0.1:8010` in a browser.

By default NextEp stores its SQLite database in `data/reelore.db`. Override it with the
`REELORE_DB_PATH` environment variable when needed.

## Main sections

- `/` — Home
- `/library` — Library
- `/calendar` — Upcoming releases
- `/history` — Watch history and rewatches
- `/stats` — Personal watch statistics
- `/top-ten` — Personal Top 10
- `/reminders` — Release reminder preferences

## Architecture

The project follows a local-first, provider-independent architecture. SQLite is authoritative for
personal state, catalog adapters stay behind application boundaries, and the web application is
assembled from a single composition root.

The current product scope is TV series. The domain leaves room for other media types in future
versions without requiring NextEp 1.0 to pretend it already tracks everything humans have ever
watched, read or regrettably binged.
