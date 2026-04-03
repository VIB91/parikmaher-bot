import asyncio
from datetime import datetime, timedelta
from database import get_upcoming_bookings, mark_as_reminded

async def notifier(bot):
    while True:
        now = datetime.now()
        bookings = await get_upcoming_bookings(days=3)  # только ближайшие 3 дня

        for b in bookings:
            booking_datetime = datetime.strptime(b["date"] + " " + b["time"], "%Y-%m-%d %H:%M")
            reminder_time = booking_datetime - timedelta(hours=24)

            # если настало время отправить напоминание
            if now >= reminder_time:
                try:
                    await bot.send_message(
                        b["user_id"],
                        f"⏰ Напоминание: у вас запись к {b['master']} на {b['date']} в {b['time']} ({b['service']})"
                    )
                    await mark_as_reminded(b["id"])
                except Exception as e:
                    print(f"Ошибка при отправке напоминания: {e}")

        await asyncio.sleep(60)  # проверка каждую минуту