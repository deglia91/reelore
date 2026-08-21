from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import FranchiseRelationType, FranchiseTVTitle
from reelore.infrastructure.curated_franchise import (
    CURATED_TV_FRANCHISE_GRAPH,
    CuratedFranchiseTVProvider,
)


def _catalog(provider_id: str = "169") -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id=provider_id,
        title="Breaking Bad",
        summary=None,
        status="Ended",
        premiered=date(2008, 1, 20),
        ended=date(2013, 9, 29),
        image_url=None,
    )


def test_curated_franchise_provider_returns_explicit_relationships_for_source_id() -> None:
    expected = (
        FranchiseTVTitle(
            provider_key="618",
            title="Better Call Saul",
            relations=(
                FranchiseRelationType.SPIN_OFF_OF,
                FranchiseRelationType.PREQUEL_OF,
            ),
            premiered=date(2015, 2, 8),
        ),
    )
    provider = CuratedFranchiseTVProvider({"169": expected})

    assert provider.franchise_for(_catalog()) == expected


def test_curated_franchise_provider_returns_empty_for_unknown_source_id() -> None:
    provider = CuratedFranchiseTVProvider({"169": ()})

    assert provider.franchise_for(_catalog("999")) == ()


def test_initial_curated_graph_covers_two_known_narrative_universes() -> None:
    assert CURATED_TV_FRANCHISE_GRAPH["169"][0].provider_key == "618"
    assert FranchiseRelationType.PREQUEL_OF in CURATED_TV_FRANCHISE_GRAPH["169"][0].relations
    assert CURATED_TV_FRANCHISE_GRAPH["618"][0].provider_key == "169"

    assert CURATED_TV_FRANCHISE_GRAPH["82"][0].provider_key == "44778"
    assert FranchiseRelationType.PREQUEL_OF in CURATED_TV_FRANCHISE_GRAPH["82"][0].relations
    assert CURATED_TV_FRANCHISE_GRAPH["44778"][0].provider_key == "82"
