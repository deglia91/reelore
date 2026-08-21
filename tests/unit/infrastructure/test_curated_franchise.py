from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import FranchiseRelationType, FranchiseTVTitle
from reelore.infrastructure.curated_franchise import CuratedFranchiseTVProvider


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
            provider_key="60059",
            title="Better Call Saul",
            relation=FranchiseRelationType.SPIN_OFF_OF,
            premiered=date(2015, 2, 8),
        ),
    )
    provider = CuratedFranchiseTVProvider({"169": expected})

    assert provider.franchise_for(_catalog()) == expected


def test_curated_franchise_provider_returns_empty_for_unknown_source_id() -> None:
    provider = CuratedFranchiseTVProvider({"169": ()})

    assert provider.franchise_for(_catalog("999")) == ()
