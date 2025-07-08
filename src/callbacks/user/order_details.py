# src/callbacks/user/order_details.py
from aiogram import types
import asyncio
import models
import constants
from markups import markups

# We can reuse the status helper function from the orders list view
from .orders import get_status_text 
SDEK_TRACKING_URL = "https://www.cdek.ru/ru/tracking?order_id="
async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    order_id = data["oid"]
    order = models.orders.Order(order_id)

    # 1. Gather all order details in parallel
    (
        status,
        date_created,
        tracking_number,
        address,
        phone_number,
        comment,
        items,
    ) = await asyncio.gather(
        order.status,
        order.date_created,
        order.tracking_number,
        order.address,
        order.phone_number,
        order.comment,
        order.items, # This returns a list of __Item objects
    )

    # 2. Format the list of items for display
    total_price = 0
    items_text_list = []
    for item in items:
        price = item.price * item.amount
        total_price += price
        items_text_list.append(f"  - {item.title} ({item.amount} шт.)")
    items_text = "\n".join(items_text_list)

    # 3. Format the final text for the message
    final_text = constants.language.order_details_text.format(
        status_text=get_status_text(status),
        date_created=date_created.strftime("%d.%m.%Y %H:%M"),
        tracking_number=tracking_number if tracking_number else constants.language.no_tracking_number,
        items_text=items_text,
        address=address,
        phone_number=phone_number,
        comment=comment,
        total_price=total_price,
        currency_symbol=constants.config['settings']['currency_symbol']
    )

    # 3. Build the markup
    markup = []
    
    # 3a. Add a clickable tracking button if a tracking number exists
    if tracking_number:
        # URL buttons are created differently in markups.create
        # We pass a dictionary with 'url' as the second element.
        markup.append((
            constants.language.track_order_button, 
            {"url": f"{SDEK_TRACKING_URL}{tracking_number}"}
        ))
    
    # 3b. Add a "Request Cancellation" button that leads to a confirmation step
    if status == 0:
        # This button now calls 'confirm_cancellation' instead of directly requesting it
        cancel_callback = f'{{"r":"user", "oid":{order_id}}}confirm_cancellation'
        markup.append((constants.language.request_cancellation, cancel_callback))
    
    markup.append((constants.language.back, f"{constants.JSON_USER}orders"))
    
    # 4. Format the final text (the tracking number is now in a button, so we can simplify the text)
    final_text = constants.language.order_details_text.format(
        status_text=get_status_text(status),
        date_created=date_created.strftime("%d.%m.%Y %H:%M"),
        # The tracking number text is now simpler as it's a separate button
        tracking_number=tracking_number if tracking_number else constants.language.no_tracking_number,
        items_text=items_text,
        address=address,
        phone_number=phone_number,
        comment=comment,
        total_price=total_price,
        currency_symbol=constants.config['settings']['currency_symbol']
    )

    # 5. Send the message
    await callback_query.message.edit_text(
        text=constants.language.order_details_title.format(order_id=order_id) + final_text,
        reply_markup=markups.create(markup),
        parse_mode="HTML",
    )