# src/callbacks/user/cart.py

from aiogram import types
import models
import constants
from markups import markups
import asyncio

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message=None) -> None:
    cart_items_dict = await user.cart.items.dict
    target = message if message else callback_query.message

    if not cart_items_dict:
        text = constants.language.cart_empty
        return await target.answer(text) if message else await target.edit_text(text)
    
    # --- START OF NEW REFACTORED LOGIC ---

    def changeCart_callback(item_id: int, state: int) -> str:
        return f'{{"r":"user","iid":{item_id},"s":{state},"d":"cart"}}changeCart'

    items_list_for_text = []
    markup_list = []
    currency = constants.config["settings"]["currency_symbol"]
    total_price = await user.cart.total_price

    for item_id, amount in cart_items_dict.items():
        item = models.items.Item(item_id)
        item_name, item_price = await asyncio.gather(item.name, item.price)
        
        # 1. Build the text line for the message body
        sub_total = amount * item_price
        items_list_for_text.append(
            f"• {item_name} ({amount} шт.) - {sub_total:.2f}{currency}"
        )

        # 2. Build the button row: [-] [Item Name] [+]
        # The middle button is a non-clickable label
        button_row = [
            (constants.language.minus, changeCart_callback(item_id, 0)),
            (item_name, constants.CALLBACK_DO_NOTHING),
            (constants.language.plus, changeCart_callback(item_id, 1))
        ]
        markup_list.append(button_row)

    # 3. Add the final action buttons
    markup_list.append(
        (constants.language.clear_cart, f"{constants.JSON_USER}clearCart")
    )
    markup_list.append(
        (constants.language.cart_checkout, f"{constants.JSON_USER}checkout")
    )

    # 4. Format the final text header
    text = constants.language.cart_header.format(
        items_list="\n".join(items_list_for_text), # Join the list of items into a single string
        total_price=f"{total_price:.2f}",
        currency_symbol=currency
    )
    
    final_markup = markups.create(markup_list)

    # --- END OF NEW REFACTORED LOGIC ---
    
    # Send the message (using HTML parse mode is safer)
    if message:
        await target.answer(text=text, reply_markup=final_markup, parse_mode="HTML")
    else:
        # Check for photo messages to avoid errors
        if callback_query.message.photo:
            await callback_query.message.delete()
            await target.answer(text=text, reply_markup=final_markup, parse_mode="HTML")
        else:
            await target.edit_text(text=text, reply_markup=final_markup, parse_mode="HTML")