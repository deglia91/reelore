from fastapi import FastAPI
from fastapi.testclient import TestClient

from reelore.application.release_reminders import ReleaseReminderPreferences
from reelore.web_release_reminders import install_release_reminder_routes


class StubPreferences:
    def __init__(self) -> None:
        self.preferences = ReleaseReminderPreferences()

    def get_preferences(self) -> ReleaseReminderPreferences:
        return self.preferences

    def save_preferences(self, preferences: ReleaseReminderPreferences) -> None:
        self.preferences = preferences


class StubTestSender:
    def __init__(self) -> None:
        self.calls = 0

    def send_test(self) -> None:
        self.calls += 1


def test_release_reminder_settings_get_reads_current_preferences() -> None:
    store = StubPreferences()
    store.preferences = ReleaseReminderPreferences(today_enabled=False, tomorrow_enabled=True)
    app = FastAPI()
    install_release_reminder_routes(app, store, notifications_available=True)

    response = TestClient(app).get("/reminders")

    assert response.status_code == 200
    assert 'name="today_enabled" value="true" checked' not in response.text
    assert 'name="tomorrow_enabled" value="true" checked' in response.text
    assert "Notifiche di sistema attive su questo Mac" in response.text


def test_release_reminder_settings_post_saves_checkbox_values() -> None:
    store = StubPreferences()
    app = FastAPI()
    install_release_reminder_routes(app, store, notifications_available=True)

    response = TestClient(app).post(
        "/reminders",
        data={"today_enabled": "true"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/reminders?saved=true"
    assert store.preferences == ReleaseReminderPreferences(
        today_enabled=True,
        tomorrow_enabled=False,
    )


def test_release_reminder_settings_get_shows_saved_confirmation() -> None:
    app = FastAPI()
    install_release_reminder_routes(app, StubPreferences(), notifications_available=True)

    response = TestClient(app).get("/reminders?saved=true")

    assert response.status_code == 200
    assert "Preferenze salvate" in response.text


def test_release_reminder_settings_can_send_test_notification() -> None:
    sender = StubTestSender()
    app = FastAPI()
    install_release_reminder_routes(
        app,
        StubPreferences(),
        notifications_available=True,
        test_sender=sender,
    )

    response = TestClient(app).post("/reminders/test", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/reminders?tested=true"
    assert sender.calls == 1


def test_release_reminder_settings_hide_test_action_without_sender() -> None:
    app = FastAPI()
    install_release_reminder_routes(app, StubPreferences(), notifications_available=False)

    response = TestClient(app).get("/reminders")

    assert response.status_code == 200
    assert 'action="/reminders/test"' not in response.text
