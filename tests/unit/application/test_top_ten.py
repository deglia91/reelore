from dataclasses import dataclass, field

from reelore.application import TopTenService
from reelore.domain import LibraryStatus, MediaItem, MediaType, PersonalMediaState


@dataclass
class FakeTopTenStore:
    media: dict[str, MediaItem] = field(default_factory=dict)
    states: dict[str, PersonalMediaState] = field(default_factory=dict)

    def add(self, media_id: str, rank: int | None = None) -> None:
        self.media[media_id] = MediaItem(media_id, media_id.title(), MediaType.TV_SERIES)
        self.states[media_id] = PersonalMediaState(
            media_id,
            LibraryStatus.PLANNED,
            top_ten_rank=rank,
        )

    def list_media(self) -> tuple[MediaItem, ...]:
        return tuple(self.media.values())

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return self.states.get(media_id)

    def save_personal_state(self, state: PersonalMediaState) -> None:
        self.states[state.media_id] = state


def test_inserting_unranked_media_shifts_contiguous_occupants_down() -> None:
    store = FakeTopTenStore()
    store.add("first", 1)
    store.add("second", 2)
    store.add("third", 3)
    store.add("new")

    TopTenService(store).assign("new", 2)

    assert store.states["first"].top_ten_rank == 1
    assert store.states["new"].top_ten_rank == 2
    assert store.states["second"].top_ten_rank == 3
    assert store.states["third"].top_ten_rank == 4


def test_inserting_unranked_media_stops_at_first_free_rank() -> None:
    store = FakeTopTenStore()
    store.add("second", 2)
    store.add("fourth", 4)
    store.add("new")

    TopTenService(store).assign("new", 2)

    assert store.states["new"].top_ten_rank == 2
    assert store.states["second"].top_ten_rank == 3
    assert store.states["fourth"].top_ten_rank == 4


def test_inserting_into_full_tail_drops_previous_tenth_place() -> None:
    store = FakeTopTenStore()
    store.add("ninth", 9)
    store.add("tenth", 10)
    store.add("new")

    TopTenService(store).assign("new", 9)

    assert store.states["new"].top_ten_rank == 9
    assert store.states["ninth"].top_ten_rank == 10
    assert store.states["tenth"].top_ten_rank is None
