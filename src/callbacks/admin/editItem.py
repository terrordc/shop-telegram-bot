# src/callbacks/admin/editItem.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
import models
import constants
from markups import markups
import states


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    item = models.items.Item(data["iid"])

    # --- FIX: Removed item.category_id from gather ---
    item_image, text, is_hidden = await asyncio.gather(
        item.image_id,
        item.format_text(
            constants.config["info"]["item_template"],
            constants.config["settings"]["currency_symbol"]
        ),
        item.is_hidden
    )

    markup_buttons = [
        (constants.language.edit_name, f'{{"r":"admin","iid":{item.id}}}editItemName'),
        (constants.language.edit_description, f'{{"r":"admin","iid":{item.id}}}editItemDescription'),
        (constants.language.edit_price, f'{{"r":"admin","iid":{item.id}}}editItemPrice'),
        (constants.language.edit_image, f'{{"r":"admin","iid":{item.id}}}editItemImage'),
        # --- NEW BUTTON FOR THE SUB-MENU ---
        (constants.language.edit_details, f'{{"r":"admin","iid":{item.id}}}editDetails'),
        (constants.language.show if is_hidden else constants.language.hide, f'{{"r":"admin","iid":{item.id}}}toggleIsHidden'),
        (constants.language.delete, f'{{"r":"admin","iid":{item.id}}}deleteItem'),
        # Back button now goes to the list of all items, which is more logical
        (constants.language.back, f'{{"r":"admin","d":"all_items"}}cancel')
    ]
    
    markup = markups.create(markup_buttons)

    await states.EditItem.main.set()
    await state.update_data(item_id=item.id) # Pre-load the item_id into the state

    # --- REFACTORED: Simplified sending logic ---
    if callback_query and callback_query.message.photo:
        # If the existing message has a photo, delete it and send a new one
        await callback_query.message.delete()
        await callback_query.message.answer_photo(
            photo=item_image,
            caption=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    elif item_image:
        # If the item has an image but the current message doesn't, send a new photo message
        if callback_query: await callback_query.message.delete()
        target = message or callback_query.message
        await target.answer_photo(
            photo=item_image,
            caption=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    else:
        # If no image involved, just edit or send a text message
        target = message or callback_query.message
        try:
            # Try to edit the existing message first
            await target.edit_text(text=text, reply_markup=markup,parse_mode="HTML")
        except Exception:
            # If editing fails (e.g., message is too old), send a new one
            if callback_query: await callback_query.message.delete()
            await target.answer(text=text, reply_markup=markup,parse_mode="HTML")