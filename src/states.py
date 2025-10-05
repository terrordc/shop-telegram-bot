from aiogram.dispatcher.filters.state import State, StatesGroup

# class AddCategory(StatesGroup):
#     name = State()
#     parent_category = State()

# class EditCategory(StatesGroup):
#     category_id = State()
#     main = State()
#     name = State()
#     parent_category = State()
#     delete = State()

class AddItem(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image_id = State()
    confirmation = State()

class EditItem(StatesGroup):
    item_id = State()
    main = State()
    name = State()
    description = State()
    category = State()
    price = State()
    image_id = State()
    delete = State()
    composition = State()
    usage = State()
    details_image_id = State()

class Language(StatesGroup):
    language = State()

class Greeting(StatesGroup):
    greeting = State()

class DeliveryPrice(StatesGroup):
    delivery_price = State()

class Notification(StatesGroup):
    notification = State()
    confirmation = State()

class UserProfile(StatesGroup):
    id = State()

class AdminOrder(StatesGroup):
    waiting_for_tracking_number = State()
    
class Order(StatesGroup):
    full_name = State()
    email = State()
    phone_number = State()
    address = State()
    comment = State()
    captcha = State()
    confirmation = State()

class LeaveReview(StatesGroup):
    waiting_for_input = State()      # The initial state where user sends order ID or review text
    waiting_for_text = State() 
    waiting_for_rating = State()     # The state where user sends the rating