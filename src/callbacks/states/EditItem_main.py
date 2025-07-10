# src/callbacks/states/EditItem_main.py

import asyncio
import importlib
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

# --- Helper function 1: To display the main edit menu ---
async def _display_main_menu(callback_query: types.CallbackQuery, item: models.items.Item):
    item_image, text, is_hidden = await asyncio.gather(
        item.image_id,
        item.format_text(constants.config["info"]["item_template"], constants.config["settings"]["currency_symbol"]),
        item.is_hidden
    )

    markup_buttons = [
        (constants.language.edit_name, f'{{"r":"admin","iid":{item.id}}}editItemName'),
        (constants.language.edit_description, f'{{"r":"admin","iid":{item.id}}}editItemDescription'),
        (constants.language.edit_price, f'{{"r":"admin","iid":{item.id}}}editItemPrice'),
        (constants.language.edit_image, f'{{"r":"admin","iid":{item.id}}}editItemImage'),
        (constants.language.edit_details, f'{{"r":"admin","iid":{item.id}}}editDetails'),
        (constants.language.show if is_hidden else constants.language.hide, f'{{"r":"admin","iid":{item.id}}}toggleIsHidden'),
        (constants.language.delete, f'{{"r":"admin","iid":{item.id}}}deleteItem'),
        (constants.language.back, f'{{"r":"admin","d":"all_items"}}cancel')
    ]
    markup = markups.create(markup_buttons)

    # Smart editing: edit caption for photo messages, edit text for text messages
    if callback_query.message.photo:
        await callback_query.message.edit_caption(caption=text, reply_markup=markup)
    else:
        await callback_query.message.edit_text(text=text, reply_markup=markup)

# --- Helper function 2: To display the details sub-menu ---
async def _display_details_menu(callback_query: types.CallbackQuery, item: models.items.Item):
    composition, usage = await asyncio.gather(item.composition, item.usage)
    text = constants.language.edit_details_menu.format(
        composition=composition or "Не задано",
        usage=usage or "Не задано"
    )
    markup = markups.create([
        (constants.language.edit_composition, f'{{"r":"admin","iid":{item.id}}}editComposition'),
        (constants.language.edit_usage, f'{{"r":"admin","iid":{item.id}}}editUsage'),
        (constants.language.edit_details_image, f'{{"r":"admin","iid":{item.id}}}editDetailsImage'),
        (constants.language.back, f'{{"r":"admin","iid":{item.id}}}editItem')
    ])

    # Smart editing: same logic as above
    if callback_query.message.photo:
        await callback_query.message.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
    else:
        await callback_query.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    if message: return

    call = callback_query.data[callback_query.data.index("}")+1:]
    state_data = await state.get_data()
    item_id = state_data.get("item_id")
    if not item_id: return

    item = models.items.Item(item_id)
    text = constants.language.unknown_error
    is_prompt = False # Flag to check if we are sending a prompt

    match call:
        case "editItem":
            await _display_main_menu(callback_query, item)
            return
        case "editDetails":
            await _display_details_menu(callback_query, item)
            return
            
        case "editItemName":
            await callback_query.answer() # Send popup
            await states.EditItem.name.set()
            text = constants.language.input_item_name
            is_prompt = True
        case "editItemDescription":
            await callback_query.answer() # Send popup
            await states.EditItem.description.set()
            text = constants.language.input_item_description
            is_prompt = True
        case "editItemPrice":
            await callback_query.answer() # Send popup
            await states.EditItem.price.set()
            text = constants.language.input_item_price
            is_prompt = True
        case "editItemImage":
            await callback_query.answer() # Send popup
            await states.EditItem.image_id.set()
            text = constants.language.send_item_changed_images
            is_prompt = True
        case "editComposition":
            await callback_query.answer() # Send popup
            await states.EditItem.composition.set()
            text = constants.language.input_item_composition
            is_prompt = True
        case "editUsage":
            await callback_query.answer() # Send popup
            await states.EditItem.usage.set()
            text = constants.language.input_item_usage
            is_prompt = True
        case "editDetailsImage":
            await callback_query.answer() # Send popup
            await states.EditItem.details_image_id.set()
            text = constants.language.send_item_details_image
            is_prompt = True

        case "toggleIsHidden":
            await item.set_is_hidden(not await item.is_hidden)
            await _display_main_menu(callback_query, item)
            return

        case "deleteItem":
            await states.EditItem.delete.set()
            text = constants.language.confirm_delete_item
            is_prompt = True
        case _:
            return await callback_query.answer()

    # This part now only handles sending the text prompt for the next state
    markup = markups.create([(constants.language.back, f'{{"r":"admin","iid":{item.id},"d":"editItem"}}cancel')])
    
    # Send the prompt and save its ID to the state for later editing
    prompt_message = await callback_query.message.answer(text=text, reply_markup=markup)
    await state.update_data(prompt_message_id=prompt_message.message_id)