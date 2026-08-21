from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import FranchiseRelationType, FranchiseTVTitle
from reelore.application.franchise_view import FranchiseTitleViewService


class WorkingFranchiseProvider:
    def franchise_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]:
        return (
            FranchiseTVTitle(
                provider_key="618",
                title="Better Call Saul",
                relations=(FranchiseRelationType.SPIN_OFF_OF,),
            ),
        )


class FailingFranchiseProvider:
    def franchise_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]:
        raise RuntimeError("provider unavailable")


def _catalog() -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id="169",
        title="Breaking Bad",
        summary=None,
        status="Ended",
        premiered=date(2008, 1, 20),
        ended=date(2013, 9, 29),
        image_url=None,
    )


def test_franchise_title_view_service_returns_provider_items() -> None:
    service = FranchiseTitleViewService(WorkingFranchiseProvider())

    assert service.list_for(_catalog()) == (
        FranchiseTVTitle(
            provider_key="618",
            title="Better Call Saul",
            relations=(FranchiseRelationType.SPIN_OFF_OF,),
        ),
    )


def test_franchise_title_view_service_ignores_provider_failures() -> None:
    service = FranchiseTitleViewService(FailingFranchiseProvider())

    assert service.list_for(_catalog()) == ()
