# At the top of src/callbacks/states/Order_confirmation.py

import asyncio
import json
import datetime
import os  # <-- ADD THIS
import uuid  # <-- ADD THIS
from aiogram import types
from aiogram.dispatcher import FSMContext
from yookassa import Configuration, Payment  # <-- ADD THIS
from yookassa.domain.models.currency import Currency  # <-- ADD THIS
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder  # <-- ADD THIS
import models
import constants
from services import sdek_api
from markups import markups # <-- ADD THIS to use your markup creator

# In src/callbacks/states/Order_confirmation.py
# REPLACE the old execute function with this one

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # --- START OF FIX ---
    # Check if this was triggered by a button press (a callback)
    if callback_query:
        # If it's a callback, we can edit the message and proceed with payment logic
        await callback_query.message.edit_text(constants.language.order_processing)
    else:
        # If it was triggered by a random text message, just ignore it and do nothing.
        # This prevents the crash.
        return
    state_data = await state.get_data()
    cart_items_dict, total_price = await asyncio.gather(
        user.cart.items.dict,
        user.cart.total_price
    )

    # 2. Prepare item data for the database
    items_for_db = []
    for item_id, amount in cart_items_dict.items():
        item = models.items.Item(item_id)
        item_name, item_price = await asyncio.gather(item.name, item.price)
        items_for_db.append({ "id": item_id, "amount": amount, "title": item_name, "price": item_price })
    items_json = json.dumps(items_for_db)
    
    # 3. Create the order in your database (this is correct)
    new_order = await models.orders.create(
        user_id=user.id,
        items_json=items_json,
        date_created=datetime.datetime.now().strftime(constants.TIME_FORMAT),
        full_name=state_data.get("full_name"),
        address=state_data.get("address"),
        phone_number=state_data.get("phone_number"),
        comment=state_data.get("comment"),
        status=6 
    )

    # --- START OF YOOKASSA INTEGRATION ---
    try:
        shop_id = os.environ.get('YOOKASSA_SHOP_ID')
        secret_key = os.environ.get('YOOKASSA_SECRET_KEY')

        if not shop_id or not secret_key:
            await callback_query.message.edit_text("Ошибка: Платежная система не настроена.")
            print("ERROR: YooKassa credentials not found.")
            return

        Configuration.configure(shop_id, secret_key)
        
        idempotence_key = str(uuid.uuid4())
        description = f"Оплата заказа №{new_order.id}"
        # This will get your bot's username automatically for the return URL
        bot_user = await constants.bot.get_me() 
        return_url = f'https://t.me/{bot_user.username}'

        builder = PaymentRequestBuilder()
        builder.set_amount({"value": str(total_price), "currency": Currency.RUB}) \
               .set_capture(True) \
               .set_confirmation({"type": "redirect", "return_url": return_url}) \
               .set_description(description) \
               .set_metadata({'order_id': new_order.id}) # Pass your internal order ID to YooKassa

        payment_request = builder.build()
        res = Payment.create(payment_request, idempotence_key)
        payment_link = res.confirmation.confirmation_url

    except Exception as e:
        await callback_query.message.edit_text("Не удалось создать ссылку для оплаты. Пожалуйста, свяжитесь с администратором.")
        print(f"YooKassa API Error: {e}")
        return
    # --- END OF YOOKASSA INTEGRATION ---

    # 5. Create the payment button using your existing markup creator
    payment_keyboard = markups.create([
        [("➡️ Оплатить заказ", {"url": payment_link})]
    ])

    # 6. Send the payment link to the user
    await callback_query.message.edit_text(
        text=f"Ваш заказ №{new_order.id} создан.\n\nНажмите кнопку ниже, чтобы перейти к оплате.",
        reply_markup=payment_keyboard
    )

    # 7. IMPORTANT: We do NOT clear the cart or finish the state here anymore.
    # That should happen only AFTER YooKassa confirms the payment.
    # So we are deleting the old code that did that.
    #
    # OLD CODE TO DELETE:
    # sdek_payload = { ... }
    # tracking_number = await sdek_api.create_shipment(sdek_payload)
    # await new_order.set_tracking_number(tracking_number)
    # await user.cart.items.clear()
    # await state.finish()
    # await callback_query.message.edit_text(...)