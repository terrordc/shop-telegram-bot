# Misc buttons
try_again = "Попробуйте ещё раз."
skip = "⏭ Пропустить"
back = "🔙 Назад"
skip = "⏭ Пропустить"
tick = "✅"
cross = "❌"
yes = "✅ Да"
no = "❌ Нет"
enabled = "✅ Включено"
disabled = "❌ Выключено"
error = "Произошла ошибка!"
or_press_back = "или нажмите на кнопку \"Назад\"."
or_press_skip = "или нажмите на кнопку \"Пропустить\"."
hide = "🙈 Скрыть"
show = "🐵 Показать"
delete = "❌ Удалить"
reset = "❌ Сбросить"
no_permission = "У вас нет прав для выполнения данной команды!"
unknown_command = "Не могу понять команду :("
cross = "❌"
too_many_categories = "Слишком много категорий!"
unknown_call_stop_state = "Бот ожидает от вас ввода данных, но вы ничего не ввели. Для выхода из режима ввода данных нажмите на кнопку ниже."
state_cancelled = "Вы отменили операцию."
unknown_error = "Произошла неизвестная ошибка!"

# main markup
admin_panel = "🔴 Админ панель"
faq = "❓ Часто задаваемые вопросы"
profile = "📦 Мои заказы"
cart = "🛒 Корзина"
cart_header = """
🛒 <b>Корзина</b>

<b>Товары:</b>
{items_list}

<b>Общая стоимость:</b> {total_price}{currency_symbol}
"""
support = "✍️ Поддержка" 

# Cart
payment_method = "💳 Способ оплаты"
choose_payment_method = "Выберите способ оплаты:"
def format_delivery(delivery_price: int) -> str:
    return f"🚚 Доставка: {delivery_price} руб."
delivery = "🚚 Доставка"
self_pickup = "🖐️ Самовывоз"
cart_empty = "Ваша корзина пуста!"
def cart_total_price(price: float, currency_sym: str) -> str:
    return f"🛒 Итоговая цена: {price:.2f} {currency_sym}"

# Admin panel tabs
item_management = "📦 Управление товаром"
no_categories = "Создайте хотя бы одну категорию перед созданием товара!"
user_management = "🧍 Управление пользователями"
category_management = "Управление категориями"
stats = "📈 Статистика"
settings = "⚙ Настройки"

# Main settings
language = "🌐 Язык"
choose_a_language = f"Выберите язык {or_press_skip}:"
language_was_set = "Язык был успешно изменен! Для применения изменений перезапустите бота."
english = "🇬🇧 Английский"
russian = "🇷🇺 Русский"
input_greeting = "Форматирование: \n\"%s\" - ник пользователя\n\nВведите приветственное сообщение:"
greeting_was_set = "Приветственное сообщение было успешно изменено!"

greeting = "👋 Приветствие"

# FAQ
contacts = "📞 Контакты"
refund_policy = "🎫 Политика возврата"

# Profile
my_orders = "📂 Мои заказы"
cancel_order = "❌ Отменить заказ"
restore_order = "✅ Восстановить заказ"
my_support_tickets = "🙋 Мои тикеты в тех. поддержку"
enable_notif = "🔔Включить оповещения о заказах"
disable_notif = "🔕Выключить оповещения о заказах"

# Catalogue / Item / Cart
search = "🔍 Найти"
add_to_cart = "🛒 Добавить в корзину"
not_in_stock = "❌ Нет в наличии"
cart_is_empty = "Корзина пуста."
category_is_empty = "Категория пуста."
textpickup = "✅Самовывоз"
def delivery_on(price): return f"✅ Доставка - {price}руб."
def delivery_off(price): return f"❌ Доставка - {price}руб."
cart_checkout = "Оформить заказ"
clear_cart = "Очистить корзину"
status_processing = "Обрабатывается"
status_delivery = "Ожидает доставки"
status_done = "Готов"
status_cancelled = "Отменён"
def item(item):
    stock = "под заказ" if item.is_custom else f"{item.amount}"
    return f"{item.name}\n{item.price:.2f} руб.\nВ наличии: {stock}\n{item.description}"

