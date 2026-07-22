"""
Admin handlers for KRD Telegram Shopping Bot
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
from database import db
from keyboards.keyboards import *

router = Router()


class AdminStates(StatesGroup):
    add_category = State()
    add_product = State()
    edit_product_name = State()
    edit_product_price = State()
    edit_product_stock = State()


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    """Admin panel main menu"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن للوصول إلى لوحة التحكم", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 <b>لوحة التحكم الإدارية</b>\n\n"
        "اختر ما تريد إدارته:",
        reply_markup=get_admin_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


# ============= CATEGORY MANAGEMENT =============

@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery):
    """Admin categories management"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📦 <b>إدارة الفئات</b>",
        reply_markup=get_admin_categories_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_category")
async def admin_add_category(callback: CallbackQuery, state: FSMContext):
    """Add new category"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    await state.set_state(AdminStates.add_category)
    await callback.message.edit_text(
        "📝 أرسل اسم الفئة الجديدة:\n(مثال: إلكترونيات)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ إلغاء", callback_data="admin_categories")
        ]])
    )
    await callback.answer()


@router.message(AdminStates.add_category)
async def add_category_name(message: Message, state: FSMContext):
    """Process category name"""
    category_name = message.text.strip()
    
    if db.add_category(category_name, emoji="📦"):
        await message.reply(
            f"✅ تم إضافة الفئة '{category_name}' بنجاح!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="رجوع", callback_data="admin_categories")
            ]])
        )
    else:
        await message.reply(
            "❌ خطأ في إضافة الفئة. هل الفئة موجودة بالفعل؟",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="إعادة محاولة", callback_data="admin_add_category")
            ]])
        )
    
    await state.clear()


@router.callback_query(F.data.startswith("admin_delete_cat_"))
async def admin_delete_category(callback: CallbackQuery):
    """Delete category"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[-1])
    
    if db.delete_category(category_id):
        await callback.answer("✅ تم حذف الفئة بنجاح", show_alert=True)
        await callback.message.edit_text(
            "📦 <b>إدارة الفئات</b>",
            reply_markup=get_admin_categories_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ خطأ في حذف الفئة", show_alert=True)


# ============= PRODUCT MANAGEMENT =============

@router.callback_query(F.data == "admin_products")
async def admin_products(callback: CallbackQuery):
    """Admin products management"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🛍️ <b>إدارة المنتجات</b>",
        reply_markup=get_admin_products_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_product")
