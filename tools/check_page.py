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

        print("Page loaded")


        # Step 1: Click Anmeldung
        print("Clicking Anmeldung...")

        await page.get_by_text(
            "Anmeldung",
            exact=True
        ).click()

        print("Clicked Anmeldung")


        await page.wait_for_load_state(
            "networkidle"
        )

        await page.wait_for_timeout(2000)



        # Step 2: Click Weiter zu Schritt 2
        print("Clicking Weiter zu Schritt 2...")

        await page.get_by_text(
            "Weiter zu Schritt 2",
            exact=True
        ).click()

        print("Clicked Weiter zu Schritt 2")


        await page.wait_for_load_state(
            "networkidle"
        )

        await page.wait_for_timeout(2000)



        # Step 3: Click Weiter zu Schritt 3
        print("Clicking Weiter zu Schritt 3...")

        await page.get_by_text(
            "Weiter zu Schritt 3",
            exact=True
        ).click()

        print("Clicked Weiter zu Schritt 3")


        await page.wait_for_load_state(
            "networkidle"
        )

        await page.wait_for_timeout(3000)



        # Get page information
        title = await page.title()

        print("\nPage title:")
        print(title)


        text = await page.text_content("body")

        print("\nAppointment page text:")
        print("--------------------")
        print(text[:5000])


        # Save full HTML
        html = await page.content()

        with open(
            "appointment_page.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(html)


        # Save screenshot
        await page.screenshot(
            path="appointment_page.png",
            full_page=True
        )


        print("\nFiles created:")
        print("✅ appointment_page.html")
        print("✅ appointment_page.png")


        await browser.close()



if __name__ == "__main__":
    asyncio.run(main())