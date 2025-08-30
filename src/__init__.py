# src/__init__.py - CLEANED AND CORRECTED

import asyncio, os, importlib, json, traceback
from aiogram import Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiohttp import web
from aiogram.dispatcher.webhook import configure_app
import dotenv

# --- Project Imports ---
import constants, config, utils, database, schedules, states
from markups import markups
import models.users as users
import models.items as items
import models.orders as orders
# At the top of src/__init__.py
from logger import setup_logger
# --- Bot Initialization ---
dotenv.load_dotenv(dotenv.find_dotenv())
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("No TOKEN found in environment variables!")

storage = MemoryStorage()
bot = constants.create_bot(TOKEN)
dp = Dispatcher(bot, storage=storage)
setup_logger(bot)
WEBHOOK_PATH_YOOKASSA = "/yookassa_webhook/"

# =================================================================================
# HANDLERS - ORDER MATTERS! Specific command handlers must come first.
# =================================================================================

# FIX 1: This handler is now correctly placed BEFORE the generic text handler.
@dp.message_handler(commands=["start"])
async def welcome(message: types.Message):
    await users.create_if_not_exist(message.chat.id, message.from_user.username)
    user = users.User(message.chat.id)
    markup = markups.main

    greeting_text = config.config["info"]["greeting"].replace("%s", message.from_user.full_name)

    if await user.is_admin:
        markup.add(types.KeyboardButton(constants.language.admin_panel))
        greeting_text += "\n\n⭐ **Вы вошли как администратор.**"

    if "sticker.tgs" in os.listdir("."):
        with open("sticker.tgs", "rb") as sticker:
            await bot.send_sticker(user.id, sticker)

    await bot.send_message(
        chat_id=user.id,
        text=greeting_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
@dp.message_handler(commands=["cart", "orders", "profile", "all_items", "faq", "support", "help"])
async def handle_menu_commands(message: types.Message):
    await users.create_if_not_exist(message.chat.id, message.from_user.username)
    user = users.User(message.chat.id)
    
    command = message.get_command(pure=True)
    destination = ""

    # --- Logic Router ---

    # Commands that open a new "view"
    if command == "cart":
        destination = "cart"
    elif command in ["orders", "profile"]:
        destination = "orders"
    elif command == "all_items":
        destination = "all_items"
    
    # Commands that send a direct message
    elif command == "faq":
        faq_url = config.config["info"]["faq_url"]
        text = f'Вы можете найти ответы на часто задаваемые вопросы на <a href="{faq_url}">нашей странице FAQ</a>.'
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
        return # Stop execution
    
    elif command == "support":
        support_username = config.config["info"]["support_username"]
        text = f'Для связи с поддержкой, пожалуйста, напишите нашему менеджеру: @{support_username}'
        await message.answer(text, parse_mode="HTML")
        return # Stop execution

    elif command == "help":
        await message.answer("Здесь будет раздел помощи.")
        return # Stop execution

    # --- Execution Logic for "view" commands ---
    if not destination:
        # This is a fallback for any commands we might have missed
        return await message.answer(constants.language.unknown_command)

    # This reuses the same logic as your text handler to open the correct view
    await importlib.import_module(f"callbacks.user.{destination}").execute(None, user, None, message, None)
# FIX 2: Added the decorator to register this as a command. Placed BEFORE generic text handler.

@dp.message_handler(commands=["testorder"])
async def create_test_order(message: types.Message, state: FSMContext):
    user = users.User(message.chat.id)
    if not await user.is_admin:
        return await message.answer("Эта команда только для администраторов.")

    try:
        # 1. Clear cart and add a test item
        await user.cart.items.clear()
        
        # --- START OF FIX ---
        # The .add() method only takes the item_id.
        await user.cart.items.add(1) 
        # --- END OF FIX ---

        # 2. Pre-fill state with dummy data
        dummy_data = {
            "full_name": "Тест Тестовый",
            "phone_number": "+79991234567",
            "address": "г. Москва, ул. Тестовая, д. 1, кв. 2",
            "comment": "Это тестовый заказ, созданный автоматически."
        }
        await state.set_data(dummy_data)

        # 3. Move the user directly to the confirmation state
        await states.Order.confirmation.set()

        # 4. Send the confirmation message
        total_price = await user.cart.total_price
        confirmation_text = (
            f"**Пожалуйста, подтвердите ваш заказ:**\n\n"
            f"**Имя:** `{dummy_data['full_name']}`\n"
            f"**Телефон:** `{dummy_data['phone_number']}`\n"
            f"**Адрес:** `{dummy_data['address']}`\n\n"
            f"**Итого к оплате: {total_price} RUB**"
        )
        confirm_keyboard = markups.create([[("✅ Подтвердить и оплатить", '{"r":"user"}create_payment')]])
        await message.answer(confirmation_text, reply_markup=confirm_keyboard, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"Не удалось создать тестовый заказ. Ошибка: {e}")
        await state.finish()
# This is the generic, "catch-all" handler for text buttons. It now comes last.
@dp.message_handler()
async def handle_text(message: types.Message):
    await users.create_if_not_exist(message.chat.id, message.from_user.username)
    user = users.User(message.chat.id)
    destination = ""
    role = "user"

    # This part remains the same
    if message.text == constants.language.faq:
        faq_url = config.config["info"]["faq_url"]
        return await message.answer(f'Вы можете найти ответы на часто задаваемые вопросы на <a href="{faq_url}">нашей странице FAQ</a>.', parse_mode="HTML", disable_web_page_preview=True)
    if message.text == constants.language.support:
        support_username = config.config["info"]["support_username"]
        return await message.answer(f'Для связи с поддержкой, пожалуйста, напишите нашему менеджеру: @{support_username}', parse_mode="HTML")

    match message.text:
        case constants.language.all_items:
            destination = "all_items"
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

# --- Callback Handlers (No changes needed here) ---
@dp.callback_query_handler(state=None)
async def process_callback_no_state(callback_query: types.CallbackQuery, state: FSMContext):
    # ... code is correct ...
    call_data = callback_query.data
    if call_data == constants.CALLBACK_DO_NOTHING: return await callback_query.answer()
    user = users.User(callback_query.message.chat.id)
    data = json.loads(call_data[:call_data.find("}") + 1])
    call = call_data[call_data.find("}") + 1:]
    if config.config["settings"]["debug"]: print(f"{call} | [{user.id}] | {data}")
    if data.get("r") == "admin" and not await user.is_admin: return await utils.sendNoPermission(callback_query.message)
    try:
        await importlib.import_module(f"callbacks.{data['r']}.{call}").execute(callback_query, user, data, None, state)
    except ModuleNotFoundError: await callback_query.answer(constants.language.unknown_command, show_alert=True)
    except Exception: traceback.print_exc()

@dp.callback_query_handler(state="*")
async def process_callback_in_state(callback_query: types.CallbackQuery, state: FSMContext):
    # ... code is correct ...
    call_data = callback_query.data
    if call_data == constants.CALLBACK_DO_NOTHING: return await callback_query.answer()
    user = users.User(callback_query.message.chat.id)
    data = json.loads(call_data[:call_data.find("}") + 1])
    call = call_data[call_data.find("}") + 1:]
    current_state_str = await state.get_state()
    if config.config["settings"]["debug"]: print(f"[STATE: {current_state_str}] {call} | [{user.id}] | {data}")
    if current_state_str:
        state_path = f"callbacks.states.{current_state_str.replace(':', '_')}"
        try:
            await importlib.import_module(state_path).execute(callback_query=callback_query, user=user, data=data, state=state)
        except ModuleNotFoundError: await utils.sendStateNotFound(callback_query.message)
        except Exception: traceback.print_exc()
    else:
        await state.finish()
        await callback_query.answer("Your session has expired.", show_alert=True)

# --- State Message Handler (No changes needed here) ---
@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def process_message_state(message: types.Message, state: FSMContext):
    # ... code is correct ...
    state_path = f"callbacks.states.{(await state.get_state()).replace(':', '_')}"
    try:
        await importlib.import_module(state_path).execute(callback_query=None, user=users.User(message.chat.id), data=None, message=message, state=state)
    except ModuleNotFoundError: await utils.sendStateNotFound(message)
    except Exception: traceback.print_exc()

# =================================================================================
# YOOKASSA WEBHOOK HANDLER
# =================================================================================

async def yookassa_webhook_handler(request: web.Request):
    try:
        notification = await request.json()
        event = notification.get("event")
        payment = notification.get("object", {})
        
        
        if event == "payment.succeeded":
            order_id = int(payment.get("metadata", {}).get("order_id"))
            if not order_id:
                return web.Response(status=200)

            print(f"✅ SUCCESSFUL payment for order #{order_id}")
            
            order = orders.Order(order_id)
            user = users.User(await order.user_id)
            
            # --- Business Logic ---
            await order.set_status(1) # Status 1 = "Processing"
            await user.cart.items.clear()
            
            # --- START OF FIX: Fetch ALL data before building ANY messages ---
            order_items = await order.items
            total_price = sum(item.price * item.amount for item in order_items)
            customer_name = await order.full_name
            customer_phone = await order.phone_number
            customer_address = await order.address
            customer_comment = await order.comment
            # --- END OF FIX ---

            # --- NOTIFICATION LOGIC ---
            
            # 2. Send simple notification to ALL admins
            admin_message = (
                f"**[АДМИН]** ✅ **Новый оплаченный заказ!**\n\n"
                f"Номер заказа: `#{order_id}`\n"
                f"Сумма: `{total_price}` RUB"
            )
            admin_ids = await users.get_all_admin_ids()
            for admin_id in admin_ids:
                try:
                    await bot.send_message(admin_id, admin_message, parse_mode="Markdown")
                except Exception as e:
                    print(f"Could not send notification to admin {admin_id}: {e}")

            # 3. Send DETAILED notification to the SDEK manager
            sdek_manager_id = None
            try:
                sdek_manager_id = config.config["info"]["sdek_manager_telegram_id"]
            except KeyError:
                print("WARNING: 'sdek_manager_telegram_id' not found in config.json")
            
            if sdek_manager_id:
                items_text_list = [f"• {item.title} ({item.amount} шт.)" for item in order_items]
                items_text = "\n".join(items_text_list)
                manager_message = (
                    f"📦 **Заказ #{order_id} готов к отправке (SDEK)**\n\n"
                    f"**Клиент:** `{customer_name}`\n"
                    f"**Телефон:** `{customer_phone}`\n"
                    f"**Адрес:** `{customer_address}`\n\n"
                    f"**Состав заказа:**\n{items_text}\n\n"
                    f"**Сумма:** `{total_price}` RUB\n"
                    f"**Комментарий:** `{customer_comment or 'Нет'}`"
                )
                try:
                    await bot.send_message(sdek_manager_id, manager_message, parse_mode="Markdown")
                except Exception as e:
                    print(f"Could not send notification to SDEK manager {sdek_manager_id}: {e}")
            
            # 4. Notify the user that their payment was successful
            await bot.send_message(
                chat_id=user.id,
                text=f"✅ Оплата заказа №{order_id} прошла успешно! Ваш заказ готовится к отправке."
            )
        return web.Response(status=200)

    except Exception as e:
        print(f"Error processing YooKassa webhook: {e}")
        traceback.print_exc()
        return web.Response(status=500)

# =================================================================================
# APPLICATION STARTUP
# =================================================================================

# In src/__init__.py
# REPLACE your entire block at the bottom with this one.

async def main():
    """The main entrypoint for the application."""

    # 1. Create database and tables if they don't exist
    if not os.path.exists("database.db"):
        print("Database not found. Creating tables...")
        tasks = [database.fetch(obj.database_table) for obj in [users.User(0), items.Item(0), orders.Order(0)]]
        # This is the correct way to run multiple tasks inside an async function
        await asyncio.gather(*tasks)
        print("Database tables created.")

    # 2. Configure the web application
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH_YOOKASSA, yookassa_webhook_handler)
    configure_app(dispatcher=dp, app=app, path='/')

    # 3. Register scheduled tasks
    async def run_scheduled_tasks(app_instance):
        await schedules.on_startup(dp)

    app.on_startup.append(run_scheduled_tasks)
    
    # 4. Run the application
    print("✅ Starting combined server for Telegram and YooKassa...")
    # We need a runner to correctly manage the web app lifecycle
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    # Keep the application running forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
    except Exception as e:
        # This is the final catch-all.
        logging.critical("Bot failed to start or crashed unexpectedly!", exc_info=True)