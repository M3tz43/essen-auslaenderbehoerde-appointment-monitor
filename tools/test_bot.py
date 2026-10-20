import os
import asyncio

from dotenv import load_dotenv
from telegram import Bot


load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def main():

    bot = Bot(
        token=TOKEN
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ Essen ABH Monitor is working!"
    )


if __name__ == "__main__":
    asyncio.run(main())