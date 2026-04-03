import aiosqlite
import asyncio

async def add_reminded_column():
    async with aiosqlite.connect("barber.db") as db:
        await db.execute("ALTER TABLE bookings ADD COLUMN reminded INTEGER DEFAULT 0;")
        await db.commit()
        print("Колонка reminded добавлена")

asyncio.run(add_reminded_column())