# src/callbacks/user/item_details.py

import asyncio
from aiogram import types
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # 1. Get the item object
    item = models.items.Item(data["iid"])

    # 2. Fetch all necessary data, including the new details_image_id
    (
        composition,
        usage,
        details_image_id,
    ) = await asyncio.gather(
        item.composition,
        item.usage,
        item.details_image_id,
    )

    # 3. Format the text (the caption for our photo)
    details_text = constants.language.item_details_text.format(
        composition=composition if composition else constants.language.item_details_not_specified,
        usage=usage if usage else constants.language.item_details_not_specified
    )

    # 4. Create the "Back" button, passing all breadcrumbs
    photo_id_breadcrumb = f',"pmid":{data["pmid"]}' if "pmid" in data else ""
    back_callback = f'{{"r":"user","iid":{item.id}{photo_id_breadcrumb}}}item'
    
    markup = markups.create([
        (constants.language.back, back_callback)
    ])

    # 5. Delete the previous message (the main item view) for a clean UI
    await callback_query.message.delete()

    if details_image_id:
        try:
            # Try to send the photo using the ID from the database
            await callback_query.message.answer_photo(
                photo=details_image_id,
                caption=details_text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        except exceptions.WrongFileIdentifier:
            # If the ID is invalid, log the error and fall back to a text message
            print(f"WARNING: Invalid file_id '{details_image_id}' for item id={item.id}")
            await callback_query.message.answer(
                text=details_text,
                reply_markup=markup,
                parse_mode="HTML"
            )
    else:
        # If no details image ID is specified at all, send a text message
        await callback_query.message.answer(
            text=details_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    # --- END OF FIX ---