"""
Main handlers for KRD Telegram Shopping Bot
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart
from database import db
from keyboards.keyboards import *

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Add user to database
    db.add_user(user_id, username, first_name, last_name)

    await message.answer(
        f"👋 مرحباً {first_name}!\n\n"
        f"🎉 أهلاً وسهلاً في متجر <b>KRD</b>\n"
        f"اختر من القائمة أدناه لبدء التسوق:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    """Show main menu"""
    await callback.message.edit_text(
        "🏠 <b>القائمة الرئيسية</b>\n\n"
        "اختر ما تريد:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "shop")
async def shop(callback: CallbackQuery):
    """Show shop with categories"""
    await callback.message.edit_text(
        "🛍️ <b>متجرنا</b>\n\n"
        "اختر الفئة:",
        reply_markup=get_categories_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery):
    """Show products in category"""
    category_id = int(callback.data.split("_")[1])
    category = db.get_category(category_id)
    
    if not category:
        await callback.answer("❌ الفئة غير موجودة", show_alert=True)
        return
    
    products = db.get_products_by_category(category_id)
    
    text = f"{category['emoji']} <b>{category['name']}</b>\n\n"
    
    if not products:
        text += "لا توجد منتجات في هذه الفئة"
    else:
        text += "اختر منتج:"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_products_keyboard(category_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery):
    """Show product details"""
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ المنتج غير موجود", show_alert=True)
        return
    
    text = f"🛍️ <b>{product['name']}</b>\n\n"
    text += f"💰 <b>السعر:</b> ${product['price']:.2f}\n"
    text += f"📦 <b>المخزون:</b> {product['stock']} وحدة\n"
    
    if product['description']:
        text += f"\n📝 <b>الوصف:</b>\n{product['description']}\n"
    
    # Send product with image if available
    if product['image_url']:
        await callback.message.delete()
        await callback.message.chat.send_photo(
            photo=product['image_url'],
            caption=text,
            reply_markup=get_product_detail_keyboard(product_id),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product_id),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("add_to_cart_"))
async def select_quantity(callback: CallbackQuery):
    """Show quantity selector"""
    product_id = int(callback.data.split("_")[-1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.answer("❌ المنتج غير موجود", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🛒 اختر الكمية للمنتج:\n\n<b>{product['name']}</b>",
        reply_markup=get_quantity_keyboard(product_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qty_"))
async def add_to_cart(callback: CallbackQuery):
    """Add product to cart"""
    parts = callback.data.split("_")
    quantity = int(parts[1])
    product_id = int(parts[2])
    user_id = callback.from_user.id
    
    product = db.get_product(product_id)
    
    if not product or product['stock'] < quantity:
        await callback.answer("❌ المنتج غير متاح بهذه الكمية", show_alert=True)
        return
    
    db.add_to_cart(user_id, product_id, quantity)
    
    await callback.answer(f"✅ تمت الإضافة! ({quantity}x {product['name']})", show_alert=True)
    await callback.message.edit_text(
        "🛒 <b>تمت الإضافة للسلة!</b>\n\n"
        "ماذا تريد أن تفعل؟",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ متابعة التسوق", callback_data="shop")],
            [InlineKeyboardButton(text="🛒 عرض السلة", callback_data="cart")],
            [InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")],
        ]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    """Show shopping cart"""
    user_id = callback.from_user.id
    cart = db.get_cart(user_id)
    total = db.get_cart_total(user_id)
    
    if not cart:
        await callback.message.edit_text(
            "🛒 <b>سلتك فارغة</b>\n\n"
            "ابدأ التسوق الآن!",
            reply_markup=get_empty_cart_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    text = "🛒 <b>سلتك</b>\n\n"
    
    for item in cart:
        text += f"• <b>{item['name']}</b>\n"
        text += f"  السعر: ${item['price']:.2f} x {item['quantity']}\n"
        text += f"  الإجمالي: ${item['price'] * item['quantity']:.2f}\n\n"
    
    text += f"━━━━━━━━━━━━━━\n"
    text += f"💰 <b>الإجمالي النهائي:</b> ${total:.2f}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_cart_keyboard(user_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_from_cart(callback: CallbackQuery):
    """Remove product from cart"""
    product_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    
    product = db.get_product(product_id)
    db.remove_from_cart(user_id, product_id)
    
    await callback.answer(f"✅ تمت الإزالة! ({product['name']})", show_alert=True)
    
    cart = db.get_cart(user_id)
    
    if not cart:
        await callback.message.edit_text(
            "🛒 <b>سلتك فارغة</b>\n\n"
            "ابدأ التسوق الآن!",
            reply_markup=get_empty_cart_keyboard(),
            parse_mode="HTML"
        )
    else:
        await show_cart(callback)


@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    """Checkout"""
    user_id = callback.from_user.id
    cart = db.get_cart(user_id)
    total = db.get_cart_total(user_id)
    user = db.get_user(user_id)
    
    if not cart:
        await callback.answer("❌ سلتك فارغة", show_alert=True)
        return
    
    text = "✅ <b>تأكيد الطلب</b>\n\n"
    text += f"👤 <b>الاسم:</b> {user['first_name']} {user['last_name'] or ''}\n"
    text += f"📱 <b>الرقم:</b> {user['phone'] or 'لم يتم تعيينه'}\n"
    text += f"📍 <b>العنوان:</b> {user['address'] or 'لم يتم تعيينه'}\n\n"
    
    text += "<b>المنتجات:</b>\n"
    for item in cart:
        text += f"• {item['name']} x{item['quantity']} = ${item['price'] * item['quantity']:.2f}\n"
    
    text += f"\n💰 <b>الإجمالي النهائي:</b> ${total:.2f}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_checkout_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery):
    """Confirm and create order"""
    user_id = callback.from_user.id
    cart = db.get_cart(user_id)
    total = db.get_cart_total(user_id)
    
    if not cart:
        await callback.answer("❌ سلتك فارغة", show_alert=True)
        return
    
    # Create order
    order_id = db.create_order(user_id, total)
    
    if not order_id:
        await callback.answer("❌ خطأ في إنشاء الطلب", show_alert=True)
        return
    
    # Add items to order
    for item in cart:
        db.add_order_item(order_id, item['product_id'], item['quantity'], item['price'])
    
    # Clear cart
    db.clear_cart(user_id)
    
    await callback.answer(f"✅ تم الطلب برقم #{order_id}", show_alert=True)
    
    await callback.message.edit_text(
        f"✅ <b>تم تأكيد طلبك!</b>\n\n"
        f"🎉 رقم الطلب: <b>#{order_id}</b>\n"
        f"💰 المبلغ: <b>${total:.2f}</b>\n\n"
        f"سيتم توصيل طلبك قريباً!\n"
        f"شكراً لتسوقك معنا 💝",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 طلباتي", callback_data="orders")],
            [InlineKeyboardButton(text="🛍️ متابعة التسوق", callback_data="shop")],
            [InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")],
        ]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "orders")
async def show_orders(callback: CallbackQuery):
    """Show user orders"""
    user_id = callback.from_user.id
    orders = db.get_user_orders(user_id)
    
    if not orders:
        await callback.message.edit_text(
            "📦 <b>طلباتك</b>\n\n"
            "لم تقم بأي طلبات حتى الآن",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🛍️ ابدأ التسوق", callback_data="shop"),
                InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu")
            ]]),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "📦 <b>طلباتك</b>",
        reply_markup=get_orders_keyboard(user_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_"))
async def show_order_detail(callback: CallbackQuery):
    """Show order details"""
    order_id = int(callback.data.split("_")[1])
    order = db.get_order(order_id)
    order_items = db.get_order_items(order_id)
    
    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return
    
    text = f"📦 <b>تفاصيل الطلب #{order['order_id']}</b>\n\n"
    text += f"📊 <b>الحالة:</b> {order['status']}\n"
    text += f"📅 <b>التاريخ:</b> {order['created_at']}\n\n"
    
    text += "<b>المنتجات:</b>\n"
    for item in order_items:
        text += f"• {item['name']}\n"
        text += f"  x{item['quantity']} = ${item['price'] * item['quantity']:.2f}\n"
    
    text += f"\n💰 <b>الإجمالي:</b> ${order['total_price']:.2f}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_order_detail_keyboard(order_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "account")
async def show_account(callback: CallbackQuery):
    """Show account menu"""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    text = f"👤 <b>حسابي</b>\n\n"
    text += f"<b>الاسم:</b> {user['first_name']} {user['last_name'] or ''}\n"
    text += f"<b>اسم المستخدم:</b> {user['username'] or 'N/A'}\n"
    text += f"<b>الرقم:</b> {user['phone'] or 'لم يتم تعيينه'}\n"
    text += f"<b>العنوان:</b> {user['address'] or 'لم يتم تعيينه'}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_account_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "set_phone")
async def set_phone(callback: CallbackQuery):
    """Set phone number"""
    await callback.message.edit_text(
        "📱 أرسل رقم هاتفك:\n(مثال: +1234567890)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ إلغاء", callback_data="account")
        ]])
    )
    await callback.answer()


@router.message(F.text)
async def handle_phone(message: Message):
    """Handle phone number"""
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()
    
    user_id = message.from_user.id
    db.update_user(user_id, phone=phone)
    
    await message.reply(
        f"✅ تم حفظ رقمك: {phone}",
        reply_markup=get_account_keyboard()
    )


@router.callback_query(F.data == "set_address")
async def set_address(callback: CallbackQuery):
    """Set address"""
    await callback.message.edit_text(
        "📍 أرسل عنوانك:\n(مثال: الشارع 123، المدينة)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ إلغاء", callback_data="account")
        ]])
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    """Show about page"""
    text = "ℹ️ <b>عن متجر KRD</b>\n\n"
    text += "🏪 متجر KRD هو منصة تسوق احترافية عبر تطبيق Telegram\n\n"
    text += "<b>المميزات:</b>\n"
    text += "✅ منتجات متنوعة\n"
    text += "✅ عملية شراء سهلة\n"
    text += "✅ خدمة توصيل سريعة\n"
    text += "✅ دعم 24/7\n\n"
    text += "📞 للتواصل معنا: @support\n"
    text += "🌐 موقعنا: www.krd-store.com\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_and_home_buttons(),
        parse_mode="HTML"
    )
    await callback.answer()
