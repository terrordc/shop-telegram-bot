# Create this new file: src/callbacks/admin/order_details.py

import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
# We can reuse the status helper from the user-side orders view
from ..user.orders import get_status_text

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    order_id = data["oid"]
    order = models.orders.Order(order_id)
    
    # Gather all order details
    (
        order_user_id,
        status,
        full_name,
        address,
        phone_number,
        comment,
        items,
    ) = await asyncio.gather(
        order.user_id,
        order.status,
        order.full_name,
        order.address,
        order.phone_number,
        order.comment,
        order.items,
    )

    # Format items and price for display
    total_price = 0
    items_text_list = []
    for item in items:
        price = item.price * item.amount
        total_price += price
        items_text_list.append(f"• {item.title} ({item.amount} шт.)")
    items_text = "\n".join(items_text_list)

    # Format the main message text
    details_text = f"""
Детали заказа #{order_id}
<b>Статус:</b> {get_status_text(status)}

<b>Клиент:</b> {full_name or 'Не указано'}
<b>ID клиента:</b> <code>{order_user_id}</code>
<b>Телефон:</b> <code>{phone_number}</code>
<b>Адрес:</b> {address}
<b>Комментарий:</b> {comment or 'Нет'}

<b>Состав заказа:</b>
{items_text}
<b>Итого:</b> {total_price:.2f}{constants.config['settings']['currency_symbol']}
    """

    # --- Build Action Buttons Based on Status ---
    markup = []
    original_status_breadcrumb = data["s"]

    # If the order is "Awaiting Cancellation" (status 5)
    if status == 5:
        # Now we pass the original status 's' along with the new status 'st'
        approve_callback = f'{{"r":"admin", "oid":{order_id}, "st":4, "s":{original_status_breadcrumb}}}change_status'
        deny_callback = f'{{"r":"admin", "oid":{order_id}, "st":0, "s":{original_status_breadcrumb}}}change_status'
        markup.append([(constants.language.approve_cancellation, approve_callback)])
        markup.append([(constants.language.deny_cancellation, deny_callback)])

    # If the order is "New" (status 0)
    elif status == 0:
        # This button will now trigger an FSM to ask for the tracking number
        shipped_callback = f'{{"r":"admin", "oid":{order_id}}}set_tracking_number'
        markup.append([(constants.language.mark_as_shipped, shipped_callback)])

    # Add a "Back" button that returns to the previous list, using the 's' breadcrumb
    back_callback = f'{{"r":"admin", "s":{data["s"]}}}orders_list'
    markup.append([(constants.language.back, back_callback)])

    await callback_query.message.edit_text(
        text=details_text,
        reply_markup=markups.create(markup),
        parse_mode="HTML"
    )