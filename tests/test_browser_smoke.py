from __future__ import annotations

import os
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
                if os.getenv("CI"):
                    raise RuntimeError(
                        f"Chromium is not installed for Playwright in CI: {bundled_error}"
                    ) from bundled_error
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


def _set_layer(page: Page, layer: str, checked: bool) -> None:
    control = page.locator(f'#active-layers input[value="{layer}"]')
    if checked:
        control.check(force=True)
    else:
        control.uncheck(force=True)


def _search(page: Page, query: str) -> None:
    page.locator("#search-input").fill(query)
    page.locator("#search-input").press("Enter")


def _search_and_open(page: Page, query: str, result_text: str) -> None:
    _search(page, query)
    result = page.locator(".search-result-item").filter(has_text=result_text).first
    expect(result).to_be_visible(timeout=10_000)
    result.click()


def test_application_startup(page: Page) -> None:
    expect(page.locator("#map")).to_be_visible()
    expect(page.locator(".leaflet-container")).to_be_visible()
    expect(page.locator("#visible-count")).to_contain_text("9,371 visible", timeout=10_000)


def test_layer_toolbar_visible(page: Page) -> None:
    expect(page.locator("#layer-toolbar")).to_be_visible(timeout=10_000)
    expect(page.locator('#active-layers input[value="global_metros"]')).to_be_checked()
    expect(page.locator('#active-layers input[value="adversary_military"]')).to_be_checked()
    expect(page.locator('#active-layers input[value="us_military"]')).to_be_checked()


def test_duplicate_floating_utilities_are_absent(page: Page) -> None:
    expect(page.locator(".map-control-group")).to_have_count(0)
    expect(page.locator("#map-reset-view")).to_have_count(0)
    expect(page.locator("#map-fit-screen")).to_have_count(0)
    expect(page.locator("#map-full-map-toggle")).to_have_count(0)
    expect(page.locator("#map-sidebar-toggle")).to_have_count(0)


def test_marker_click_opens_and_closes_details(page: Page) -> None:
    marker = page.locator(".location-marker, .metro-marker, .us-marker").first
    expect(marker).to_be_visible(timeout=10_000)

    marker.click()
    _expect_any_details_open(page)

    page.locator("#close-details").click()
    expect(page.locator("#details-panel")).to_have_class(re.compile(r".*\bis-collapsed\b.*"))


def test_metro_only_view(page: Page) -> None:
    _set_layer(page, "adversary_military", False)
    _set_layer(page, "us_military", False)
    expect(page.locator("#visible-count")).to_contain_text("7,027 visible", timeout=10_000)
    expect(page.locator("#visible-count")).to_contain_text("Global metros: 7,027")


def test_adversary_only_view(page: Page) -> None:
    _set_layer(page, "global_metros", False)
    _set_layer(page, "us_military", False)
    expect(page.locator("#visible-count")).to_contain_text("718 visible", timeout=10_000)
    expect(page.locator("#visible-count")).to_contain_text("Adversary military: 718")


def test_us_only_view(page: Page) -> None:
    _set_layer(page, "global_metros", False)
    _set_layer(page, "adversary_military", False)
    expect(page.locator("#visible-count")).to_contain_text("1,626 visible", timeout=10_000)
    expect(page.locator("#visible-count")).to_contain_text("U.S. military: 1,626")


def test_all_military_view(page: Page) -> None:
    _set_layer(page, "global_metros", False)
    expect(page.locator("#visible-count")).to_contain_text("2,344 visible", timeout=10_000)


def test_all_three_layers_view(page: Page) -> None:
    expect(page.locator("#visible-count")).to_contain_text("9,371 visible", timeout=10_000)


def test_metro_and_adversary_view(page: Page) -> None:
    _set_layer(page, "us_military", False)
    expect(page.locator("#visible-count")).to_contain_text("7,745 visible", timeout=10_000)


def test_global_city_search_and_details(page: Page) -> None:
    _search_and_open(page, "Tokyo", "Tokyo")
    _expect_details_open(page, "Tokyo")
    expect(page.locator("#details-panel")).to_contain_text("Population source", timeout=10_000)
    expect(page.locator("#details-panel")).to_contain_text("Sources and Research Links")


def test_us_site_search_and_details(page: Page) -> None:
    _search_and_open(page, "Ramstein", "Ramstein AB")
    _expect_details_open(page, "Ramstein AB")
    expect(page.locator("#details-panel")).to_contain_text("Coordinate quality", timeout=10_000)
    expect(page.locator("#details-panel")).to_contain_text("Site Identity")


def test_coordinate_audit_warning_display(page: Page) -> None:
    _search_and_open(page, "Camp Morse", "Camp Morse")
    _expect_details_open(page, "Camp Morse")
    expect(page.locator("#details-panel")).to_contain_text(
        "Coordinate audit warning",
        timeout=10_000,
    )
    expect(page.locator("#quality-warning-banner")).to_be_visible(timeout=10_000)


def test_top_bar_controls(page: Page) -> None:
    page.get_by_role("button", name="Reset View").click()
    expect(page.locator("#visible-count")).to_contain_text("visible", timeout=10_000)
    page.get_by_role("button", name="Fit to Screen").click()
    expect(page.locator("#map")).to_be_visible()
    page.get_by_role("button", name="Full Map").click()
    expect(page.locator("#app-shell")).to_have_class(re.compile(r".*\bis-full-map\b.*"))
    page.get_by_role("button", name="Collapse Sidebar").click()
    expect(page.locator("#app-shell")).to_have_class(re.compile(r".*\bis-sidebar-collapsed\b.*"))


def test_type_selection_preservation(page: Page) -> None:
    page.locator("#clear-all-types").click()
    expect(page.locator("#visible-count")).to_contain_text("0 visible", timeout=10_000)
    _set_layer(page, "global_metros", False)
    expect(page.locator("#visible-count")).to_contain_text("0 visible", timeout=10_000)
    page.locator("#select-all-types").click()
    expect(page.locator("#visible-count")).not_to_contain_text("0 visible", timeout=10_000)


def test_zoom_to_selected_behavior(page: Page) -> None:
    _search_and_open(page, "Tokyo", "Tokyo")
    _expect_details_open(page, "Tokyo")
    page.locator("#zoom-to-selected").click()
    expect(page.locator("#details-panel")).not_to_have_class(re.compile(r".*\bis-collapsed\b.*"))


def test_mobile_layout(page: Page) -> None:
    _search_and_open(page, "Ramstein", "Ramstein AB")
    page.set_viewport_size({"width": 390, "height": 760})
    expect(page.locator("#details-panel")).not_to_have_class(re.compile(r".*\bis-collapsed\b.*"))
    expect(page.locator("#layer-toolbar")).to_be_visible()
    expect(page.locator(".details-title")).to_contain_text("Ramstein AB")
