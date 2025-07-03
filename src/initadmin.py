
import os
import asyncio  # 1. Import the asyncio library
from dotenv import load_dotenv

# 2. Import ALL the functions and classes you need
from models.users import get_user_by_id, User # Assuming set_admin is a method on the User now

# 3. Wrap your logic in an async function so you can use 'await'
async def main():
    """The main entry point for our admin initialization script."""
    print("Loading environment variables...")
    load_dotenv()

    admin_id_str = os.getenv("ADMIN_ID")
    if not admin_id_str:
        print("Error: ADMIN_ID not found in .env file.")
        return

    try:
        # The ID from .env is a string, but the function needs an integer
        admin_id = int(admin_id_str)
    except ValueError:
        print(f"Error: ADMIN_ID ('{admin_id_str}') is not a valid integer.")
        return

    print(f"Attempting to find user with ID: {admin_id}")
    # 4. Use 'await' to call your async database function
    user = await get_user_by_id(admin_id)

    if user:
        print(f"Found user '{user.name}'. Promoting to admin...")
        # Let's assume set_admin is now a method on the User object, which is good practice.
        # This is cleaner than a separate set_admin(user) function.
        await user.set_admin() # 5. Call the set_admin method on the user object
    else:
        print(f"Error: User with ID {admin_id} was not found in the database.")


# 6. This special block runs the 'main' async function
#    This is the standard way to run an async script from the top level.
if __name__ == "__main__":
    # In your init.py you should have a single asyncio.run(main())
    # if initadmin is the entry point.
    # Since you import it, you just need to call the function from your main loop.
    # For now, let's assume this script is run directly.
    asyncio.run(main())