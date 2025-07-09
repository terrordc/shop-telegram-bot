# src/callbacks/user/changeCart.py

import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # --- START OF FIX ---
    # Define variables from the 'data' dict FIRST.
    item_id = data["iid"]
    add_or_remove_state = data["s"] # Renamed 'state' to avoid conflict with FSMContext 'state'
    source_view = data["d"]

    # Now we can safely use item_id to check the cart's state
    cart_before = await user.cart.items.dict
    is_first_add = str(item_id) not in cart_before and add_or_remove_state == 1
    # --- END OF FIX ---

    # Update the cart quantity
    if add_or_remove_state == 1: # Add
        await user.cart.items.add(item_id)
    else: # Remove
        await user.cart.items.remove(item_id)
    
    # Show the pop-up notification if it's the first add
    if is_first_add:
        await callback_query.answer(constants.language.item_added_to_cart)
    else:
        await callback_query.answer()

    # Re-fetch the cart data to get the new state
    cart_items_dict = await user.cart.items.dict

    # --- IF THE UPDATE WAS FROM THE ITEM VIEW ---
    if source_view == "item":
        item = models.items.Item(item_id)
        
        def cart_callback(new_s: int):
            return f'{{"r":"user","iid":{item.id},"s":{new_s},"d":"item"}}changeCart'

        item_id_str = str(item.id)

        if item_id_str in cart_items_dict:
            cart_buttons = (
                (constants.language.minus, cart_callback(0)),
                (cart_items_dict[item_id_str], constants.CALLBACK_DO_NOTHING),
                (constants.language.plus, cart_callback(1)),
            )
        else:
            # Note the extra comma to make it a tuple of tuples for the markup helper
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
        from . import cart
        await cart.execute(callback_query, user, data, message, state)