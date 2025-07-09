import asyncio
import os
import importlib
import json
from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
import dotenv

import constants
from config import config
from markups import markups
import models.users as users
import models.items as items
import models.categories as categories
import models.orders as orders
import utils
import database
import schedules

# First startup
if not os.path.exists("database.db"):
    tasks = [
        database.fetch(object.database_table)
        for object in [users.User(0), items.Item(0), categories.Category(0), orders.Order(0)]
    ]
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))


dotenv.load_dotenv(dotenv.find_dotenv())
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("No token found!")
    exit(1)


storage = MemoryStorage()
bot = constants.create_bot(TOKEN)
# bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

# @dp.message_handler(content_types=types.ContentType.PHOTO)
# async def dev_get_photo_id(message: types.Message):
#     # The last element in the 'photo' array is the highest quality one
#     file_id = message.photo[-1].file_id
#     print("--- PHOTO FILE ID RECEIVED ---")
#     print(file_id)
#     print("----------------------------")
#     await message.reply(f"Photo `file_id` received and printed to console:\n\n`{file_id}`", parse_mode="Markdown")

@dp.message_handler(commands=["start"])
async def welcome(message: types.Message) -> None:
    # ... (code to create user) ...
    user = users.User(message.chat.id)

    markup = markups.main
    if await user.is_admin:
        markup.add(types.KeyboardButton(constants.language.admin_panel))

    if "sticker.tgs" in os.listdir("."):
        with open("sticker.tgs", "rb") as sticker:
            await bot.send_sticker(user.id, sticker)

    await bot.send_message(
        chat_id=user.id,
        text=config["info"]["greeting"].replace("%s", message.from_user.full_name),
        reply_markup=markup,
    )

@dp.message_handler()
async def handle_text(message: types.Message) -> None:
    await users.create_if_not_exist(message.chat.id, message.from_user.username)
    user = users.User(message.chat.id)
    destination = ""
    role = "user"

    # --- START OF MODIFICATION ---

    if message.text == constants.language.faq:
        faq_url = constants.config["info"]["faq_url"]
        # Embed the link directly in the text using HTML's <a> tag
        text = f'Вы можете найти ответы на часто задаваемые вопросы на <a href="{faq_url}">нашей странице FAQ</a>.'
        # We send the message without any extra buttons
        return await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

    if message.text == constants.language.support:
        support_username = constants.config["info"]["support_username"]
        # Embed the link directly in the text
        text = f'Для связи с поддержкой, пожалуйста, напишите нашему менеджеру: @{support_username}'
        # You can also use an HTML link here for a cleaner look
        # text = f'Для связи с поддержкой, пожалуйста, <a href="https://t.me/{support_username}">напишите нашему менеджеру</a>.'
        return await message.answer(text, parse_mode="HTML")


    # The existing menu navigation logic remains below
    match message.text:
        case constants.language.catalogue:
            destination = "all_items"
        case constants.language.cart:
            destination = "cart"
        case constants.language.profile:
            destination = "orders"
        # We no longer need a 'faq' case here since it's handled above
        case constants.language.admin_panel:
            destination = "adminPanel"
            role = "admin"



    if not destination:
        await message.answer(constants.language.unknown_command)
        return

    permission = True
    match role:
        case "admin":
            permission = await user.is_admin
    if not permission:
        return await utils.sendNoPermission(message)

    await importlib.import_module(f"callbacks.{role}.{destination}").execute(None, user, None, message, None)

@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext) -> None: 
    call = callback_query.data
    # Change "None" to our new constant
    if call == constants.CALLBACK_DO_NOTHING:
        return await callback_query.answer() # It's good practice to answer the callback so the loading icon disappears


    user = users.User(callback_query.message.chat.id)
    data = json.loads(call[:call.index("}")+1])
    call = call[call.index("}")+1:]
    execute_args = (callback_query, user, data, None, state)

    if config["settings"]["debug"]:
        print(f"{call} | [{user.id}] | {data}")
    if call in ["cancel", "skip"]:
        if "d" in data:
            return await importlib.import_module(f"callbacks.{data['r']}.{data['d']}").execute(*execute_args)

        await callback_query.message.delete()
        return

    permission = True
    match data["r"]:
        case "admin":
            permission = await user.is_admin

    if not permission:
        return await utils.sendNoPermission(callback_query.message)

    try:
        return await importlib.import_module(f"callbacks.{data['r']}.{call}").execute(*execute_args)
    except ModuleNotFoundError:
        await callback_query.answer(
            text=constants.language.unknown_command
        )


def parse_state(current_state: State) -> str:
    current_state_str = str(current_state)
    return current_state_str[current_state_str.index("'")+1:-2]


# states
@dp.callback_query_handler(state="*")
async def process_callback_state(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    call = callback_query.data
    # Add the same check here
    if call == constants.CALLBACK_DO_NOTHING:
        return await callback_query.answer()

    user = users.User(callback_query.message.chat.id)
    data = json.loads(call[:call.index("}")+1])
    call = call[call.index("}")+1:]
    execute_args = (callback_query, user, data)

    if config["settings"]["debug"]:
        print(f"[STATE: {await state.get_state()}] {call} | [{user.id}] | {data}")

    if call == "cancel":
        await state.finish()
        if "d" in data:
            return await importlib.import_module(f"callbacks.{data['r']}.{data['d']}").execute(*execute_args)

        await callback_query.message.edit_text(
            text=constants.language.state_cancelled,
        )
        return

    
    state_path = f"callbacks.states.{(await state.get_state()).replace(':', '_')}"
    try:
        await importlib.import_module(state_path).execute(callback_query=callback_query, user=user, data=data, state=state)
    except ModuleNotFoundError:
        await utils.sendStateNotFound(callback_query.message)
    except:
        import traceback
        traceback.print_exc()


@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def process_message_state(message: types.Message, state: FSMContext) -> None:
    state_path = f"callbacks.states.{(await state.get_state()).replace(':', '_')}"

    try:
        await importlib.import_module(state_path).execute(callback_query=None, user=users.User(message.chat.id), data=None, message=message, state=state)
    except ModuleNotFoundError:
        await utils.sendStateNotFound(message)
    except:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, loop=constants.loop, on_startup=schedules.on_startup)

