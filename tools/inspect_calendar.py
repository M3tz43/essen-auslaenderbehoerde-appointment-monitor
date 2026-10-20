import asyncio
from playwright.async_api import async_playwright


URL = "https://termine.essen.de/?link=4ce9"


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page()


        await page.goto(
            URL,
            wait_until="networkidle",
            timeout=60000
        )


        # Step 1
        await page.get_by_text(
            "Anmeldung",
            exact=True
        ).click()

        await page.wait_for_load_state("networkidle")


        # Step 2
        await page.get_by_text(
            "Weiter zu Schritt 2",
            exact=True
        ).click()

        await page.wait_for_load_state("networkidle")


        # Step 3
        await page.get_by_text(
            "Weiter zu Schritt 3",
            exact=True
        ).click()

        await page.wait_for_load_state("networkidle")

        await page.wait_for_timeout(3000)


        print("Checking calendar elements...")


        buttons = await page.locator("button").all_inner_texts()

        print("\nBUTTONS:")
        for b in buttons:
            print(repr(b))


        await page.screenshot(
            path="calendar_debug.png",
            full_page=True
        )


        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())