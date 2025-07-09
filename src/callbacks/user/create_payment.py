# src/callbacks/user/create_payment.py

import asyncio
import aiohttp # Make sure you have this library installed: pip install aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # 1. Acknowledge the press and show a loading message to the user
    await callback_query.message.edit_text("⏳ Создаём ваш заказ, пожалуйста, подождите...")

    # 2. Retrieve all collected data from the state and the user's cart
    state_data = await state.get_data()
    cart_items_dict, total_price = await asyncio.gather(
        user.cart.items.dict,
        user.cart.total_price
    )

    # 3. (Simulated) Create an order in the local database
    # In a real scenario, this would return a new order object with a unique ID.
    # We will pretend it returns an object with id=123.
    # YOU WILL NEED TO IMPLEMENT: new_order = await models.orders.create(...)
    class MockOrder:
        id = 123
        async def set_external_id(self, eid): print(f"Order {self.id} external ID set to {eid}")

    new_order = MockOrder()
    print(f"--- Simulating Order Creation: Order #{new_order.id} created locally. ---")

    # 4. Prepare the data payload for the SDEK API
    items_for_api = []
    for item_id, amount in cart_items_dict.items():
        item = models.items.Item(item_id)
        name, price = await asyncio.gather(item.name, item.price)
        items_for_api.append({"sku": item_id, "name": name, "quantity": amount, "price": price})

    sdek_payload = {
        "local_order_id": new_order.id,
        "customer_phone": state_data.get('phone_number'),
        "delivery_address": state_data.get('address'),
        "comment": state_data.get('comment'),
        "items": items_for_api,
        "total_price": total_price
    }

    # 5. Send the data to a dummy API (httpbin.org is perfect for this)
    sdek_uuid = None
    try:
        async with aiohttp.ClientSession() as session:
            # We send our data to httpbin, which will echo it back in the response
            api_url = "https://httpbin.org/post"
            async with session.post(api_url, json=sdek_payload) as response:
                if response.status == 200:
                    response_json = await response.json()
                    # We pretend SDEK returns a unique ID for tracking.
                    # We'll just make one up for this example.
                    sdek_uuid = f"SDEK-{new_order.id}-{user.id}"
                    
                    # In real code, you would save this ID to your database order record
                    await new_order.set_external_id(sdek_uuid)

                    print("--- API Call Success ---")
                    print("Sent to SDEK:", sdek_payload)
                    print("Received from httpbin:", response_json)
                else:
                    # Handle API error
                    print(f"--- API Call Failed: Status {response.status} ---")
                    await callback_query.message.edit_text(constants.language.order_creation_error)
                    return

    except aiohttp.ClientError as e:
        # Handle network error
        print(f"--- Network Error During API Call: {e} ---")
        await callback_query.message.edit_text(constants.language.order_creation_error)
        return

    # 6. If everything was successful, clear the user's cart
    await user.cart.clear()

    # 7. Notify the user of the success
    success_text = constants.language.order_creation_success.format(
        order_id=new_order.id,
        sdek_id=sdek_uuid
    )
    await callback_query.message.edit_text(text=success_text)