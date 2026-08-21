from reelore.application.release_reminders import ReleaseReminderPreferences
from reelore.web_release_reminders import render_release_reminder_settings_page


def test_release_reminder_settings_page_shows_current_preferences() -> None:
    page = render_release_reminder_settings_page(
        ReleaseReminderPreferences(today_enabled=True, tomorrow_enabled=False)
    )

    assert "Promemoria uscite" in page
    assert 'name="today_enabled"' in page
    assert 'name="tomorrow_enabled"' in page
    assert 'name="today_enabled" value="true" checked' in page
    assert 'name="tomorrow_enabled" value="true" checked' not in page
    assert 'action="/reminders"' in page
    assert "Salva preferenze" in page
