# src/callbacks/user/changeCart.py

import asyncio
from aiogram import types
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    item_id = data["iid"]
    state = data["s"]
    source_view = data["d"]

    # --- START OF MODIFICATION ---
    # Get the state of the cart BEFORE we change it
    cart_before = await user.cart.items.dict
    is_first_add = str(item_id) not in cart_before and state == 1
    # --- END OF MODIFICATION ---

    # Update the cart quantity
    if state == 1:
        await user.cart.items.add(item_id)
    else:
        await user.cart.items.remove(item_id)
    
    # --- START OF MODIFICATION ---
    # If this was the first time adding the item, show the pop-up notification.
    # Otherwise, just send a blank answer to stop the loading animation.
    if is_first_add:
        await callback_query.answer(constants.language.item_added_to_cart)
    else:
        await callback_query.answer()
    # --- END OF MODIFICATION ---

    # Re-fetch the cart data to get the new state
    cart_items_dict = await user.cart.items.dict

    # 3. Rebuild the appropriate markup based on where the click came from
    # --- IF THE UPDATE WAS FROM THE ITEM VIEW ---
    if source_view == "item":
        # We need to rebuild the item view's keyboard
        item = models.items.Item(item_id)
        
        def cart_callback(new_state: int):
            return f'{{"r":"user","iid":{item.id},"s":{new_state},"d":"item"}}changeCart'

        item_id_str = str(item.id)

        if item_id_str in cart_items_dict:
            cart_buttons = (
                (constants.language.minus, cart_callback(0)),
                (cart_items_dict[item_id_str], constants.CALLBACK_DO_NOTHING),
                (constants.language.plus, cart_callback(1)),
            )
        else:
            cart_buttons = ((constants.language.add_to_cart, cart_callback(1)),)
        
        # We need to rebuild the other buttons too
        photo_id_breadcrumb = f',"pmid":{data["pmid"]}' if "pmid" in data else ""
        details_button = (constants.language.item_details_button, f'{{"r":"user","iid":{item.id}{photo_id_breadcrumb}}}item_details')
        back_button = (constants.language.back, f'{{"r":"user"{photo_id_breadcrumb}}}all_items')

        new_markup = markups.create([
            [details_button],
            cart_buttons,
            [back_button]
        ])

        await callback_query.message.edit_reply_markup(reply_markup=new_markup)

    # --- IF THE UPDATE WAS FROM THE CART VIEW ---
    elif source_view == "cart":
        # We need to rebuild the entire cart view
        # The simplest way is to re-trigger the cart handler, which already does a smooth edit.
        from . import cart
        await cart.execute(callback_query, user, data)