# Category management
add_category = "🛍️ Добавить категорию"
edit_category = "✏️ Редактировать категорию"
input_category_name = f"Введите название категории {or_press_back}"
set_parent_category = f"📁 Выберите родительскую категорию {or_press_skip}"
category_created = "Категория успешно создана."
def format_category(category_id, category_name, category_parent_id, category_parent_name):
    return f"Категория: [{category_id}]{category_name}\nРодительская категория: {f'[{category_parent_id}]{category_parent_name}' if category_parent_id else 'Нет'}"
edit_parent_category = "📁 Изменить родительскую категорию"
choose_a_category_to_edit = "Выберите категорию для редактирования:"
confirm_delete_category = "Вы уверены, что хотите удалить категорию?"
category_deleted = "Категория успешно удалена."

# Item management
def format_editItemsCategory_text(category_name: str) -> str:
    return f"Выберите товар для редактирования в категории {category_name}:"
add_item = "🗃️ Добавить товар"
edit_item = "✏️ Редактировать товар"

edit_name = "📋 Изменить название"
input_item_name = f"Введите название товара {or_press_back}"

choose_category = "📁 Выберите категорию"
select_item_category = f"📁 Выберите категорию товара {or_press_back}"
edit_category = "✏️ Изменить категорию"

input_item_description = f"Введите описание товара {or_press_back}"
edit_description = "📝 Изменить описание"

input_item_price = f"Введите цену товара {or_press_back}"
edit_price = "💰 Изменить цену"
price_must_be_number = "Цена должна быть числом."

send_item_images = f"🖼️ Отправьте изображение товара {or_press_skip}"
send_item_changed_images = f"🖼️ Отправьте изображение товара {or_press_back}"
delete_image = "❌ Удалить изображение"
edit_image = "🖼️ Изменить изображение"


confirm_delete_item = "Вы уверены, что хотите удалить товар?"
item_was_deleted = "Товар успешно удален."
change_desc = "📝 Изменить описание"
change_price = "🏷️ Изменить цену"
change_item_cat = "🛍️ Изменить категорию"
change_stock = "📦 Изменить кол-во"
def format_confirm_item(name: str, description: str, category_id: int, price: float, images: list[str]) -> str:
    return f"Товар: {name}\nОписание: {description}\nКатегория: {category_id}\nЦена: {price}\nId изображения: {images}\n\nВы уверены, что хотите создать товар?"
item_added = "Товар успешно добавлен."

# User management
user_does_not_exist = "Пользователь не найден. {try_again}"
def format_user_profile(id: int, username: str, registration_date: str, is_admin: bool, is_manager: bool) -> str:
    role = "Пользователь"
    if is_admin:
        role = "Администратор"
    elif is_manager:
        role = "Менеджер"
    return f"ID: {id}\nИмя: {username}\nДата регистрации: {registration_date}\nРоль: {role}"
invalid_user_id = "Неверный ID пользователя. {try_again}"

user_profile = "📁Профиль пользователя"
input_user_id = f"Введите ID пользователя {or_press_back}"
notify_everyone = "🔔Оповещение всем пользователям"
input_notification = f"Введите текст оповещения {or_press_back}"
def confirm_notification(text: str) -> str:
    return f"Вы уверены, что хотите отправить оповещение?\nТекст:\n{text}"
def notification_sent(done_users: int, total_users: int) -> str:
    return f"Оповещение успешно отправлено {done_users}/{total_users} пользователям."
orders = "📁 Управление заказами"
remove_manager_role = "👨‍💼 Убрать роль менеджера"
add_manager_role = "👨‍💼 Сделать менеджером"
remove_admin_role = "🔴 Убрать роль администратора"
add_admin_role = "🔴 Сделать администратором"
def change_order_status(status): return f"Изменить статус на \"{status}\""

