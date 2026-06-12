from __future__ import annotations

import re
import socket
import threading
import time
from collections.abc import Iterator

import pytest
import requests

from app import create_app

pytestmark = pytest.mark.browser

playwright_sync_api = pytest.importorskip("playwright.sync_api")
Error = playwright_sync_api.Error
Page = playwright_sync_api.Page
expect = playwright_sync_api.expect
sync_playwright = playwright_sync_api.sync_playwright


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def dash_url() -> str:
    port = _free_port()
    dash_app = create_app()
    thread = threading.Thread(
        target=lambda: dash_app.run(host="127.0.0.1", port=port, debug=False),
        daemon=True,
    )
    thread.start()
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 25
    while time.time() < deadline:
        try:
            response = requests.get(f"{url}/_dash-layout", timeout=1)
            if response.ok:
                return url
        except requests.RequestException:
            time.sleep(0.25)
    raise RuntimeError(f"Dash test server did not start at {url}")


@pytest.fixture(scope="module")
def browser() -> Iterator[object]:
    with sync_playwright() as playwright:
        browser_instance = None
        try:
            browser_instance = playwright.chromium.launch(headless=True)
        except Error as bundled_error:
            for channel in ("msedge", "chrome"):
                try:
                    browser_instance = playwright.chromium.launch(
                        channel=channel,
                        headless=True,
                    )
                    break
                except Error:
                    continue
            if browser_instance is None:
                pytest.skip(f"Chromium is not installed for Playwright: {bundled_error}")
        yield browser_instance
        browser_instance.close()


@pytest.fixture()
def page(browser: object, dash_url: str) -> Iterator[Page]:
    browser_instance = browser
    page_instance = browser_instance.new_page(viewport={"width": 1280, "height": 820})
    page_instance.goto(dash_url)
    expect(page_instance.locator("#map")).to_be_visible(timeout=15_000)
    expect(page_instance.locator(".leaflet-container")).to_be_visible(timeout=15_000)
    yield page_instance
    page_instance.close()


def _expect_details_open(page: Page, title: str) -> None:
    expect(page.locator("#details-panel")).not_to_have_class(re.compile(r".*\bis-collapsed\b.*"))
    expect(page.locator(".details-title")).to_contain_text(title, timeout=10_000)


def _expect_any_details_open(page: Page) -> None:
    expect(page.locator("#details-panel")).not_to_have_class(re.compile(r".*\bis-collapsed\b.*"))
    expect(page.locator(".details-title")).to_be_visible(timeout=10_000)


def test_marker_click_opens_closes_and_reopens_details(page: Page) -> None:
    marker = page.locator(".location-marker, .metro-marker").first
    expect(marker).to_be_visible(timeout=10_000)

    marker.click()
    _expect_any_details_open(page)

    page.locator("#close-details").click()
    expect(page.locator("#details-panel")).to_have_class(re.compile(r".*\bis-collapsed\b.*"))

    marker = page.locator(".location-marker, .metro-marker").first
    expect(marker).to_be_visible(timeout=10_000)
    marker.click()
    _expect_any_details_open(page)


def test_filters_search_result_reset_and_mobile_details(page: Page) -> None:
    page.locator('#country-filter input[value="DPRK"]').check(force=True)
    expect(page.locator("#visible-count")).to_contain_text("38 visible", timeout=10_000)
    expect(page.locator('#type-filter input[value="Metro Area"]')).to_be_attached()
    expect(page.locator('#type-filter input[value="Missile operating base"]')).to_be_attached()

    page.locator('#location-category-filter input[value="Countervalue"]').check(force=True)
    expect(page.locator("#visible-count")).to_contain_text("16 visible", timeout=10_000)

    page.locator("#search-input").fill("Pyongyang")
    result = page.locator(".search-result-item").filter(has_text="Pyongyang").first
    expect(result).to_be_visible(timeout=10_000)
    result.click()
    _expect_details_open(page, "Pyongyang")

    page.get_by_role("button", name="Reset View").first.click()
    expect(page.locator("#visible-count")).to_contain_text("1 visible", timeout=10_000)

    page.set_viewport_size({"width": 390, "height": 760})
    expect(page.locator("#details-panel")).not_to_have_class(re.compile(r".*\bis-collapsed\b.*"))
    expect(page.locator(".details-title")).to_contain_text("Pyongyang")
