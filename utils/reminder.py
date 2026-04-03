import asyncio
from datetime import datetime, timedelta
from database import get_all_bookings, mark_notified

async def reminder(bot):
    while True:
        now = datetime.now()

        bookings = await get_all_bookings()

        for b in bookings:
            # id, user_id, master, service, date, time, notified
            booking_id = b[0]
            user_id = b[1]
            master = b[2]
            service = b[3]
            date = b[4]
            time = b[5]
            notified = b[6] if len(b) > 6 else 0

            # если уже отправляли — пропускаем
            if notified:
                continue

            try:
                booking_datetime = datetime.strptime(
                    f"{date} {time}",
                    "%Y-%m-%d %H:%M"
                )
            except:
                continue

            # разница времени
            diff = booking_datetime - now

            # если до записи ~24 часа (±5 минут)
            if 86000 <= diff.total_seconds() <= 87000:
                try:
                    nice_date = booking_datetime.strftime("%d.%m.%Y %H:%M")

                    await bot.send_message(
                        user_id,
                        f"⏰ Напоминание!\n\n"
                        f"Вы записаны завтра:\n"
                        f"💇 {master}\n"
                        f"🧾 {service}\n"
                        f"📅 {nice_date}"
                    )

                    # помечаем как отправленное
                    await mark_notified(booking_id)

                except:
                    pass

        await asyncio.sleep(60)