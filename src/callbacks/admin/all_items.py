# src/callbacks/admin/all_items.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import asyncio

ITEMS_PER_PAGE = 8 # You can adjust this number

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    page = data.get("p", 0) # Get page number from callback data, default to 0

    all_items = await models.items.get_all_items()

    if not all_items:
        await callback_query.message.edit_text(
            constants.language.no_items_to_edit,
            reply_markup=markups.create([(constants.language.back, f"{constants.JSON_ADMIN}items")])
        )
        return

    # Pagination logic
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    items_on_page = all_items[start_index:end_index]

    markup_list = []
    for item in items_on_page:
        item_name, is_hidden = await asyncio.gather(item.name, item.is_hidden)
        display_name = f"👁️ {item_name}" if not is_hidden else f"🚫 {item_name}"
        callback_data = f'{{"r":"admin","iid":{item.id}}}editItem'
        markup_list.append((display_name, callback_data))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append((constants.language.previous, f'{{"r":"admin","p":{page-1}}}all_items'))
    if end_index < len(all_items):
        nav_buttons.append((constants.language.next, f'{{"r":"admin","p":{page+1}}}all_items'))
    
    if nav_buttons:
        markup_list.append(nav_buttons)

    markup_list.append((constants.language.back, f"{constants.JSON_ADMIN}items"))
    
    final_markup = markups.create(markup_list)
    text = constants.language.select_item_to_edit

    # --- FIX STARTS HERE ---
    try:
        # Check if the message we are coming from has a photo.
        if callback_query.message.photo:
            # If so, we can't edit it into a text message.
            # We must delete it and send a new text message.
            await callback_query.message.delete()
            await callback_query.message.answer(text, reply_markup=final_markup)
        else:
            # If it was a text message, we can safely edit it.
            await callback_query.message.edit_text(text, reply_markup=final_markup)
    except Exception as e:
        # A general fallback for any other editing errors.
        print(f"Error in all_items handler: {e}")
        try:
            await callback_query.message.delete()
        except Exception:
            pass # Ignore if deletion also fails
        await callback_query.message.answer(text, reply_markup=final_markup)
    # --- FIX ENDS HERE ---