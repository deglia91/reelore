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


def test_release_reminder_settings_get_reads_current_preferences() -> None:
    store = StubPreferences()
    store.preferences = ReleaseReminderPreferences(today_enabled=False, tomorrow_enabled=True)
    app = FastAPI()
    install_release_reminder_routes(app, store)

    response = TestClient(app).get("/reminders")

    assert response.status_code == 200
    assert 'name="today_enabled" value="true" checked' not in response.text
    assert 'name="tomorrow_enabled" value="true" checked' in response.text


def test_release_reminder_settings_post_saves_checkbox_values() -> None:
    store = StubPreferences()
    app = FastAPI()
    install_release_reminder_routes(app, store)

    response = TestClient(app).post(
        "/reminders",
        data={"today_enabled": "true"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/reminders"
    assert store.preferences == ReleaseReminderPreferences(
        today_enabled=True,
        tomorrow_enabled=False,
    )
