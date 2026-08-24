import os
import sys
from pathlib import Path

from pytest import MonkeyPatch
from starlette.routing import Route

import reelore.bootstrap as bootstrap
from reelore.bootstrap import _load_env_file, build_app


def test_build_app_initializes_local_database(tmp_path: Path) -> None:
    database_path = tmp_path / "reelore.db"

    app = build_app(database_path)

    assert app.title == "NextEp"
    assert database_path.exists()
    assert any(isinstance(route, Route) and route.path == "/reminders" for route in app.routes)
    assert any(isinstance(route, Route) and route.path == "/stats" for route in app.routes)


def test_build_app_starts_catalog_refresh(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    started: list[tuple[object, object, object | None]] = []

    def fake_start_catalog_refresh(
        service: object,
        reconciliation: object,
        reminders: object | None = None,
    ) -> None:
        started.append((service, reconciliation, reminders))

    monkeypatch.setattr(bootstrap, "start_catalog_refresh", fake_start_catalog_refresh)

    build_app(tmp_path / "reelore.db")

    assert len(started) == 1
    assert started[0][0] is not None
    assert started[0][1] is not None


def test_build_app_wires_release_reminders_on_macos(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    refresh_reminders: list[object | None] = []
    scheduled_reminders: list[object] = []

    def fake_start_catalog_refresh(
        service: object,
        reconciliation: object,
        reminders: object | None = None,
    ) -> None:
        refresh_reminders.append(reminders)

    def fake_start_release_reminder_scheduler(reminders: object) -> None:
        scheduled_reminders.append(reminders)

    monkeypatch.setattr(bootstrap, "start_catalog_refresh", fake_start_catalog_refresh)
    monkeypatch.setattr(
        bootstrap,
        "start_release_reminder_scheduler",
        fake_start_release_reminder_scheduler,
    )
    monkeypatch.setattr(sys, "platform", "darwin")

    build_app(tmp_path / "reelore.db")

    assert len(refresh_reminders) == 1
    assert refresh_reminders[0] is not None
    assert scheduled_reminders == [refresh_reminders[0]]


def test_load_env_file_sets_values_without_overriding_environment(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "# local configuration\nTMDB_API_TOKEN=from-file\nREELORE_DB_PATH='custom/reelore.db'\n",
        encoding="utf-8",
    )
    previous_token = os.environ.get("TMDB_API_TOKEN")
    previous_database = os.environ.get("REELORE_DB_PATH")
    os.environ["TMDB_API_TOKEN"] = "from-environment"
    os.environ.pop("REELORE_DB_PATH", None)
    try:
        _load_env_file(env_path)

        assert os.environ["TMDB_API_TOKEN"] == "from-environment"
        assert os.environ["REELORE_DB_PATH"] == "custom/reelore.db"
    finally:
        if previous_token is None:
            os.environ.pop("TMDB_API_TOKEN", None)
        else:
            os.environ["TMDB_API_TOKEN"] = previous_token
        if previous_database is None:
            os.environ.pop("REELORE_DB_PATH", None)
        else:
            os.environ["REELORE_DB_PATH"] = previous_database
