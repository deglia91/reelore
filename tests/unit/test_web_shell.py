from reelore.web import _page


def test_app_shell_exposes_desktop_and_mobile_navigation() -> None:
    page = _page("<p>Content</p>", home=True)

    assert 'class="app-header"' in page
    assert 'class="desktop-nav"' in page
    assert 'class="mobile-nav"' in page
    assert 'href="/#library"' in page
    assert 'href="/#upcoming"' in page
    assert 'href="/#top-ten"' in page
    assert 'href="/#search"' in page


def test_app_shell_uses_semantic_theme_tokens() -> None:
    page = _page("<p>Content</p>")

    assert "background: var(--color-bg)" in page
    assert "background: var(--color-accent)" in page
    assert "border: 1px solid var(--color-border)" in page
    assert 'class="detail-page"' in page
