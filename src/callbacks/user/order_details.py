# src/callbacks/user/order_details.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
import datetime
import models
import constants
from markups import markups
from .orders import get_status_text 

SDEK_TRACKING_URL = "https://www.cdek.ru/ru/tracking?order_id="

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    order_id = data["oid"]
    order = models.orders.Order(order_id)

    # 1. Gather all order details, including the new date_updated_raw
    (
        status,
        date_created,
        date_updated_raw,
        tracking_number,
        address,
        phone_number,
        comment,
        items,
    ) = await asyncio.gather(
        order.status,
        order.date_created,
        order.date_updated_raw,
        order.tracking_number,
        order.address,
        order.phone_number,
        order.comment,
        order.items,
    )

    # 2. Format the list of items for display
    total_price = 0
    items_text_list = []
    for item in items:
        price = item.price * item.amount
        total_price += price
        items_text_list.append(f"• {item.title} ({item.amount} шт.)")
    items_text = "\n".join(items_text_list)

    # 3. Build the dynamic part of the details text based on status
    status_specific_info = ""
    # Status 4 = Cancelled
    if status == 4 and date_updated_raw:
        date_cancelled = datetime.datetime.strptime(date_updated_raw, constants.TIME_FORMAT).strftime("%d.%m.%Y %H:%M")
        status_specific_info = f"<b>{constants.language.date_cancelled_text}</b> {date_cancelled}"

    # 4. Format the final text for the message
    # (I'm using a direct f-string here for simplicity, but you can use your language template)
    final_text = f"""
📄 <b>Детали заказа #{order_id}</b>

<b>Статус:</b> {get_status_text(status)}
<b>Дата:</b> {date_created.strftime("%d.%m.%Y %H:%M")}
{status_specific_info}

<b>Товары:</b>
{items_text}

<b>Адрес доставки:</b> {address}
<b>Телефон:</b> {phone_number}
<b>Комментарий:</b> {comment or 'Нет'}

<b>Итого:</b> {total_price:.2f}{constants.config['settings']['currency_symbol']}
    """

    # 5. Build the markup, also based on status
    markup = []
    # Show tracking button ONLY if the order has a tracking number and is NOT cancelled
    if tracking_number and status != 4:
        markup.append((
            constants.language.track_order_button, 
            {"url": f"{SDEK_TRACKING_URL}{tracking_number}"}
        ))
    
    # Show cancellation request button ONLY if the order is "New"
    if status == 0:
        cancel_callback = f'{{"r":"user", "oid":{order_id}}}confirm_cancellation'
        markup.append((constants.language.request_cancellation, cancel_callback))
    
    markup.append((constants.language.back, f"{constants.JSON_USER}orders"))

    # 6. Send the message
    await callback_query.message.edit_text(
        text=final_text.strip(),
        reply_markup=markups.create(markup),
        parse_mode="HTML",
    )