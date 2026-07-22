"""
Keyboard layouts for KRD Telegram Shopping Bot
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from database import db


# ============= MAIN MENU KEYBOARDS =============

def get_main_menu() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="🛍️ متجر", callback_data="shop")],
        [InlineKeyboardButton(text="🛒 سلتي", callback_data="cart"), 
         InlineKeyboardButton(text="📦 طلباتي", callback_data="orders")],
        [InlineKeyboardButton(text="👤 حسابي", callback_data="account"),
         InlineKeyboardButton(text="ℹ️ عن المتجر", callback_data="about")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_button() -> InlineKeyboardMarkup:
    """Get back button"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ رجوع", callback_data="main_menu")
    ]])


def get_back_and_home_buttons() -> InlineKeyboardMarkup:
    """Get back and home buttons"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ رجوع", callback_data="shop"),
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")
    ]])


# ============= SHOP KEYBOARDS =============

def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Get categories keyboard"""
    categories = db.get_all_categories()
    buttons = []
    
    for cat in categories:
        btn_text = f"{cat['emoji']} {cat['name']}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"category_{cat['category_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """Get products keyboard for a category"""
    products = db.get_products_by_category(category_id)
    buttons = []
    
    for product in products:
        btn_text = f"{product['name']} - ${product['price']:.2f}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"product_{product['product_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ الفئات", callback_data="shop")])
    buttons.append([InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_detail_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """Get product detail keyboard"""
    buttons = [
        [InlineKeyboardButton(text="➕ أضف للسلة", callback_data=f"add_to_cart_{product_id}")],
        [InlineKeyboardButton(text="◀️ رجوع", callback_data="shop"),
         InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quantity_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """Get quantity selector keyboard"""
    buttons = [
        [InlineKeyboardButton(text="1", callback_data=f"qty_1_{product_id}"),
         InlineKeyboardButton(text="2", callback_data=f"qty_2_{product_id}"),
         InlineKeyboardButton(text="3", callback_data=f"qty_3_{product_id}")],
        [InlineKeyboardButton(text="4", callback_data=f"qty_4_{product_id}"),
         InlineKeyboardButton(text="5", callback_data=f"qty_5_{product_id}"),
         InlineKeyboardButton(text="10", callback_data=f"qty_10_{product_id}")],
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="shop")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= CART KEYBOARDS =============

def get_cart_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get cart keyboard"""
    cart = db.get_cart(user_id)
    
    if not cart:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")
        ]])
    
    buttons = []
    for item in cart:
        btn_text = f"🗑️ حذف - {item['name']}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"remove_from_cart_{item['product_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="✅ تم الطلب", callback_data="checkout")])
    buttons.append([InlineKeyboardButton(text="🛍️ متابعة التسوق", callback_data="shop"),
                    InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_empty_cart_keyboard() -> InlineKeyboardMarkup:
    """Get empty cart keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🛍️ ابدأ التسوق", callback_data="shop"),
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")
    ]])


# ============= ORDER KEYBOARDS =============

def get_checkout_keyboard() -> InlineKeyboardMarkup:
    """Get checkout keyboard"""
    buttons = [
        [InlineKeyboardButton(text="✅ تأكيد الطلب", callback_data="confirm_order")],
        [InlineKeyboardButton(text="◀️ العودة للسلة", callback_data="cart"),
         InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_orders_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get user orders keyboard"""
    orders = db.get_user_orders(user_id)
    buttons = []
    
    for order in orders:
        btn_text = f"طلب #{order['order_id']} - {order['status']}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"order_{order['order_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_order_detail_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Get order detail keyboard"""
    buttons = [
        [InlineKeyboardButton(text="◀️ الطلبات", callback_data="orders"),
         InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============= ACCOUNT KEYBOARDS =============

def get_account_keyboard() -> InlineKeyboardMarkup:
    """Get account menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📱 رقم الهاتف", callback_data="set_phone")],
        [InlineKeyboardButton(text="📍 العنوان", callback_data="set_address")],
        [InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Get phone request keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 شارك رقمي", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Get cancel keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ إلغاء")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# ============= ADMIN KEYBOARDS =============

def get_admin_menu() -> InlineKeyboardMarkup:
    """Get admin menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📦 الفئات", callback_data="admin_categories")],
        [InlineKeyboardButton(text="🛍️ المنتجات", callback_data="admin_products")],
        [InlineKeyboardButton(text="📋 الطلبات", callback_data="admin_orders")],
        [InlineKeyboardButton(text="👥 المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_categories_keyboard() -> InlineKeyboardMarkup:
    """Get admin categories keyboard"""
    categories = db.get_all_categories()
    buttons = []
    
    for cat in categories:
        btn_text = f"📝 {cat['name']}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"admin_edit_cat_{cat['category_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="➕ إضافة فئة", callback_data="admin_add_category")])
    buttons.append([InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_products_keyboard() -> InlineKeyboardMarkup:
    """Get admin products keyboard"""
    products = db.get_all_products()
    buttons = []
    
    for product in products:
        btn_text = f"📝 {product['name']}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"admin_edit_prod_{product['product_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="➕ إضافة منتج", callback_data="admin_add_product")])
    buttons.append([InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_edit_category_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """Get admin edit category keyboard"""
    buttons = [
        [InlineKeyboardButton(text="✏️ تعديل", callback_data=f"admin_edit_cat_form_{category_id}")],
        [InlineKeyboardButton(text="🗑️ حذف", callback_data=f"admin_delete_cat_{category_id}")],
        [InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_categories")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_edit_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """Get admin edit product keyboard"""
    buttons = [
        [InlineKeyboardButton(text="✏️ تعديل", callback_data=f"admin_edit_prod_form_{product_id}")],
        [InlineKeyboardButton(text="🗑️ حذف", callback_data=f"admin_delete_prod_{product_id}")],
        [InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_products")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_orders_keyboard() -> InlineKeyboardMarkup:
    """Get admin orders keyboard"""
    orders = db.get_all_orders()
    buttons = []
    
    for order in orders:
        btn_text = f"طلب #{order['order_id']} - {order['status']}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"admin_order_{order['order_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Get admin order actions keyboard"""
    order = db.get_order(order_id)
    buttons = []
    
    if order['status'] != 'completed':
        buttons.append([InlineKeyboardButton(text="✅ تم التوصيل", callback_data=f"admin_complete_order_{order_id}")])
    
    if order['status'] != 'cancelled':
        buttons.append([InlineKeyboardButton(text="❌ إلغاء", callback_data=f"admin_cancel_order_{order_id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_orders")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    """Get admin users keyboard"""
    users = db.get_all_users()
    buttons = []
    
    for user in users:
        btn_text = f"👤 {user['first_name'] or 'User'} ({user['user_id']})"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"admin_user_{user['user_id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
