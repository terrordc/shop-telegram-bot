# src/callbacks/states/EditItem_main.py

import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
import importlib
# --- THIS IS THE FIX ---
# We import the INSTANCE named 'markups' from the 'markups' module.
from markups import markups
import states

# --- Helper functions to draw the menus ---
async def _send_main_menu(message: types.Message, item: models.items.Item):
    item_image, text, is_hidden = await asyncio.gather(
        item.image_id, item.format_text(constants.config["info"]["item_template"], constants.config["settings"]["currency_symbol"]), item.is_hidden
    )
    markup = markups.create([
        (constants.language.edit_name, f'{{"r":"admin","iid":{item.id}}}editItemName'),
        (constants.language.edit_description, f'{{"r":"admin","iid":{item.id}}}editItemDescription'),
        (constants.language.edit_price, f'{{"r":"admin","iid":{item.id}}}editItemPrice'),
        (constants.language.edit_image, f'{{"r":"admin","iid":{item.id}}}editItemImage'),
        (constants.language.edit_details, f'{{"r":"admin","iid":{item.id}}}editDetails'),
        (constants.language.show if is_hidden else constants.language.hide, f'{{"r":"admin","iid":{item.id}}}toggleIsHidden'),
        (constants.language.delete, f'{{"r":"admin","iid":{item.id}}}deleteItem'),
        (constants.language.back, f'{{"r":"admin","d":"all_items"}}cancel')
    ])
    if item_image: await message.answer_photo(photo=item_image, caption=text, reply_markup=markup)
    else: await message.answer(text=text, reply_markup=markup)

async def _send_details_menu(message: types.Message, item: models.items.Item):
    composition, usage, item_image = await asyncio.gather(item.composition, item.usage, item.image_id)
    text = constants.language.edit_details_menu.format(composition=composition or "Не задано", usage=usage or "Не задано")
    markup = markups.create([
        (constants.language.edit_composition, f'{{"r":"admin","iid":{item.id}}}editComposition'),
        (constants.language.edit_usage, f'{{"r":"admin","iid":{item.id}}}editUsage'),
        (constants.language.edit_details_image, f'{{"r":"admin","iid":{item.id}}}editDetailsImage'),
        (constants.language.back, f'{{"r":"admin","iid":{item.id}}}editItem')
    ])
    if item_image: await message.answer_photo(photo=item_image, caption=text, reply_markup=markup, parse_mode="HTML")
    else: await message.answer(text, reply_markup=markup, parse_mode="HTML")


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext) -> None:
    call = callback_query.data[callback_query.data.index("}") + 1:]
    
    # --- CANCEL LOGIC IS NOW HANDLED HERE ---
    if call == "cancel":
        await state.finish()
        destination = data.get("d")
        if destination: # If it's a back button with a destination
            await callback_query.message.delete()
            # We need to execute the destination file
            execute_args = (callback_query, user, data, None, state)
            await importlib.import_module(f"callbacks.{data['r']}.{destination}").execute(*execute_args)
        else: # A generic cancel
             await callback_query.message.edit_text(constants.language.state_cancelled)
        return

    # --- MAIN LOGIC FOR ALL OTHER BUTTONS ---
    state_data = await state.get_data()
    item_id = state_data.get("item_id")
    if not item_id: return await state.finish() # Safety exit

    item = models.items.Item(item_id)
    
    # Delete the current menu before showing the next one
    await callback_query.message.delete()
    
    match call:
        case "editItem":
            await _send_main_menu(callback_query.message, item)
        case "editDetails":
            await _send_details_menu(callback_query.message, item)
        case "toggleIsHidden":
            await item.set_is_hidden(not await item.is_hidden)
            await _send_main_menu(callback_query.message, item) # Redisplay menu with updated button
        case _:
            # All other buttons lead to a new state with a prompt
            text_to_send = ""
            state_to_set = None
            back_dest = "editItem"

            if call == "editItemName": state_to_set, text_to_send = states.EditItem.name, constants.language.input_item_name
            elif call == "editItemDescription": state_to_set, text_to_send = states.EditItem.description, constants.language.input_item_description
            elif call == "editItemPrice": state_to_set, text_to_send = states.EditItem.price, constants.language.input_item_price
            elif call == "editItemImage": state_to_set, text_to_send = states.EditItem.image_id, constants.language.send_item_image
            elif call == "editComposition": state_to_set, text_to_send, back_dest = states.EditItem.composition, constants.language.input_item_composition, "editDetails"
            elif call == "editUsage": state_to_set, text_to_send, back_dest = states.EditItem.usage, constants.language.input_item_usage, "editDetails"
            elif call == "editDetailsImage": state_to_set, text_to_send, back_dest = states.EditItem.details_image_id, constants.language.send_item_details_image, "editDetails"
            # Add 'deleteItem' logic here if needed

            if state_to_set:
                await state_to_set.set()
                markup = markups.create([(constants.language.back, f'{{"r":"admin","iid":{item.id},"d":"{back_dest}"}}cancel')])
                prompt_message = await callback_query.message.answer(text_to_send, reply_markup=markup)
                await state.update_data(prompt_message_id=prompt_message.message_id)