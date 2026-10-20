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


        print("DATE BUTTON DETAILS")
        print("-------------------")


        buttons = page.locator("button")

        count = await buttons.count()


        for i in range(count):

            button = buttons.nth(i)

            text = await button.inner_text()

            if text.strip():

                disabled = await button.is_disabled()

                classes = await button.get_attribute("class")

                print("\nBUTTON:", repr(text))
                print("Disabled:", disabled)
                print("Class:", classes)


        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())