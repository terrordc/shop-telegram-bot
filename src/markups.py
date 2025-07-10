from aiogram import types
from constants import language


class Markups:
    # --- START OF REPLACEMENT ---

    
    def create(self, values: list) -> types.InlineKeyboardMarkup:
        """
        Creates an InlineKeyboardMarkup.
        Handles rows, single buttons, and URL buttons.
        Skips any values that are not properly formatted tuples.
        """
        markup = types.InlineKeyboardMarkup()
        for row_data in values:
            # Defensive check: if the row_data is not a list or a tuple, skip it.
            if not isinstance(row_data, (list, tuple)):
                continue

            # Ensure every item is treated as a row for consistency
            if isinstance(row_data, tuple) and len(row_data) == 2 and isinstance(row_data[1], (str, dict)):
                # This looks like a single button tuple, e.g., ("Text", "data")
                row_data = [row_data]
            
            buttons_in_row = []
            # This loop expects row_data to be an iterable of button tuples
            for button_tuple in row_data:
                # Defensive check: ensure the item is a 2-element tuple
                if not (isinstance(button_tuple, tuple) and len(button_tuple) == 2):
                    continue
                
                text, data = button_tuple
                if isinstance(data, dict):
                    # For URL buttons: ("Text", {"url": "..."})
                    buttons_in_row.append(types.InlineKeyboardButton(text=text, **data))
                else:
                    # For callback buttons: ("Text", "callback_data")
                    buttons_in_row.append(types.InlineKeyboardButton(text=text, callback_data=str(data)))
            
            # Only add a row if we actually created buttons for it
            if buttons_in_row:
                markup.row(*buttons_in_row)
        
        return markup
    # --- END OF REPLACEMENT ---

    @property
    def main(self) -> types.ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(language.all_items))
        markup.add(types.KeyboardButton(language.cart))
        markup.add(types.KeyboardButton(language.profile))
        markup.add(types.KeyboardButton(language.faq))
        markup.add(types.KeyboardButton(language.support))
        return markup

markups = Markups()

