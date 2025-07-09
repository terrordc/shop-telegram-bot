#!/bin/bash

# This script cleans up the project by:
# 1. Renaming files from camelCase to snake_case for consistency.
# 2. Archiving legacy and unused files (like the old category system and toggles)
#    into a _legacy_archive directory.
#
# It is designed to be run from the project's root directory.
#
# IMPORTANT: Before running, please commit your current changes to git!
# `git add . && git commit -m "Pre-cleanup state"`

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
ARCHIVE_DIR="_legacy_archive"

# --- Safety Check ---
if [ ! -d "src" ] || [ ! -d "src/callbacks" ]; then
    echo "Error: This script must be run from the project root directory."
    echo "Could not find 'src/callbacks'."
    exit 1
fi

echo "Starting project cleanup..."
echo "Legacy files will be moved to the '$ARCHIVE_DIR' directory."
echo "--------------------------------------------------------"


# --- 1. Renaming Files for Consistency (camelCase to snake_case) ---
echo "Step 1: Renaming files for PEP 8 consistency..."

# Use `git mv` if you are in a git repository to preserve history.
# If not, a simple `mv` will suffice. We check if `git` is available.
MV_CMD="mv"
if git rev-parse --git-dir > /dev/null 2>&1; then
  MV_CMD="git mv"
  echo "Git repository detected. Using 'git mv' for renaming."
fi

$MV_CMD src/callbacks/admin/adminPanel.py src/callbacks/admin/admin_panel.py
$MV_CMD src/callbacks/admin/deliveryPrice.py src/callbacks/admin/delivery_price.py
$MV_CMD src/callbacks/admin/editCategories.py src/callbacks/admin/edit_categories.py
$MV_CMD src/callbacks/admin/editCategory.py src/callbacks/admin/edit_category.py
$MV_CMD src/callbacks/admin/editItemsCategories.py src/callbacks/admin/edit_items_categories.py
$MV_CMD src/callbacks/admin/editItemsCategory.py src/callbacks/admin/edit_items_category.py
$MV_CMD src/callbacks/admin/editItem.py src/callbacks/admin/edit_item.py
$MV_CMD src/callbacks/user/changeCart.py src/callbacks/user/change_cart.py
$MV_CMD src/callbacks/user/clearCart.py src/callbacks/user/clear_cart.py
$MV_CMD src/callbacks/user/cycleDelivery.py src/callbacks/user/cycle_delivery.py
$MV_CMD src/callbacks/user/cyclePaymentMethod.py src/callbacks/user/cycle_payment_method.py
$MV_CMD src/callbacks/states/DeliveryPrice_delivery_price.py src/callbacks/states/delivery_price_state.py
$MV_CMD src/callbacks/states/EditItem_main.py src/callbacks/states/edit_item_main_state.py


# --- 2. Archiving Legacy and Unused Files ---
echo ""
echo "Step 2: Archiving legacy and unused files..."

# Create the archive directory structure
mkdir -p "$ARCHIVE_DIR/src/callbacks/admin"
mkdir -p "$ARCHIVE_DIR/src/callbacks/user"
mkdir -p "$ARCHIVE_DIR/src/callbacks/states"
mkdir -p "$ARCHIVE_DIR/src/models"

# --- Archive the old Category System ---
echo "Archiving old category management system..."
# Admin callbacks
mv src/callbacks/admin/addCategory.py "$ARCHIVE_DIR/src/callbacks/admin/"
mv src/callbacks/admin/categories.py "$ARCHIVE_DIR/src/callbacks/admin/"
mv src/callbacks/admin/edit_categories.py "$ARCHIVE_DIR/src/callbacks/admin/" # Note: uses renamed file
mv src/callbacks/admin/edit_category.py "$ARCHIVE_DIR/src/callbacks/admin/"   # Note: uses renamed file
mv src/callbacks/admin/edit_items_categories.py "$ARCHIVE_DIR/src/callbacks/admin/" # Note: uses renamed file
mv src/callbacks/admin/edit_items_category.py "$ARCHIVE_DIR/src/callbacks/admin/" # Note: uses renamed file

# User callbacks
mv src/callbacks/user/catalogue.py "$ARCHIVE_DIR/src/callbacks/user/"
mv src/callbacks/user/category.py "$ARCHIVE_DIR/src/callbacks/user/"

# FSM States for Categories
mv src/callbacks/states/AddCategory_*.py "$ARCHIVE_DIR/src/callbacks/states/"
mv src/callbacks/states/EditCategory_*.py "$ARCHIVE_DIR/src/callbacks/states/"

# Category Model
mv src/models/categories.py "$ARCHIVE_DIR/src/models/"

# --- Archive Unused Toggles ---
echo "Archiving unused admin toggle settings..."
mv src/callbacks/admin/toggle_captcha.py "$ARCHIVE_DIR/src/callbacks/admin/"
mv src/callbacks/admin/toggle_email.py "$ARCHIVE_DIR/src/callbacks/admin/"
mv src/callbacks/admin/toggle_phone_number.py "$ARCHIVE_DIR/src/callbacks/admin/"
mv src/callbacks/admin/toggle_payment_method.py "$ARCHIVE_DIR/src/callbacks/admin/"

# --- Archive other miscellaneous legacy files ---
echo "Archiving other legacy files..."
mv src/callbacks/user/profile.py "$ARCHIVE_DIR/src/callbacks/user/" # Was likely replaced by "My Orders"
mv src/callbacks/user/refund.py "$ARCHIVE_DIR/src/callbacks/user/" # Not implemented, better to remove for now

echo ""
echo "--------------------------------------------------------"
echo "✅ Cleanup complete!"
echo "Files have been renamed and legacy code has been archived in the '$ARCHIVE_DIR' directory."
echo "Please test the bot to ensure all functionality is intact."
echo "After confirming, you can delete the '$ARCHIVE_DIR' directory."
if [ "$MV_CMD" == "git mv" ]; then
  echo "Run 'git status' to see the changes staged for commit."
fi