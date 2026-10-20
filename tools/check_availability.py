import asyncio

from playwright.async_api import async_playwright


URL = "https://termine.essen.de/?link=4ce9"


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page()


        print("Opening page...")

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


        print("Checking available dates...")


        dates = page.locator(
            "button.duet-date__day"
        )


        count = await dates.count()

        available_dates = []


        for i in range(count):

            date = dates.nth(i)

            disabled = await date.is_disabled()

            text = await date.inner_text()


            if not disabled:
                available_dates.append(text)


        if available_dates:

            print("🚨 APPOINTMENT AVAILABLE!")
            print(available_dates)

        else:

            print("❌ No appointments available")


        await browser.close()



if __name__ == "__main__":
    asyncio.run(main())