# src/callbacks/user/item.py

import asyncio
from aiogram import types
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # 1. Clean up the old menu components.
    # Delete the text/button part of the "All Items" menu.
    try:
        await callback_query.message.delete()
    except Exception:
        pass # Ignore if already deleted

    # If the menu's photo ID was passed, delete it.
    if "pmid" in data:
        try:
            await callback_query.bot.delete_message(chat_id=user.id, message_id=data["pmid"])
        except Exception:
            pass # Ignore if already deleted

    # 2. Fetch all data for the item view
    item = models.items.Item(data["iid"])
    item_text, image_id, cart_dict = await asyncio.gather(
        item.format_text(constants.config["info"]["item_template"], constants.config["settings"]["currency_symbol"]),
        item.image_id,
        user.cart.items.dict,
    )

    # 3. Build the keyboard for the item view
    def cart_callback(state: int):
        return f'{{"r":"user","iid":{item.id},"s":{state},"d":"item"}}changeCart'

    item_id_str = str(item.id)
    if item_id_str in cart_dict:
        cart_buttons = (
            (constants.language.minus, cart_callback(0)),
            (cart_dict[item_id_str], constants.CALLBACK_DO_NOTHING),
            (constants.language.plus, cart_callback(1)),
        )
    else:
        cart_buttons = ((constants.language.add_to_cart, cart_callback(1)),)

    # The "Back" button needs to be simple, as there's nothing to pass forward anymore.
    back_button = (constants.language.back, f'{{"r":"user"}}all_items')
    
    details_button = (constants.language.item_details_button, f'{{"r":"user","iid":{item.id}}}item_details')
    
    markup = markups.create([
        [details_button],
        cart_buttons,
        [back_button]
    ])

    # 4. Send the new item view
    target_chat = callback_query.message

    if image_id:
        # If the item has an image, send a new photo message.
        await target_chat.answer_photo(
            photo=image_id,
            caption=item_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    else:
        # Otherwise, send a new text message.
        await target_chat.answer(
            text=item_text,
            reply_markup=markup,
            parse_mode="HTML"
        )