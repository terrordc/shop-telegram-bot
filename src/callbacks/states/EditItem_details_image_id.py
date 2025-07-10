from aiogram import types
from aiogram.dispatcher import FSMContext
import models, states, constants, asyncio
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext):
    if not message or not message.photo: return
    state_data = await state.get_data()
    item_id = state_data.get("item_id"); prompt_message_id = state_data.get("prompt_message_id")
    if not item_id: return await state.finish()
        
    item = models.items.Item(item_id)
    file_id = message.photo[-1].file_id
    await item.set_details_image_id(file_id)
    
    composition, usage = await asyncio.gather(item.composition, item.usage)
    text = constants.language.edit_details_menu.format(composition=composition or "Не задано", usage=usage or "Не задано")
    markup = markups.create([
        (constants.language.edit_composition, f'{{"r":"admin","iid":{item.id}}}editComposition'),
        (constants.language.edit_usage, f'{{"r":"admin","iid":{item.id}}}editUsage'),
        (constants.language.edit_details_image, f'{{"r":"admin","iid":{item.id}}}editDetailsImage'),
        (constants.language.back, f'{{"r":"admin","iid":{item.id}}}editItem')
    ])

    if prompt_message_id:
        try: # Delete the old text prompt
            await message.bot.delete_message(message.chat.id, prompt_message_id)
        except:
            pass # Ignore if it's already deleted
    
    # Send the new menu
    await message.answer("✅ Изображение для деталей обновлено.")
    await message.answer(text, reply_markup=markup, parse_mode="HTML")

    await states.EditItem.main.set()