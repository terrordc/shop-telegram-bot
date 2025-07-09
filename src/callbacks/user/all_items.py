# src/callbacks/user/all_items.py

import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # 1. Clean up any old menu components if coming from a callback.
    if callback_query:
        # Delete the main message (e.g., the item view).
        try:
            await callback_query.message.delete()
        except Exception:
            pass # Ignore if already deleted
        
        # If an old menu photo ID was passed, delete it too.
        if "pmid" in data:
            try:
                await callback_query.bot.delete_message(chat_id=user.id, message_id=data["pmid"])
            except Exception:
                pass # Ignore if already deleted
            
    # 2. Get items and handle the 'no items' case
    all_items = await models.items.get_all_visible_items()
    target_chat = message if message else callback_query.message

    if not all_items:
        text = "К сожалению, сейчас нет доступных товаров."
        return await target_chat.answer(text)

    # 3. Send the new header photo and get its message object
    # Create a fresh InputFile object every time to avoid "closed file" errors.
    photo_message = await target_chat.answer_photo(
        photo=types.InputFile(constants.ALL_ITEMS_IMAGE_PATH)
    )
    
    # 4. Build the keyboard, embedding the NEW photo's message_id
    markup = []
    for item in all_items:
        name = await item.name
        button_text = f"{name}"
        button_callback = f'{{"r":"user","rd":"all_items","iid":{item.id},"pmid":{photo_message.message_id}}}item'
        markup.append((button_text, button_callback))
    
    # 5. Send the text message with the keyboard attached
    await target_chat.answer(
        text=constants.language.all_items_caption,
        reply_markup=markups.create(markup)
    )