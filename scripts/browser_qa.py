#!/usr/bin/env python3
"""Responsive browser smoke test for the Bayou Gloss static website."""

from pathlib import Path

from playwright.sync_api import sync_playwright


URL = "http://127.0.0.1:4173"
SCREENSHOTS = Path(__file__).resolve().parent.parent / "screenshots"


def main() -> None:
    SCREENSHOTS.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        for width, height, label in (
            (1440, 1000, "desktop"),
            (1024, 900, "tablet"),
            (390, 844, "phone"),
        ):
            page = browser.new_page(viewport={"width": width, "height": height})
            console_errors: list[str] = []
            page.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            page.goto(URL, wait_until="networkidle")
            page.wait_for_timeout(500)
            page.evaluate("document.documentElement.style.scrollBehavior = 'auto'")
            for image in page.locator("img[loading='lazy']").all():
                image.scroll_into_view_if_needed()
                page.wait_for_timeout(120)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(250)

            metrics = page.evaluate(
                """() => ({
                    viewport: innerWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                    h1Count: document.querySelectorAll('h1').length,
                    imageCount: document.images.length,
                    loadedImages: [...document.images].filter(
                        image => image.complete && image.naturalWidth > 0
                    ).length,
                    headerBackground: getComputedStyle(
                        document.querySelector('.site-header')
                    ).backgroundColor,
                    phoneLinks: document.querySelectorAll(
                        'a[href="tel:+18323583394"]'
                    ).length,
                    bookingLinks: document.querySelectorAll(
                        'a[href="https://cal.com/sumitdatta/auto-detail-service"]'
                    ).length,
                    forms: document.querySelectorAll('form').length,
                    mailLinks: document.querySelectorAll('a[href^="mailto:"]').length
                })"""
            )
            print(f"{label}: {metrics}; console_errors={console_errors}")

            assert metrics["scrollWidth"] <= metrics["viewport"] + 1
            assert metrics["h1Count"] == 1
            assert metrics["imageCount"] == metrics["loadedImages"]
            assert metrics["headerBackground"] not in ("rgba(0, 0, 0, 0)", "transparent")
            assert metrics["phoneLinks"] >= 5
            assert metrics["bookingLinks"] >= 5
            assert metrics["forms"] == 0
            assert metrics["mailLinks"] == 0
            assert not console_errors

            page.screenshot(path=SCREENSHOTS / f"{label}-top.png", full_page=False)
            page.locator("#finish-check").scroll_into_view_if_needed()
            page.wait_for_timeout(350)
            page.screenshot(path=SCREENSHOTS / f"{label}-finish.png", full_page=False)

            if width == 390:
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(200)
                page.locator("[data-menu-toggle]").click()
                assert page.locator("[data-menu-toggle]").get_attribute("aria-expanded") == "true"
                assert page.locator("[data-nav]").evaluate(
                    "element => getComputedStyle(element).display"
                ) != "none"
                page.screenshot(path=SCREENSHOTS / "phone-menu.png", full_page=False)
                page.locator("[data-menu-toggle]").click()

                page.locator("#faq").scroll_into_view_if_needed()
                page.locator("#faq details:first-child summary").click()
                assert page.locator("#faq details:first-child").get_attribute("open") is not None

            page.close()

        browser.close()


if __name__ == "__main__":
    main()
