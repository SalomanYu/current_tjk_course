from aiogram import Bot, executor, Dispatcher, types
from dotenv import load_dotenv
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from corrency import get_actual_currency, get_last_rate, save_result, tz

chats = (
    544490770, # Rosya
)

env = load_dotenv(".env")
if not env:
    exit("Создайте файл .env")

bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()

@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    await message.answer('Актуальный курс TJK/RUB')
    await scheduled_message()


async def scheduled_message():
    current_rate = await get_actual_currency()
    rub_1k = current_rate.RUB_TO_TJK * 1_000
    rub_280k = current_rate.RUB_TO_TJK * 280_000
    msg = "\n".join([
        f"Актуальный курс на {datetime.now(tz)}:",
        f"1000 рублей = {rub_1k} сомони",
        f"280К рублей = {rub_280k} сомони",
    ])
    previos_rate = get_last_rate()
    if previos_rate and previos_rate != current_rate.RUB_TO_TJK:
        difference_rub_1k = f"📈{previos_rate * 1_000 - rub_1k}" if previos_rate * 1_000 - rub_1k > 0 else f"{previos_rate * 1_000 - rub_1k}"
        difference_rub_280k = f"📈{previos_rate * 280_000 - rub_280k}" if previos_rate * 280_000 - rub_280k > 0 else f"{previos_rate * 280_000 - rub_280k}"
        additional = "\n".join([
            "\n",
            "Разница с предыдущим курсом:",
            f"1000 рублей = {previos_rate * 1_000} ({difference_rub_1k})",
            f"280K рублей = {previos_rate * 280_000} ({difference_rub_280k})",
        ])
        msg += additional
    print(msg)
    for chat in chats:
        await bot.send_message(chat, msg)
    save_result(current_rate.RUB_TO_TJK)




if __name__ == "__main__":
    scheduler.add_job(scheduled_message, 'interval', hours=12)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)