"""Reelore application package."""

from reelore import web_navigation_theme as _web_navigation_theme
from reelore.web_brand_polish import BRAND_POLISH_CSS
from reelore.web_shell import NEXT_EP_SHELL_CSS

_web_navigation_theme.NAVIGATION_CSS += BRAND_POLISH_CSS + NEXT_EP_SHELL_CSS
