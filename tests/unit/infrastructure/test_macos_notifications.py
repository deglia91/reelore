from datetime import date

from reelore.application.release_reminders import ReleaseReminder, ReleaseReminderKind
from reelore.infrastructure.macos_notifications import MacOSReleaseReminderNotifier


def _reminder(kind: ReleaseReminderKind) -> ReleaseReminder:
    return ReleaseReminder(
        media_id="tvmaze:1",
        series_title='Example "Show"',
        season_number=2,
        episode_number=3,
        episode_title="The Return",
        airdate=date(2026, 8, 22),
        kind=kind,
    )


def test_macos_notifier_sends_tomorrow_release_to_notification_center() -> None:
    commands: list[list[str]] = []

    def run(command: list[str]) -> None:
        commands.append(command)

    notifier = MacOSReleaseReminderNotifier(run_command=run)

    notifier.notify(_reminder(ReleaseReminderKind.TOMORROW))

    assert commands[0][:2] == ["/usr/bin/osascript", "-e"]
    assert 'Domani esce Example \\"Show\\" · S02E03 · The Return' in commands[0][2]
    assert 'with title "NextEp"' in commands[0][2]


def test_macos_notifier_labels_today_release() -> None:
    commands: list[list[str]] = []
    notifier = MacOSReleaseReminderNotifier(run_command=commands.append)

    notifier.notify(_reminder(ReleaseReminderKind.TODAY))

    assert "Oggi esce" in commands[0][2]