# Shop stats
registration_stats = "👥Статистика регистраций"
order_stats = "📦Статистика заказов"
all_time = "За всё время"
monthly = "За последние 30 дней"
weekly = "За последние 7 дней"
daily = "За последние 24 часа"

# Payment settings
yoomoney = "🟢 ЮMoney"
qiwi = "🏧 QIWI"

# in src/localization/ru.py
approve_cancellation = "✅ Одобрить отмену"
deny_cancellation = "❌ Отклонить отмену"
mark_as_shipped = "🚚 Отметить как отправленный"

# Shop settings
main_settings = "🛠️ Основные настройки"
item_settings = "🗃️ Настройки товаров"
payment_settings = "💳 Настройки оплаты"
additional_settings = "📖 Дополнительные настройки"
custom_commands = "📖 Команды"
add_command = "📝 Добавить команду"
clean_logs = "📖 Очистить логи"
clean_logs_text = "⚠️ Вы уверены, что хотите очистить логи? Они будут удалены без возможности восстановления!\n(Логи за сегодняшний день не будут удалены)"
backups = "💾 Резервное копирование"
update_backup = "🔄 Обновить резервную копию"
load_backup = "💿 Загрузить резервную копию"
clean_backups = "🧹 Очистка резервных копий"
system_settings = "💻 Настройки системы"
clean_images = "🗑️ Удалить неиспользуемые изображения"
clean_images_text = "⚠️ Вы уверены, что хотите удалить неспользуемые изображения? Они будут удалены без возможности восстановления!"
clean_database = "📚 Очистить базу данных"
clean_database_text = "⚠️ Вы уверены, что хотите очистить базу данных? Все данные будут удалены без возможности восстановления!"
reset_settings = "⚙️ Сбросить настройки"
resert_settings_text = "⚠️ Вы уверены, что хотите сбросить настройки? Все данные будут удалены без возможности восстановления!"
image = "🖼️ Изображение"
checkout_settings = "🛒 Настройки оформления заказа"
stats_settings = "📈 Настройки статистики"
graph_color = "🌈 Цвет графика"
border_width = "🔲 Ширина обводки"
title_font_size = "ℹ️ Размер названия графика"
axis_font_size = "↔️Размер текста для осей"
tick_font_size = "🔢Размер текста для делений"
unavailable = "⛔️"
minus = "➖"
plus = "➕"
enable_sticker = "❌ Стикер в приветствии"
disable_sticker = "✅ Стикер в приветствии"

toggle_email = "Email при заказе"
toggle_phone_number = "Номер телефона при заказе"
enable_delivery = "❌ Доставка"
disable_delivery = "✅ Доставка"
toggle_captcha = "CAPTCHA при заказе"
enable_debug = "❌ Режим отладки"

input_email = f"Введите email {or_press_back}"
input_phone = f"Пожалуйста, введите ваш номер телефона для доставки.\nНапример: +79991234567 или 89991234567\n\n{or_press_back}"
input_address = f"Пожалуйста, введите ваш полный адрес для доставки.\n<b>Пример:</b> г. Москва, ул. Пушкина, д. 10, кв. 5\n\n{or_press_back}"
input_captcha = f"Введите CAPTCHA {or_press_back}"
input_captcha_error = "Неверный CAPTCHA"
input_email_error = "Неверный email"
input_phone_error = "Неверный формат. Пожалуйста, введите номер в формате +7... или 8..."
input_comment = "Вы можете оставить комментарий к заказу или просто отправить любое сообщение (например, точку '.'), чтобы пропустить этот шаг."

