from aiogram import types
from aiogram.dispatcher import FSMContext
import models, states, constants, asyncio
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext):
    if not message or not message.text: return
    state_data = await state.get_data()
    item_id = state_data.get("item_id"); prompt_message_id = state_data.get("prompt_message_id")
    if not item_id: return await state.finish()

    item = models.items.Item(item_id)
    await item.set_usage(message.text)
    await message.delete()

    composition, usage = await asyncio.gather(item.composition, item.usage)
    text = constants.language.edit_details_menu.format(composition=composition or "Не задано", usage=usage or "Не задано")
    markup = markups.create([
        (constants.language.edit_composition, f'{{"r":"admin","iid":{item.id}}}editComposition'),
        (constants.language.edit_usage, f'{{"r":"admin","iid":{item.id}}}editUsage'),
        (constants.language.edit_details_image, f'{{"r":"admin","iid":{item.id}}}editDetailsImage'),
        (constants.language.back, f'{{"r":"admin","iid":{item.id}}}editItem')
    ])

    if prompt_message_id:
        try:
            await message.bot.edit_message_text(text, message.chat.id, prompt_message_id, reply_markup=markup, parse_mode="HTML")
        except:
            await message.answer(text, reply_markup=markup, parse_mode="HTML")

    await states.EditItem.main.set()