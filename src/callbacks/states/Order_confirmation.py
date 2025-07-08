# src/callbacks/states/Order_confirmation.py

import asyncio
import json
import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from services import sdek_api # Import our dummy API

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    # This handler is triggered when the user presses "Confirm and Pay"
    # The callback_data for this button is 'create_payment'

    # Give user instant feedback
    await callback_query.message.edit_text(constants.language.order_processing)

    # 1. Retrieve all data from the state and the user's cart
    state_data = await state.get_data()
    cart_items_dict, total_price = await asyncio.gather(
        user.cart.items.dict,
        user.cart.total_price
    )

    # 2. Prepare the items data for the database in the required JSON format
    items_for_db = []
    for item_id, amount in cart_items_dict.items():
        item = models.items.Item(item_id)
        item_name, item_price = await asyncio.gather(item.name, item.price)
        items_for_db.append({
            "id": item_id,
            "amount": amount,
            "title": item_name,
            "price": item_price
        })
    items_json = json.dumps(items_for_db)
    
    # 3. Create the order in your database
    new_order = await models.orders.create(
        user_id=user.id,
        items_json=items_json,
        date_created=datetime.datetime.now().strftime(constants.TIME_FORMAT),
        address=state_data.get("address"),
        phone_number=state_data.get("phone_number"),
        comment=state_data.get("comment")
    )

    # 4. Send data to the SDEK API and get a tracking number
    sdek_payload = {
        "order_id": new_order.id,
        "customer_phone": state_data.get("phone_number"),
        "delivery_address": state_data.get("address"),
        "items": items_for_db,
        "total_price": total_price
    }
    tracking_number = await sdek_api.create_shipment(sdek_payload)

    await new_order.set_tracking_number(tracking_number)

    # 5. Clean up: clear the user's cart and finish the state
    await user.cart.items.clear()
    await state.finish()

    # 6. Inform the user of success
    await callback_query.message.edit_text(
        text=constants.language.order_success_message.format(
            order_id=new_order.id,
            tracking_number=tracking_number
        ),
        parse_mode="HTML"
    )