import importlib
from aiogram import types
import models
import constants
from markups import markups
import asyncio


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
        # it means we need to delete that old menu's photo.
    if "pmid" in data:
        try:
            await callback_query.bot.delete_message(
                chat_id=user.id,
                message_id=data["pmid"]
            )
        except Exception:
            # Failsafe in case the message is already gone.
            pass
        
    item = models.items.Item(data["iid"])
    item_text, category, image_id, cart_dict = await asyncio.gather(
        item.format_text(constants.config["info"]["item_template"], constants.config["settings"]["currency"]),
        item.category,
        item.image_id,
        user.cart.items.dict,
    )

    def cart_callback(state: int):
        return f'{{"r":"user","iid":{item.id},"s":{state},"d":"item"}}changeCart'


    item_id = str(item.id)

    if item_id in cart_dict:
        cart_buttons = (
            (constants.language.minus, cart_callback(0)),
            (cart_dict[item_id], f'None'),
            (constants.language.plus, cart_callback(1)),
        )
    else:
        cart_buttons = (constants.language.add_to_cart, cart_callback(1))

    del_data = ',"del":"1"'
    # By default, the back button goes to the 'all_items' menu now
    back_callback_destination = "all_items"
    
    # If a specific redirect is provided (e.g., from the cart), use that
    if "rd" in data:
        back_callback_destination = data["rd"]

    # Check if a photo message ID was passed from the previous menu
    photo_id_breadcrumb = f',"pmid":{data["pmid"]}' if "pmid" in data else ""

    back_button = (
        constants.language.back,
        # Construct the final callback with all necessary data
        f'{{"r":"user"{photo_id_breadcrumb}}}{back_callback_destination}'
    )

    markup = markups.create([
        cart_buttons,
        [back_button] # Wrap in a list to ensure it's a single row
    ])

    if image_id:
        await callback_query.message.delete()
        return await callback_query.message.answer_photo(
            photo=image_id,
            caption=item_text,
            reply_markup=markup
        )
    return await callback_query.message.edit_text(
        text=item_text,
        reply_markup=markup
    )

