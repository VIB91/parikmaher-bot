from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from database import get_all_bookings, get_bookings_by_date, admin_delete_booking, restore_booking, get_deleted_bookings
from datetime import datetime, timedelta
from keyboards.admin_kb import get_admin_filter_kb
from aiogram.fsm.context import FSMContext
from keyboards.client_kb import get_slots_kb
from services.booking_service import get_free_slots

router = Router()

@router.message(F.text == "CRM")
async def crm(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📊 Выберите фильтр:",
        reply_markup=get_admin_filter_kb()
    )

    bookings = await get_all_bookings()

    if not bookings:
        await message.answer("Нет записей")
        return

    text = "📊 *Все записи:*\n\n"

    for b in bookings:
        # b = (id, user_id, master, service, date, time)
        try:
            nice_date = datetime.strptime(b[4], "%Y-%m-%d").strftime("%d.%m.%Y")
        except (ValueError, IndexError):
            nice_date = str(b[4])  # если дата неправильная, показываем как есть

        text += (
            f"👤 ID: {b[1]}\n"
            f"💇 {b[2]}\n"
            f"🧾 {b[3]}\n"
            f"📅 {nice_date} {b[5]}\n"
            f"------------------\n"
        )

    await message.answer(text, parse_mode="Markdown")


@router.callback_query(F.data.startswith("filter_"))
async def handle_filter(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    filter_type = callback.data

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    if filter_type == "filter_today":
        bookings = await get_bookings_by_date(today)
        title = "📅 Сегодня"
    elif filter_type == "filter_tomorrow":
        bookings = await get_bookings_by_date(tomorrow)
        title = "📅 Завтра"
    else:
        bookings = await get_all_bookings()
        title = "📊 Все записи"

    if not bookings:
        await callback.message.answer(f"{title}\n\nНет записей")
        return

    await callback.message.answer(title)

    for b in bookings:
        # b = (id, user_id, master, service, date, time)
        booking_id = b[0]
        user_id = b[1]
        master = b[2]
        service = b[3]
        date = b[4]
        time = b[5]

        try:
            nice_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
        except (ValueError, TypeError):
            nice_date = str(date)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"admin_delete_{booking_id}"),
                InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_{booking_id}"),
            ]
        ])

        text = (
            f"👤 {user_id}\n"
            f"💇 {master}\n"
            f"🧾 {service}\n"
            f"📅 {nice_date} {time}"
        )

        await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("admin_delete_"))
async def delete_by_admin(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    booking_id = int(callback.data.split("_")[2])
    await admin_delete_booking(booking_id)
    await callback.message.edit_text(
        "❌ Запись удалена",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="↩️ Восстановить",
                    callback_data=f"restore_{booking_id}"
                )
            ]
        ])
    )

@router.message(F.text == "Удалённые записи")
async def deleted_list(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    bookings = await get_deleted_bookings()

    if not bookings:
        await message.answer("Нет удалённых записей")
        return

    for b in bookings:
        booking_id, user_id, master, service, date, time = b

        nice_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="↩️ Восстановить",
                    callback_data=f"restore_{booking_id}"
                )
            ]
        ])

        text = (
            f"👤 {user_id}\n"
            f"💇 {master}\n"
            f"🧾 {service}\n"
            f"📅 {nice_date} {time}"
        )

        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("restore_"))
async def restore(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[1])
    await restore_booking(booking_id)
    await callback.message.edit_text("✅ Запись восстановлена")


@router.callback_query(F.data.startswith("edit_"))
async def edit_booking(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    booking_id = int(callback.data.split("_")[1])
    await state.update_data(edit_id=booking_id)

    bookings = await get_all_bookings()

    for b in bookings:
        if b[0] == booking_id:
            master = b[2]
            date = b[4]

    slots = await get_free_slots(date, master)

    await callback.message.answer("Выберите новое время:", reply_markup=get_slots_kb(slots))