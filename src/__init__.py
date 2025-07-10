import asyncio, os, importlib, json, traceback
from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
import dotenv

import constants, config, utils, database, schedules, states
# --- FIX 1: Correctly import the 'markups' INSTANCE from the module ---
from markups import markups
import models.users as users
import models.items as items
import models.orders as orders

# --- Startup (This part is correct) ---
if not os.path.exists("database.db"):
    tasks = [
        database.fetch(object.database_table)
        for object in [users.User(0), items.Item(0), orders.Order(0)]
    ]
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))

dotenv.load_dotenv(dotenv.find_dotenv())
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("No token found!")
    exit(1)

storage = MemoryStorage()
bot = constants.create_bot(TOKEN)
dp = Dispatcher(bot, storage=storage)

# --- Message Handlers (Corrected) ---
@dp.message_handler(commands=["start"])
async def welcome(message: types.Message) -> None:
    await users.create_if_not_exist(message.chat.id, message.from_user.username)
    user = users.User(message.chat.id)
    # This line now works because of the corrected import
    markup = markups.main
    if await user.is_admin:
        markup.add(types.KeyboardButton(constants.language.admin_panel))
    if "sticker.tgs" in os.listdir("."):
        with open("sticker.tgs", "rb") as sticker:
            await bot.send_sticker(user.id, sticker)
    await bot.send_message(
        chat_id=user.id,
        text=config.config["info"]["greeting"].replace("%s", message.from_user.full_name),
        reply_markup=markup,
    )

@dp.message_handler()
async def handle_text(message: types.Message) -> None:
    await users.create_if_not_exist(message.chat.id, message.from_user.username)
    user = users.User(message.chat.id)
    destination = ""
    role = "user"
    if message.text == constants.language.faq:
        faq_url = config.config["info"]["faq_url"]
        text = f'Вы можете найти ответы на часто задаваемые вопросы на <a href="{faq_url}">нашей странице FAQ</a>.'
        return await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    if message.text == constants.language.support:
        support_username = config.config["info"]["support_username"]
        text = f'Для связи с поддержкой, пожалуйста, напишите нашему менеджеру: @{support_username}'
        return await message.answer(text, parse_mode="HTML")

    # --- FIX 2: Correctly match the main menu button text ---
    match message.text:
        case constants.language.all_items: # This should match the button text, e.g., "Каталог"
            destination = "all_items" # The destination file is correct
        case constants.language.cart:
            destination = "cart"
        case constants.language.profile:
            destination = "orders"
        case constants.language.admin_panel:
            destination = "adminPanel"
            role = "admin"

    if not destination:
        return await message.answer(constants.language.unknown_command)
    if role == "admin" and not await user.is_admin:
        return await utils.sendNoPermission(message)
    await importlib.import_module(f"callbacks.{role}.{destination}").execute(None, user, None, message, None)


# --- REFACTORED AND CORRECTED CALLBACK HANDLERS ---

# Handler 1: For when the user is NOT in a state.
@dp.callback_query_handler(state=None)
async def process_callback_no_state(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    call_data = callback_query.data
    if call_data == constants.CALLBACK_DO_NOTHING:
        return await callback_query.answer()

    user = users.User(callback_query.message.chat.id)
    data = json.loads(call_data[:call_data.find("}") + 1])
    call = call_data[call_data.find("}") + 1:]

    if config.config["settings"]["debug"]:
        print(f"{call} | [{user.id}] | {data}")

    if data.get("r") == "admin" and not await user.is_admin:
        return await utils.sendNoPermission(callback_query.message)

    try:
        execute_args = (callback_query, user, data, None, state)
        await importlib.import_module(f"callbacks.{data['r']}.{call}").execute(*execute_args)
    except ModuleNotFoundError:
        await callback_query.answer(constants.language.unknown_command, show_alert=True)
    except Exception:
        traceback.print_exc()

# Handler 2: For when the user IS in a state.
@dp.callback_query_handler(state="*")
async def process_callback_in_state(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    call_data = callback_query.data
    if call_data == constants.CALLBACK_DO_NOTHING:
        return await callback_query.answer()

    user = users.User(callback_query.message.chat.id)
    data = json.loads(call_data[:call_data.find("}") + 1])
    call = call_data[call_data.find("}") + 1:]
    
    current_state_str = await state.get_state()

    if config.config["settings"]["debug"]:
        print(f"[STATE: {current_state_str}] {call} | [{user.id}] | {data}")

    # The state handler itself will now manage all navigation, including 'cancel'.
    # This router's only job is to find the right state handler file.
    if current_state_str:
        state_path = f"callbacks.states.{current_state_str.replace(':', '_')}"
        try:
            await importlib.import_module(state_path).execute(callback_query=callback_query, user=user, data=data, state=state)
        except ModuleNotFoundError:
            await utils.sendStateNotFound(callback_query.message)
        except Exception:
            traceback.print_exc()
    else:
        # This is a fallback case, it shouldn't happen with this architecture
        await state.finish()
        await callback_query.answer("Your session has expired. Please try again.", show_alert=True)
        await callback_query.message.delete()

# --- Message handler for when in a state (This is correct) ---
@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def process_message_state(message: types.Message, state: FSMContext) -> None:
    state_path = f"callbacks.states.{(await state.get_state()).replace(':', '_')}"
    try:
        await importlib.import_module(state_path).execute(callback_query=None, user=users.User(message.chat.id), data=None, message=message, state=state)
    except ModuleNotFoundError:
        await utils.sendStateNotFound(message)
    except Exception:
        import traceback
        traceback.print_exc()

# --- Main startup (This is correct) ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, loop=constants.loop, on_startup=schedules.on_startup)