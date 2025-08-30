import os
import json
from typing import Any

filename = "config.json"
class Config:
    def __repr__(self):
        return self.__data 

    def __iter__(self):
        return self.__data

    def __getitem__(self, item):
        return self.__data[item]

    def __str__(self) -> str:
        return self.__raw 

    @property
    def __raw(self) -> str:
        with open(filename, "r") as f:
            return f.read()

    @property
    def __data(self):
       return json.loads(self.__raw) 

    def set(self, param: str | tuple[str, str], value: Any) -> None:
        modified_data = self.__data

        if isinstance(param, tuple):
            modified_data[param[0]][param[1]] = value
        else:
            modified_data[param] = value

        backup_filename = f"{filename}.bak"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
        with open(backup_filename, "w") as f:
            json.dump(modified_data, f, indent=2)        
        os.remove(filename)
        with open(filename, "w") as f:
            json.dump(modified_data, f, indent=2)

    def init(self) -> None:
        with open(filename, "w") as f:
            data = {
                "settings": {
                    "language": "ru",
                    "currency": "RUB",
                    "currency_symbol": "₽",
                    "debug": False,
                },
                "delivery": {
                    "price": 0,
                    "enabled": True,
                },
                "checkout": {
                    "full_name": True,
                    "address": True,
                    "phone": True,
                    "email": False,
                    "captcha": False,
                },
                "payment_methods": {
                    "cash": {
                        "title": "Наличными",
                        "enabled": False,
                    },
                    "manager": {
                        "title": "Оплата после связи с менеджером",
                        "enabled": False,
                    },
                    "telegram_api": {
                        "title": "Оплата через Telegram",
                        "enabled": True,
                    },
                  },
                "info": {
                    "greeting": "Приветствуем в нашем магазине!",
                    "contacts": "Телефон: +7 (999) 999-99-99\nАдрес: г. Москва, ул. Ленина, д. 1",
                    "refund_policy": "Политика возврата",
                    "faq_url": "https://telegra.ph/CHasto-zadavaemye-voprosy-07-09-3",
                    "support_username": "buttermilkjesuss",
                    "sdek_manager_telegram_id": 347242473,
                    "item_template": "<b>%n</b>\n\nЦена: %p\n\n%d",
                },
            }
            json.dump(data, f, indent=2)
    
config = Config()


