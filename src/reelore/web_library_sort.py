"""Presentation helpers for library ordering."""

from reelore.application.library_view import LibraryItemView
from reelore.domain import LibraryStatus

VALID_LIBRARY_SORTS = frozenset({"priority", "title"})


def normalize_library_sort(value: str) -> str:
    if value in VALID_LIBRARY_SORTS:
        return value
    return "priority"


def sort_library_items(
    items: tuple[LibraryItemView, ...],
    selected_sort: str,
) -> tuple[LibraryItemView, ...]:
    selected = normalize_library_sort(selected_sort)
    if selected == "title":
        return tuple(sorted(items, key=lambda item: item.title.casefold()))
    return tuple(
        sorted(
            items,
            key=lambda item: (item.next_episode is None, item.title.casefold()),
        )
    )


def render_library_sort(selected_sort: str, status: LibraryStatus | None) -> str:
    selected = normalize_library_sort(selected_sort)
    return (
        '<nav class="library-sort" aria-label="Ordina libreria">'
        '<span class="tracking-label">Ordina:</span>'
        + _sort_link("Priorità", "priority", selected, status)
        + _sort_link("Titolo", "title", selected, status)
        + "</nav>"
    )


def _sort_link(
    label: str,
    value: str,
    selected: str,
    status: LibraryStatus | None,
) -> str:
    query = f"sort={value}"
    if status is not None:
        query = f"status={status.value}&{query}"
    active = " active" if value == selected else ""
    current = ' aria-current="page"' if value == selected else ""
    return (
        f'<a class="filter-chip{active}" href="/library?{query}"{current}>'
        f"{label}</a>"
    )
