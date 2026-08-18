from reelore import __doc__


def test_package_is_importable() -> None:
    assert __doc__ == "Reelore application package."