async def admin_add_product(callback: CallbackQuery, state: FSMContext):
    """Add new product"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    categories = db.get_all_categories()
    
    if not categories:
        await callback.answer("❌ يجب إضافة فئة أولاً", show_alert=True)
        return
    
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"admin_select_cat_{cat['category_id']}"
        )])
    
    await callback.message.edit_text(
        "📝 اختر الفئة للمنتج الجديد:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_select_cat_"))
async def admin_select_category_for_product(callback: CallbackQuery, state: FSMContext):
    """Select category for new product"""
    category_id = int(callback.data.split("_")[-1])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.add_product)
    
    await callback.message.edit_text(
        "📝 أرسل اسم المنتج:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ إلغاء", callback_data="admin_products")
        ]])
    )
    await callback.answer()


@router.message(AdminStates.add_product)
async def add_product_name(message: Message, state: FSMContext):
    """Process product name"""
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStates.edit_product_price)
    await message.reply("💰 الآن أرسل سعر المنتج:")


@router.message(AdminStates.edit_product_price)
async def add_product_price(message: Message, state: FSMContext):
    """Process product price"""
    try:
        price = float(message.text.strip())
        await state.update_data(price=price)
        await state.set_state(AdminStates.edit_product_stock)
        await message.reply("📦 الآن أرسل كمية المخزون:")
    except ValueError:
        await message.reply("❌ أدخل سعراً صحيحاً")


@router.message(AdminStates.edit_product_stock)
async def add_product_stock(message: Message, state: FSMContext):
    """Process product stock"""
    try:
        stock = int(message.text.strip())
        data = await state.get_data()
        
        if db.add_product(
            category_id=data['category_id'],
            name=data['name'],
            description="",
            price=data['price'],
            stock=stock
        ):
            await message.reply(
                f"✅ تم إضافة المنتج '{data['name']}' بنجاح!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="رجوع", callback_data="admin_products")
                ]])
            )
        else:
            await message.reply("❌ خطأ في إضافة المنتج")
        
        await state.clear()
    except ValueError:
        await message.reply("❌ أدخل كمية صحيحة")


@router.callback_query(F.data.startswith("admin_delete_prod_"))
async def admin_delete_product(callback: CallbackQuery):
    """Delete product"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[-1])
    
    if db.delete_product(product_id):
        await callback.answer("✅ تم حذف المنتج بنجاح", show_alert=True)
        await callback.message.edit_text(
            "🛍️ <b>إدارة المنتجات</b>",
            reply_markup=get_admin_products_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ خطأ في حذف المنتج", show_alert=True)


# ============= ORDERS MANAGEMENT =============

@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    """Admin orders management"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📋 <b>إدارة الطلبات</b>",
        reply_markup=get_admin_orders_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_order_"))
async def admin_order_detail(callback: CallbackQuery):
    """Show order details"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    order = db.get_order(order_id)
    order_items = db.get_order_items(order_id)
    
    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return
    
    user = db.get_user(order['user_id'])
    text = f"📦 <b>تفاصيل الطلب #{order['order_id']}</b>\n\n"
    text += f"<b>المستخدم:</b> {user['first_name'] or 'Unknown'}\n"
    text += f"<b>الحالة:</b> {order['status']}\n"
    text += f"<b>السعر الإجمالي:</b> ${order['total_price']:.2f}\n\n"
    text += "<b>المنتجات:</b>\n"
    
    for item in order_items:
        text += f"• {item['name']} x{item['quantity']} = ${item['price'] * item['quantity']:.2f}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_order_actions_keyboard(order_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_complete_order_"))
async def admin_complete_order(callback: CallbackQuery):
    """Complete order"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    
    if db.update_order_status(order_id, "completed"):
        await callback.answer("✅ تم تحديث حالة الطلب", show_alert=True)
        await callback.message.edit_text(
            "📋 <b>إدارة الطلبات</b>",
            reply_markup=get_admin_orders_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ خطأ في تحديث الطلب", show_alert=True)


@router.callback_query(F.data.startswith("admin_cancel_order_"))
async def admin_cancel_order(callback: CallbackQuery):
    """Cancel order"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    
    if db.update_order_status(order_id, "cancelled"):
        await callback.answer("✅ تم إلغاء الطلب", show_alert=True)
        await callback.message.edit_text(
            "📋 <b>إدارة الطلبات</b>",
            reply_markup=get_admin_orders_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ خطأ في إلغاء الطلب", show_alert=True)


# ============= USERS MANAGEMENT =============

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Admin users management"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 <b>إدارة المستخدمين</b>",
        reply_markup=get_admin_users_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_detail(callback: CallbackQuery):
    """Show user details"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ أنت لا تملك الإذن", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[-1])
    user = db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ المستخدم غير موجود", show_alert=True)
        return
    
    text = f"👤 <b>تفاصيل المستخدم</b>\n\n"
    text += f"<b>الاسم:</b> {user['first_name']} {user['last_name'] or ''}\n"
    text += f"<b>اسم المستخدم:</b> {user['username'] or 'N/A'}\n"
    text += f"<b>الرقم:</b> {user['phone'] or 'لم يتم تعيينه'}\n"
    text += f"<b>العنوان:</b> {user['address'] or 'لم يتم تعيينه'}\n"
    text += f"<b>تاريخ الانضمام:</b> {user['created_at']}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="◀️ رجوع", callback_data="admin_users")
        ]]),
        parse_mode="HTML"
    )
    await callback.answer()
