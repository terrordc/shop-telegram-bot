from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import states
from .EditItem_main import _send_details_menu

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext):
    if not message or not message.text: return
    
    state_data = await state.get_data()
    item_id = state_data.get("item_id")
    prompt_message_id = state_data.get("prompt_message_id")
    if not item_id: return await state.finish()

    # 1. Save the data
    item = models.items.Item(item_id)
    await item.set_composition(message.text)
    
    # 2. Clean up BOTH old messages
    await message.delete() # Deletes user's input
    if prompt_message_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_message_id)
        except:
            pass # Ignore if it's already gone

    # 3. Send the fresh menu
    await _send_details_menu(message, item)
    await states.EditItem.main.set()