input_full_name = "Пожалуйста, введите ваше ФИО (Фамилия Имя Отчество), например: Иванов Иван Иванович"
confirm_order_text = """
Пожалуйста, проверьте и подтвердите ваш заказ:

<b>ФИО:</b> {full_name}
<b>Телефон:</b> {phone_number}
<b>Адрес:</b> {address}
<b>Комментарий:</b> {comment}

<b>Товары в корзине:</b>
{items_text}

<b>Итого к оплате:</b> {total_price}{currency_symbol}
"""
input_delivery_price = f"💰 Введите стоимость доставки {or_press_back}"
change_delivery_price = "💰 Изменить стоимость доставки"
disable_debug = "✅ Режим отладки"
confirm_and_pay = "✅ Подтвердить и оплатить"
admin_orders_menu_title = "🗂️ Управление заказами"
view_order = "📂 Посмотреть заказ"
order_processing = "⏳ Обрабатываем ваш заказ, пожалуйста, подождите..."
order_success_message = """
✅ Заказ #{order_id} успешно создан!

Спасибо за покупку! Мы уже начали собирать ваш заказ.

<b>Ваш трек-номер для отслеживания (SDEK):</b>
<code>{tracking_number}</code>

Вы можете отслеживать статус в разделе "Мои заказы".
"""
# Add these to src/localization/ru.py

your_orders = "📋 Ваши заказы"
no_orders_yet = "У вас пока нет заказов."

# Statuses for displaying in the list
order_status_new = "Новый"
order_status_processing = "В обработке"
order_status_shipped = "Отправлен"
order_status_delivered = "Доставлен"
order_status_cancelled = "Отменен"
order_status_unknown = "Неизвестный статус"
# Add these to src/localization/ru.py

order_details_title = "📄 Детали заказа #{order_id}"

no_tracking_number = "пока не присвоен"
request_cancellation = "❌ Запросить отмену"
cancellation_not_possible = "Отмена невозможна, так как заказ уже обрабатывается или отправлен."
cancellation_requested_success = "✅ Ваш запрос на отмену заказа #{order_id} отправлен на рассмотрение."
order_status_cancellation_requested = "Ожидает отмены" # New status text
# Add these to src/localization/ru.py

confirm_cancellation_prompt = "Вы уверены, что хотите запросить отмену заказа #{order_id}?"
yes_im_sure = "Да, я уверен"
no_go_back = "Нет, вернуться"
track_order_button = "Отследить заказ"
catalogue = "🛍️ Все товары"  # Change this text
all_items_title = "✨ Все наши товары" # Add this new title
all_items_caption = "Выберите интересующий вас товар из списка ниже:"

item_details_button = "🔎 Подробнее о товаре"
item_details_text = """
<b>Состав:</b>
{composition}

<b>Способ применения:</b>
{usage}
"""
item_details_not_specified = "Не указано"
item_added_to_cart = "✅ Товар добавлен в корзину"
filter_new_orders = " новые"
filter_cancellation_requests = " запросы на отмену"
input_tracking_number = "Введите трек-номер для этого заказа:"
order_marked_as_shipped_admin = "✅ Заказ #{order_id} отмечен как отправленный. Трек-номер: {tracking_number}"
user_notification_shipped = """
🚚 Ваш заказ #{order_id} был отправлен!

Вы можете отследить его с помощью трек-номера: <code>{tracking_number}</code>
"""
date_cancelled_text = "Дата отмены:"
order_details_text = """
<b>Статус:</b> {status_text}
<b>Дата:</b> {date_created}
{status_specific_info}  # <-- A placeholder for our dynamic text

<b>Товары:</b>
{items_text}
# ... etc
"""
confirm_delete_category_cascade = (
    "‼️ <b>ВНИМАНИЕ: НЕОБРАТИМОЕ ДЕЙСТВИЕ</b> ‼️\n\n"
    "Вы собираетесь удалить категорию «<b>{category_name}</b>».\n"
    "Это действие также навсегда удалит:\n"
    "    - <b>{sub_category_count}</b> вложенных подкатегорий\n"
    "    - <b>{item_count}</b> товаров в этой категории и всех подкатегориях\n\n"
    "Вы уверены, что хотите продолжить?"
)
category_deleted_successfully = "✅ Категория «{category_name}» и все ее содержимое были успешно удалены."