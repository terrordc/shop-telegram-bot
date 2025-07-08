# src/callbacks/user/all_items.py

import asyncio
from aiogram import types
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message=None) -> None:
    # 1. Clean up old menu photo if coming from a "Back" button
    if callback_query and "pmid" in data:
        try:
            await callback_query.bot.delete_message(chat_id=user.id, message_id=data["pmid"])
        except Exception:
            pass
            
    # 2. Get items and handle the 'no items' case
    all_items = await models.items.get_all_visible_items()
    if not all_items:
        text = "К сожалению, сейчас нет доступных товаров."
        # Use the correct context to send the message
        target = message if message else callback_query.message
        return await target.answer(text) if message else await target.edit_text(text)

    # 3. Send the new header photo and get its message object
    target_chat = message if message else callback_query.message
    # Create a fresh InputFile object right before use
    photo_message = await target_chat.answer_photo(photo=types.InputFile(constants.ALL_ITEMS_IMAGE_PATH))
    
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
    
    # 6. Clean up the previous message (e.g., the item view) if coming from a callback
    if callback_query:
        await callback_query.message.delete()