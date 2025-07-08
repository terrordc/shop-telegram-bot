# utils/sdek_api.py

import asyncio
import random
import string

async def create_shipment(order_details: dict) -> str:
    """
    Simulates sending order details to the SDEK API and receiving a tracking number.
    In a real application, this would use aiohttp or httpx to make a real API call.
    """
    print("--- SDEK API SIMULATION ---")
    print(f"Sending order details to SDEK: {order_details}")

    # Simulate network latency
    await asyncio.sleep(2)

    # Generate a fake tracking number
    tracking_number = ''.join(random.choices(string.digits, k=10))
    print(f"Received tracking number from SDEK: {tracking_number}")
    print("--------------------------")

    return tracking_number