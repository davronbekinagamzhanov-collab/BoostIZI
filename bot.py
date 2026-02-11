import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- НАСТРОЙКИ (ТВОИ ДАННЫЕ) ---
TOKEN = "8490009050:AAHJTzpsgpeNvyJdbepBd8QrC4K67kX_bS8"
SALEM_API_KEY = "jBBLsZO4DsvbZ8l09pte7kF6CvWWvzEW4L0qN5vyCIS91Mkuu4qCVBKrwuQI"
SALEM_URL = "https://salemsmm.com/api/v2"
ADMIN_ID = 6305773261
KASPI_NUMBER = "+7 706 707 64 34" # Давронбек И.

# --- ЧЕСТНАЯ БАЗА УСЛУГ (ИСПРАВЛЕННАЯ) ---
SERVICES = {
    # === INSTAGRAM ПОДПИСЧИКИ ===
    "inst_subs_cheap": {
        "id": "256", 
        "name": "📉 Подписчики [Эконом] (Возможны списания)", 
        "buy_price": 592, 
        "cat": "subs"
    },
    "inst_subs_garant": {
        "id": "205", 
        "name": "🛡️ Подписчики [Гарантия 30 дней] R30", 
        "buy_price": 752, 
        "cat": "subs"
    },

    # === INSTAGRAM ЛАЙКИ (БЕЗ РОССИИ, ТОЛЬКО ЧЕТКИЕ) ===
    "inst_likes_cheap": {
        "id": "170", 
        "name": "📉 Лайки [Дешевые] (Без гарантии)", 
        "buy_price": 148, 
        "cat": "likes"
    },
    "inst_likes_fast": {
        "id": "193", 
        "name": "⚡ Лайки [Быстрые] (Стандарт / Без гарантии)", 
        "buy_price": 238, 
        "cat": "likes"
    },
    "inst_likes_gold": {
        "id": "54", 
        "name": "💎 Лайки KZ [Гарантия 1 ГОД] Luxe", 
        "buy_price": 2250, 
        "cat": "likes"
    },

    # === INSTAGRAM ПРОСМОТРЫ ===
    "inst_views_reels": {"id": "152", "name": "🎬 Просмотры Reels [Хит продаж]", "buy_price": 3, "cat": "views"},
    "inst_views_fast": {"id": "213", "name": "⚡ Просмотры Reels [Молния]", "buy_price": 6.1, "cat": "views"},
    "inst_views_story": {"id": "176", "name": "👁 Просмотры Истории", "buy_price": 88, "cat": "views"},

    # === INSTAGRAM КОММЕНТАРИИ ===
    "inst_comm_rand": {"id": "260", "name": "💬 Комментарии [Рандомные]", "buy_price": 653, "cat": "comm"},
    "inst_comm_emoji": {"id": "25", "name": "😍 Комментарии [Emoji]", "buy_price": 5048, "cat": "comm"},
    "inst_comm_likes": {"id": "168", "name": "👍 Лайки на Комментарий", "buy_price": 951, "cat": "comm"},

    # === INSTAGRAM СТАТИСТИКА ===
    "inst_stats_save": {"id": "109", "name": "📌 Сохранения [Быстрые]", "buy_price": 49, "cat": "stats"},
    "inst_stats_reach": {"id": "110", "name": "📊 Охваты + Показы", "buy_price": 42, "cat": "stats"},
    "inst_stats_top": {"id": "14", "name": "🔝 Вывод в ТОП (Из Интересного)", "buy_price": 59, "cat": "stats"},
    "inst_reposts": {"id": "258", "name": "🚀 Репосты (Поделиться)", "buy_price": 12.4, "cat": "stats"},
    "inst_profile": {"id": "30", "name": "👀 Посещения Профиля", "buy_price": 101, "cat": "stats"},

    # === INSTAGRAM ЭФИР ===
    "inst_live_30": {"id": "31", "name": "🔴 Эфир [30 мин] (Зрители)", "buy_price": 2923, "cat": "live"},
    "inst_live_60": {"id": "32", "name": "🔴 Эфир [60 мин] (Зрители)", "buy_price": 4279, "cat": "live"},
    "inst_live_90": {"id": "33", "name": "🔴 Эфир [90 мин] (Зрители)", "buy_price": 6825, "cat": "live"},
    "inst_live_120": {"id": "34", "name": "🔴 Эфир [120 мин] (Зрители)", "buy_price": 9234, "cat": "live"},

    # === TIKTOK ПОДПИСЧИКИ ===
    "tt_subs_cheap": {
        "id": "233", 
        "name": "📉 TikTok Подписчики [Эконом] (Без гарантии)", 
        "buy_price": 786, 
        "cat": "tt_subs"
    },
    "tt_subs_stable": {
        "id": "222", 
        "name": "⚖️ TikTok Подписчики [Стабильные] (Мало списаний)", 
        "buy_price": 1237, 
        "cat": "tt_subs"
    },
    "tt_subs_garant": {
        "id": "235", 
        "name": "🛡️ TikTok Подписчики [Гарантия 30 дней]", 
        "buy_price": 1291, 
        "cat": "tt_subs"
    },
    "tt_subs_r30": {
        "id": "236", 
        "name": "🛡️ TikTok Подписчики [R30] (Высокое качество)", 
        "buy_price": 1615, 
        "cat": "tt_subs"
    },

    # === TIKTOK ЛАЙКИ ===
    "tt_likes_cheap": {
        "id": "216", 
        "name": "📉 TikTok Лайки [Эконом] (Без гарантии)", 
        "buy_price": 77, 
        "cat": "tt_likes"
    },
    "tt_likes_qual": {
        "id": "187", 
        "name": "👍 TikTok Лайки [Качественные] (Живые профили)", 
        "buy_price": 113, 
        "cat": "tt_likes"
    },
    "tt_likes_gold": {
        "id": "227", 
        "name": "💎 TikTok Лайки [ВЕЧНЫЕ / Без списаний]", 
        "buy_price": 273, 
        "cat": "tt_likes"
    },

    # === TIKTOK ПРОСМОТРЫ ===
    "tt_views_best": {"id": "183", "name": "👀 TikTok Просмотры [Выгодно]", "buy_price": 15.7, "cat": "tt_views"},
    "tt_views_v2": {"id": "220", "name": "👀 TikTok Просмотры [Быстрые]", "buy_price": 22.2, "cat": "tt_views"},
    "tt_views_rec": {"id": "207", "name": "👀 TikTok Просмотры [Рекомендуем]", "buy_price": 29.7, "cat": "tt_views"},
    "tt_views_stable": {"id": "157", "name": "👀 TikTok Просмотры [Стабильные]", "buy_price": 44, "cat": "tt_views"},

    # === TIKTOK СТАТИСТИКА ===
    "tt_saves": {"id": "162", "name": "📌 Сохранения TikTok", "buy_price": 68, "cat": "tt_stats"},
    "tt_shares": {"id": "228", "name": "🚀 Репосты TikTok", "buy_price": 76, "cat": "tt_stats"},

    # === TIKTOK ПРЯМОЙ ЭФИР ===
    "tt_live_likes": {"id": "45", "name": "❤️ Лайки на Эфир", "buy_price": 68, "cat": "tt_live"},
    "tt_live_comm": {"id": "46", "name": "💬 Комментарии для Эфира", "buy_price": 3758, "cat": "tt_live"},
    "tt_live_15": {"id": "47", "name": "🔴 Эфир [15 мин] (Зрители)", "buy_price": 4760, "cat": "tt_live"},
    "tt_live_30": {"id": "48", "name": "🔴 Эфир [30 мин] (Зрители)", "buy_price": 7433, "cat": "tt_live"},
    "tt_live_60": {"id": "49", "name": "🔴 Эфир [60 мин] (Зрители)", "buy_price": 11900, "cat": "tt_live"},
    "tt_live_90": {"id": "50", "name": "🔴 Эфир [90 мин] (Зрители)", "buy_price": 17454, "cat": "tt_live"}
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Order(StatesGroup):
    waiting_for_link = State()
    waiting_for_check = State()

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🚀 Начать продвижение", callback_data="start_order"))
    builder.row(types.InlineKeyboardButton(text="📖 Как это работает?", callback_data="instructions"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # ТВОЕ ОРИГИНАЛЬНОЕ ПРИВЕТСТВИЕ
    welcome = (
        "⚡ **BoostIZI — Твой мощный старт в топ!** ⚡\n\n"
        "Мы превращаем твои профили в настоящие магниты для аудитории. "
        "Самая быстрая и безопасная накрутка в Казахстане здесь.\n\n"
        "ℹ️ **Что мы умеем:**\n"
        "• Мгновенный запуск живых подписчиков и лайков.\n"
        "• Умные алгоритмы, которые не пугают систему защиты соцсетей.\n\n"
        "⚠️ **ВАЖНО:** Минимальная сумма заказа — **100 ₸** (ограничение системы переводов Kaspi).\n\n"
        "🔓 **Важно:** Ваш аккаунт должен быть **ОТКРЫТЫМ**.\n\n"
        "🔥 *Внимание! В ближайшее время мы добавим Telegram, YouTube и другие платформы. Наша база расширяется специально для вас!*\n\n"
        "👇 **Выберите платформу для продвижения прямо сейчас:**"
    )
    await message.answer(welcome, reply_markup=main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "instructions")
async def show_instr(callback: types.CallbackQuery):
    text = (
        "📋 **Правила успешного заказа:**\n\n"
        "1. 🔓 **Важно:** Ваш аккаунт должен быть **ОТКРЫТЫМ**.\n"
        "2. 💳 Минимальный платеж — **100 ₸**.\n"
        "3. 🔗 Ссылку нужно указывать точно (на пост или профиль).\n"
        "4. ⚡ Старт заказа: от 10 до 60 минут после проверки чека."
    )
    builder = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: types.CallbackQuery):
    await callback.message.delete()
    await cmd_start(callback.message)

@dp.callback_query(F.data == "start_order")
async def choose_platform(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📸 Instagram", callback_data="platform_inst"))
    builder.row(types.InlineKeyboardButton(text="📱 TikTok", callback_data="platform_tt"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start"))
    await callback.message.edit_text("Выберите платформу для накрутки: 👇", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("platform_"))
async def show_categories(callback: types.CallbackQuery):
    platform = callback.data.split("_")[1]
    builder = InlineKeyboardBuilder()
    if platform == "inst":
        categories = [("👥 Подписчики", "subs"), ("❤️ Лайки", "likes"), ("🎬 Просмотры", "views"), ("💬 Комментарии", "comm"), ("📊 Статистика", "stats"), ("🔴 Прямой Эфир", "live")]
    else:
        categories = [("👥 Подписчики", "tt_subs"), ("❤️ Лайки", "tt_likes"), ("👀 Просмотры", "tt_views"), ("🚀 Репосты/Стат", "tt_stats"), ("🔴 Прямой Эфир", "tt_live")]
    
    for text, cat in categories:
        builder.row(types.InlineKeyboardButton(text=text, callback_data=f"cat_{cat}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="start_order"))
    await callback.message.edit_text("💎 **Выберите категорию услуг:**", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("cat_"))
async def show_services(callback: types.CallbackQuery):
    cat_name = callback.data.replace("cat_", "")
    builder = InlineKeyboardBuilder()
    for key, data in SERVICES.items():
        if data['cat'] == cat_name:
            builder.row(types.InlineKeyboardButton(text=data['name'], callback_data=f"serv_{key}"))
    platform = "inst" if any(x in cat_name for x in ["subs","likes","views","comm","stats","live"]) and "tt" not in cat_name else "tt"
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"platform_{platform}"))
    await callback.message.edit_text("🔹 **Выберите пакет:**", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("serv_"))
async def choose_amount(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_", 1)[1]
    service = SERVICES[key]
    price_per_unit = (service['buy_price'] / 1000) * 1.7 # ТВОЯ НАЦЕНКА 70%
    await state.update_data(s_id=service['id'], s_name=service['name'], unit_price=price_per_unit, s_key=key, cat=service['cat'])
    
    builder = InlineKeyboardBuilder()
    # КНОПКИ ОТ МАЛОГО К БОЛЬШОМУ
    for a in [100, 500, 1000, 2500, 5000, 10000]:
        total_p = round(a * price_per_unit)
        builder.row(types.InlineKeyboardButton(text=f"{a} шт. — {total_p} ₸", callback_data=f"amt_{a}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cat_{service['cat']}"))
    await callback.message.edit_text(f"🔢 **{service['name']}**\n\nВыберите количество. Аккаунт должен быть **ОТКРЫТ**.\nМинимальный заказ: **100 ₸**", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("amt_"))
async def get_link(callback: types.CallbackQuery, state: FSMContext):
    amount = int(callback.data.split("_")[1])
    data = await state.get_data()
    total = round(amount * data['unit_price'])
    if total < 100:
        await callback.answer(f"⚠️ Сумма {total} ₸ слишком мала. Выберите пакет побольше!", show_alert=True)
        return
    await state.update_data(final_amount=amount, final_price=total)
    
    msg_text = (
        f"✅ Цена: **{total} ₸**\n\n"
        "🔗 **Отправьте ССЫЛКУ на профиль или пост:**\n\n"
        "⚠️ **ВНИМАНИЕ: Аккаунт должен быть ОТКРЫТЫМ!**\n"
        "Если профиль закрыт, накрутка не сработает, а **деньги не вернутся**. Проверьте настройки!"
    )
    await callback.message.answer(msg_text, parse_mode="Markdown")
    await state.set_state(Order.waiting_for_link)

@dp.message(Order.waiting_for_link)
async def get_check(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    await message.answer(f"💳 **ОПЛАТА**\nСумма: **{data['final_price']} ₸**\nKaspi: `{KASPI_NUMBER}`\nПолучатель: Давронбек И.\n\nПришлите **фото чека** или **PDF-файл**!")
    await state.set_state(Order.waiting_for_check)

@dp.message(Order.waiting_for_check, F.photo | F.document)
async def to_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    u_id = message.from_user.id
    info = f"{data['s_id']}|{data['final_amount']}|{data['link']}|{u_id}"
    caption = f"💰 ЗАКАЗ: {data['s_name']}\nКол-во: {data['final_amount']}\nСсылка: {data['link']}\nЦена: {data['final_price']} ₸"
    
    # ТВОИ КНОПКИ ДЛЯ АДМИНА (НЕ ИЗМЕНЯЛ)
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="✅ ОДОБРИТЬ (ЗАПУСК)", callback_data=f"ok_{info}"))
    kb.row(types.InlineKeyboardButton(text="❌ МАЛО ДЕНЕГ", callback_data=f"rej_3_{u_id}"),
           types.InlineKeyboardButton(text="❌ ОПЛАТЫ НЕТ", callback_data=f"rej_4_{u_id}"))
    kb.row(types.InlineKeyboardButton(text="❌ НЕВЕРНЫЙ ЧЕК", callback_data=f"rej_2_{u_id}"),
           types.InlineKeyboardButton(text="❌ УНИВЕР. ОТКАЗ", callback_data=f"rej_5_{u_id}"))

    if message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=kb.as_markup())
    elif message.document:
        await bot.send_document(ADMIN_ID, message.document.file_id, caption=caption, reply_markup=kb.as_markup())
    
    await message.answer("✅ **Чек получен!** Подождите 60 секунд, мы проверяем оплату... ✨")
    await state.clear()

@dp.callback_query(F.data.startswith("ok_"))
async def api_confirm(callback: types.CallbackQuery):
    _, info = callback.data.split("_")
    s_id, qty, link, u_id = info.split("|")
    res = requests.post(SALEM_URL, data={'key': SALEM_API_KEY, 'action': 'add', 'service': s_id, 'link': link, 'quantity': qty}).json()
    if "order" in res:
        await callback.message.edit_caption(caption=f"✅ Заказ #{res['order']} запущен!")
        await bot.send_message(u_id, "🚀 **Оплата подтверждена!** Заказ уже в работе. Скоро увидите результат! ✨\n\n💬 **Поддержка:** @davronbk7")
    else:
        await callback.message.answer(f"❌ Ошибка API: {res.get('error')}")

@dp.callback_query(F.data.startswith("rej_"))
async def handle_reject(callback: types.CallbackQuery):
    _, r_id, u_id = callback.data.split("_")
    # ТВОИ ТЕКСТЫ ОТКАЗА (НЕ ИЗМЕНЯЛ)
    reasons = {
        "1": "❌ **Ошибка в ссылке или аккаунт закрыт.** Мы не можем запустить заказ. Откройте профиль и отправьте чек заново.",
        "2": "❌ **Неправильный формат чека.** На скриншоте не видно деталей платежа. Отправьте четкий скриншот или PDF.",
        "3": "❌ **Неполная оплата.** Сумма в чеке меньше стоимости пакета. Доплатите разницу и отправьте чеки заново.",
        "4": "❌ **Перевод еще не поступил.** Возможно, банк задерживает операцию. Подождите 5 минут и отправьте чек повторно.",
        "5": "❌ **Заказ отклонен.** Оплата не подтверждена или возникла ошибка. Свяжитесь с админом для уточнения: @davronbk7"
    }
    await bot.send_message(u_id, reasons[r_id])
    await callback.message.edit_caption(caption=f"❌ Отклонено: {reasons[r_id][:35]}...")
    await callback.answer("Клиент уведомлен")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())