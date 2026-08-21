from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import (
    FranchiseRelationType,
    FranchiseTVProvider,
    FranchiseTVTitle,
)


class StubFranchiseProvider:
    def franchise_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]:
        assert catalog.title == "Breaking Bad"
        return (
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


def _titles_from(provider: FranchiseTVProvider) -> tuple[FranchiseTVTitle, ...]:
    return provider.franchise_for(
        TVSeriesCatalog(
            provider_id="169",
            title="Breaking Bad",
            summary=None,
            status="Ended",
            premiered=date(2008, 1, 20),
            ended=date(2013, 9, 29),
            image_url=None,
        )
    )


def test_franchise_relations_are_distinct_from_generic_recommendations() -> None:
    assert {relation.value for relation in FranchiseRelationType} == {
        "prequel_of",
        "sequel_of",
        "spin_off_of",
        "same_universe",
        "character_related",
        "recommended_before",
        "recommended_after",
    }


def test_franchise_provider_exposes_multiple_typed_relationships() -> None:
    titles = _titles_from(StubFranchiseProvider())

    assert titles == (
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
