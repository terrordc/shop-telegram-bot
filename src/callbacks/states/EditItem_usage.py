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

    item = models.items.Item(item_id)
    await item.set_usage(message.text)
    
    await message.delete()
    if prompt_message_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_message_id)
        except:
            pass

    await _send_details_menu(message, item)
    await states.EditItem.main.set()