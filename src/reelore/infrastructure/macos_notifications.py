"""macOS Notification Center adapter for TV release reminders."""

import subprocess
from collections.abc import Callable

from reelore.application.release_reminders import ReleaseReminder, ReleaseReminderKind


def _run_command(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True, text=True)


class MacOSReleaseReminderNotifier:
    """Deliver release reminders through macOS Notification Center."""

    def __init__(self, run_command: Callable[[list[str]], None] = _run_command) -> None:
        self._run_command = run_command

    def notify(self, reminder: ReleaseReminder) -> None:
        prefix = "Oggi esce" if reminder.kind is ReleaseReminderKind.TODAY else "Domani esce"
        reference = f"S{reminder.season_number:02}E{reminder.episode_number:02}"
        message = f"{prefix} {reminder.series_title} · {reference} · {reminder.episode_title}"
        escaped_message = _escape_applescript_text(message)
        script = f'display notification "{escaped_message}" with title "NextEp"'
        self._run_command(["/usr/bin/osascript", "-e", script])


def _escape_applescript_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
