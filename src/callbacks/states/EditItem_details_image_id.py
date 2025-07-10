from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import states
from .EditItem_main import _send_details_menu

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext):
    if not message or not message.photo: return
    
    state_data = await state.get_data()
    item_id = state_data.get("item_id")
    prompt_message_id = state_data.get("prompt_message_id")
    if not item_id: return await state.finish()
        
    item = models.items.Item(item_id)
    file_id = message.photo[-1].file_id
    await item.set_details_image_id(file_id)

    # The user's sent photo is good feedback, we can leave it.
    # Just delete the old prompt message.
    if prompt_message_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_message_id)
        except:
            pass

    await _send_details_menu(message, item)
    await states.EditItem.main.set()