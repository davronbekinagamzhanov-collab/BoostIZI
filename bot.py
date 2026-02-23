import asyncio
import logging
import math
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ==========================================
# 1. НАСТРОЙКИ СИСТЕМЫ И БИЗНЕСА
# ==========================================
TOKEN = "8490009050:AAHJTzpsgpeNvyJdbepBd8QrC4K67kX_bS8"
JAP_API_KEY = "619aa1adbd1108aaaa2efb7bae7d632a"
JAP_URL = "https://justanotherpanel.com/api/v2"

ADMIN_ID = 6305773261
KASPI_NUMBER = "+7 706 707 64 34 (Давронбек И.)"

# Финансовая модель (Твои 70%+ прибыли заложены сюда)
USD_TO_KZT = 530   
PROFIT_FACTOR = 3.5 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderProcess(StatesGroup):
    waiting_for_link = State()
    waiting_for_receipt = State()

# ==========================================
# 2. ГЛОБАЛЬНАЯ БАЗА УСЛУГ (МАСШТАБНОЕ ОБНОВЛЕНИЕ)
# ==========================================
SERVICES = {
    "inst": {
        "name": "📸 Instagram",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "eco": {"id": "10146", "name": "🌱 Эконом (Без гарантии)", "rate": 0.475, "start": "0 - 1 час", "speed": "До 200,000 в день"},
                    "r15": {"id": "8642", "name": "🛡 Гарантия 15 дней", "rate": 0.9875, "start": "0 - 3 часа", "speed": "До 100,000 в день"},
                    "r30": {"id": "10131", "name": "🛡 Гарантия 30 дней", "rate": 0.6071, "start": "0 - 2 часа", "speed": "До 20,000 в день"},
                    "r60": {"id": "10142", "name": "🛡 Гарантия 60 дней", "rate": 0.875, "start": "0 - 2 часа", "speed": "До 500,000 в день"},
                    "r90": {"id": "3791", "name": "🛡 Гарантия 90 дней", "rate": 1.375, "start": "0 - 3 часа", "speed": "До 100,000 в день"},
                    "r365": {"id": "10143", "name": "💎 Вечные (Гарантия 365 дней)", "rate": 1.0625, "start": "0 - 2 часа", "speed": "До 500,000 в день"},
                    "unlim": {"id": "10085", "name": "👑 БЕЗЛИМИТНОЕ ВОССТАНОВЛЕНИЕ", "rate": 7.375, "start": "Мгновенно", "speed": "До 200,000 в день"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "eco": {"id": "5626", "name": "🌱 Эконом (Без гарантии)", "rate": 0.1375, "start": "0 - 1 час", "speed": "До 100,000 в день"},
                    "r30": {"id": "10065", "name": "🛡 Гарантия 30 дней", "rate": 0.20, "start": "0 - 1 час", "speed": "До 100,000 в день"},
                    "r60": {"id": "1864", "name": "🛡 Гарантия 60 дней", "rate": 0.26, "start": "0 - 3 часа", "speed": "До 25,000 в день"},
                    "r90": {"id": "2994", "name": "🛡 Гарантия 90 дней", "rate": 0.266, "start": "0 - 3 часа", "speed": "До 25,000 в день"},
                    "r365": {"id": "3130", "name": "💎 Вечные (Гарантия 365 дней)", "rate": 0.27, "start": "0 - 3 часа", "speed": "До 25,000 в день"},
                    "real": {"id": "8933", "name": "🔥 Живые лайки (Высокое качество)", "rate": 1.50, "start": "Мгновенно", "speed": "Естественная"}
                }
            },
            "views": {
                "name": "👀 Просмотры",
                "items": {
                    "video": {"id": "798", "name": "🔥 Видео / Reels (Быстрые)", "rate": 0.0063, "start": "Мгновенно", "speed": "До 1,000,000 в день"},
                    "story": {"id": "312", "name": "📱 Просмотры Историй (Story)", "rate": 0.0032, "start": "0 - 1 час", "speed": "До 100,000 в день"},
                    "igtv": {"id": "6460", "name": "📺 Просмотры IGTV", "rate": 0.125, "start": "0 - 1 час", "speed": "До 5,000,000 в день"},
                    "live": {"id": "8252", "name": "🔴 Прямой эфир (Зрители на 30 мин)", "rate": 3.50, "start": "До 5 минут", "speed": "Мгновенно"}
                }
            },
            "stats": {
                "name": "📈 Статистика (Охваты/Сохранения)",
                "items": {
                    "saves": {"id": "115", "name": "📌 Сохранения публикаций", "rate": 0.05, "start": "0 - 1 час", "speed": "До 100,000 в день"},
                    "reach": {"id": "3333", "name": "📊 Охват и Показы (Reach)", "rate": 0.10, "start": "0 - 1 час", "speed": "Быстро"},
                    "share": {"id": "114", "name": "🚀 Репосты (Shares)", "rate": 0.20, "start": "0 - 1 час", "speed": "Быстро"}
                }
            },
            "comments": {
                "name": "💬 Комментарии",
                "items": {
                    "rand": {"id": "112", "name": "✍️ Случайные комментарии", "rate": 4.375, "start": "0 - 3 часа", "speed": "До 25,000 в день"},
                    "emoji": {"id": "668", "name": "😍 Эмодзи-комментарии", "rate": 4.375, "start": "0 - 3 часа", "speed": "До 25,000 в день"}
                }
            }
        }
    },
    "tt": {
        "name": "🎵 TikTok",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "std": {"id": "6678", "name": "🌱 Базовые (Mix)", "rate": 1.20, "start": "0 - 1 час", "speed": "До 10,000 в день"},
                    "r30": {"id": "5567", "name": "🛡 Гарантия 30 дней", "rate": 3.50, "start": "1 час", "speed": "До 12,000 в день"},
                    "unlim": {"id": "8960", "name": "💎 БЕЗЛИМИТНОЕ ВОССТАНОВЛЕНИЕ", "rate": 4.50, "start": "0 - 2 часа", "speed": "До 5,000 в день"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "eco": {"id": "10022", "name": "🌱 Эконом", "rate": 0.019, "start": "0 - 1 час", "speed": "До 10,000 в день"},
                    "prem": {"id": "10024", "name": "💎 Премиум (Вечные)", "rate": 0.036, "start": "0 - 1 час", "speed": "До 5,000 в день"}
                }
            },
            "views": {
                "name": "👀 Просмотры",
                "items": {
                    "fast": {"id": "2211", "name": "🚀 Мгновенные просмотры", "rate": 0.002, "start": "Мгновенно", "speed": "Очень быстро"}
                }
            },
            "stats": {
                "name": "📈 Репосты и Сохранения",
                "items": {
                    "share": {"id": "3344", "name": "🚀 Репосты видео", "rate": 0.15, "start": "0 - 1 час", "speed": "Быстро"},
                    "saves": {"id": "3345", "name": "📌 Сохранения видео", "rate": 0.10, "start": "0 - 1 час", "speed": "Быстро"}
                }
            }
        }
    },
    "tg": {
        "name": "✈️ Telegram",
        "cats": {
            "subs": {
                "name": "👥 Подписчики в канал/группу",
                "items": {
                    "std": {"id": "9378", "name": "🌱 Стандарт (Мировой микс)", "rate": 0.6875, "start": "0 - 1 час", "speed": "До 500,000 в день"},
                    "prem": {"id": "9382", "name": "💎 Премиум (Высокое качество)", "rate": 1.50, "start": "0 - 1 час", "speed": "До 50,000 в день"},
                    "nodrop": {"id": "8552", "name": "🛡 Без списаний (Zero Drop)", "rate": 1.80, "start": "Мгновенно", "speed": "До 10,000 в день"}
                }
            },
            "views": {
                "name": "👀 Просмотры постов",
                "items": {
                    "post1": {"id": "8470", "name": "👁 Просмотры на 1 последний пост", "rate": 0.0125, "start": "Мгновенно", "speed": "До 100,000 в день"},
                    "post5": {"id": "8471", "name": "👁 Просмотры на 5 последних постов", "rate": 0.05, "start": "Мгновенно", "speed": "До 100,000 в день"},
                    "post10": {"id": "8472", "name": "👁 Просмотры на 10 последних постов", "rate": 0.10, "start": "Мгновенно", "speed": "До 100,000 в день"}
                }
            },
            "reacts": {
                "name": "🔥 Реакции на посты",
                "items": {
                    "pos": {"id": "9988", "name": "👍 Позитивные реакции (Микс)", "rate": 0.25, "start": "0 - 1 час", "speed": "Быстро"},
                    "prem": {"id": "9989", "name": "⭐ Premium-реакции", "rate": 0.80, "start": "0 - 1 час", "speed": "Средняя"}
                }
            }
        }
    },
    "yt": {
        "name": "▶️ YouTube",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "r30": {"id": "6602", "name": "🛡 Гарантия 30 дней", "rate": 4.00, "start": "0 - 12 часов", "speed": "До 500 в день"},
                    "unlim": {"id": "10099", "name": "💎 БЕЗЛИМИТНОЕ ВОССТАНОВЛЕНИЕ", "rate": 15.00, "start": "0 - 24 часа", "speed": "До 1000 в день"}
                }
            },
            "views": {
                "name": "👀 Просмотры",
                "items": {
                    "std": {"id": "7709", "name": "🌱 Стандартные просмотры", "rate": 1.50, "start": "0 - 6 часов", "speed": "До 10,000 в день"},
                    "prem": {"id": "6542", "name": "💎 Премиум (Высокое удержание)", "rate": 3.00, "start": "0 - 2 часа", "speed": "До 50,000 в день"},
                    "shorts": {"id": "8811", "name": "📱 Просмотры YouTube Shorts", "rate": 1.20, "start": "Мгновенно", "speed": "До 100,000 в день"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "std": {"id": "7002", "name": "👍 Лайки на видео", "rate": 2.50, "start": "0 - 1 час", "speed": "Естественная"}
                }
            }
        }
    }
}

# ==========================================
# 3. ИНТЕРФЕЙС И НАВИГАЦИЯ КЛИЕНТА
# ==========================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    welcome_text = (
        f"👋 **Добро пожаловать, {message.from_user.first_name}!**\n\n"
        "Вы находитесь в сервисе умного и безопасного продвижения в социальных сетях 🚀\n\n"
        "✨ **Что мы умеем?**\n"
        "Мы помогаем вашим аккаунтам расти. В нашем арсенале только проверенные мировые серверы, обеспечивающие высокую скорость и надежность.\n\n"
        "🛡 **Безопасность:** Нам не нужны ваши пароли — только ссылка на профиль или пост.\n"
        "💎 **Качество:** Вы сами выбираете тариф — от экономного старта до премиум-накрутки с гарантией от списаний до 365 дней.\n\n"
        "👇 Выберите действие ниже, чтобы начать:"
    )
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🚀 Начать продвижение", callback_data="platforms"))
    kb.row(types.InlineKeyboardButton(text="ℹ️ О нас / Как это работает", callback_data="about"))
    
    await message.answer(welcome_text, reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "home")
async def go_home(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await cmd_start(callback.message, state)

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    text = (
        "ℹ️ **О нашем сервисе**\n\n"
        "🛠 **Как сделать заказ?**\n"
        "1. Нажмите «Начать продвижение» и выберите соцсеть.\n"
        "2. Выберите нужную услугу и уровень качества.\n"
        "3. Укажите объем и отправьте ссылку на ваш аккаунт/пост.\n"
        "4. Оплатите заказ переводом на Kaspi и отправьте боту скриншот чека.\n"
        "5. После проверки администратором заказ запустится автоматически! 🚀\n\n"
        "💡 **Что такое гарантия?**\n"
        "Если вы выбрали услугу с гарантией (например, 30 или 365 дней), то в случае отписок система автоматически восполнит потери абсолютно бесплатно.\n\n"
        "📞 **Поддержка:** Если возникли вопросы, свяжитесь с нами @davronbk7."
    )
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="home"))
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "platforms")
async def show_platforms(callback: types.CallbackQuery):
    text = "📱 **Выберите социальную сеть для продвижения:**"
    kb = InlineKeyboardBuilder()
    
    buttons = [types.InlineKeyboardButton(text=p_data["name"], callback_data=f"p_{p_key}") for p_key, p_data in SERVICES.items()]
    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i+2])
        
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="home"))
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("p_"))
async def choose_category(callback: types.CallbackQuery):
    p_key = callback.data.split("_")[1]
    plat_data = SERVICES[p_key]
    
    kb = InlineKeyboardBuilder()
    buttons = [types.InlineKeyboardButton(text=c_data["name"], callback_data=f"c_{p_key}_{c_key}") for c_key, c_data in plat_data["cats"].items()]
    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i+2])
    
    kb.row(types.InlineKeyboardButton(text="⬅️ Выбор платформы", callback_data="platforms"))
    await callback.message.edit_text(f"Платформа: **{plat_data['name']}**\n\n🎯 **Что именно будем накручивать?**", reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("c_"))
async def choose_quality(callback: types.CallbackQuery):
    _, p_key, c_key = callback.data.split("_")
    cat_data = SERVICES[p_key]["cats"][c_key]
    
    kb = InlineKeyboardBuilder()
    for q_key, q_data in cat_data["items"].items():
        kb.row(types.InlineKeyboardButton(text=q_data['name'], callback_data=f"q_{p_key}_{c_key}_{q_key}"))
        
    kb.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"p_{p_key}"))
    
    await callback.message.edit_text("⚙️ **Выберите подходящий пакет (качество):**", reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("q_"))
async def choose_volume(callback: types.CallbackQuery, state: FSMContext):
    _, p_key, c_key, q_key = callback.data.split("_")
    service = SERVICES[p_key]["cats"][c_key]["items"][q_key]
    
    unit_price = (service["rate"] * USD_TO_KZT * PROFIT_FACTOR) / 1000
    
    await state.update_data(
        api_id=service["id"],
        s_name=service["name"],
        unit_price=unit_price
    )
    
    kb = InlineKeyboardBuilder()
    volumes = [100, 500, 1000, 2000, 5000, 10000]
    
    vol_buttons = []
    for vol in volumes:
        total = math.ceil(vol * unit_price)
        if total < 200: total = 200 
        vol_buttons.append(types.InlineKeyboardButton(text=f"🛒 {vol} шт. — {total} ₸", callback_data=f"v_{vol}"))
        
    for i in range(0, len(vol_buttons), 2):
        kb.row(*vol_buttons[i:i+2])
        
    kb.row(types.InlineKeyboardButton(text="⬅️ Отмена", callback_data="platforms"))
    
    text = (
        f"📦 Выбранный пакет: **{service['name']}**\n\n"
        f"⏱ **Время старта:** {service['start']}\n"
        f"🚀 **Скорость накрутки:** {service['speed']}\n\n"
        f"🔢 **Укажите желаемый объем:**"
    )
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

# ==========================================
# 4. ОФОРМЛЕНИЕ И ОПЛАТА
# ==========================================

@dp.callback_query(F.data.startswith("v_"))
async def request_link(callback: types.CallbackQuery, state: FSMContext):
    vol = int(callback.data.split("_")[1])
    data = await state.get_data()
    
    total = math.ceil(vol * data["unit_price"])
    if total < 200: total = 200
    
    await state.update_data(vol=vol, total=total)
    
    text = (
        f"✅ Отлично!\n\n"
        f"⚠ ВАЖНО: ВАШ АККАУНТ ДОЛЖЕН БЫТЬ ОТКРЫТЫМ \n\n"
        f"Ваш заказ: **{data['s_name']}**\n"
        f"Объем: **{vol} шт.**\n"
        f"Сумма к оплате: **{total} ₸**\n\n"
        "🔗 **Отправьте ссылку** (на нужный профиль или публикацию) ответным сообщением:"
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(OrderProcess.waiting_for_link)

@dp.message(OrderProcess.waiting_for_link)
async def request_receipt(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    
    text = (
        f"💳 **ДЕТАЛИ ОПЛАТЫ**\n\n"
        f"К переводу: **{data['total']} ₸**\n"
        f"🏦 Kaspi Bank: `{KASPI_NUMBER}`\n\n"
        "📸 **Пожалуйста, отправьте скриншот или PDF-чек об оплате в этот чат.**\n\n"
        "*(Без чека заказ не будет передан в обработку)*"
    )
    await message.answer(text, parse_mode="Markdown")
    await state.set_state(OrderProcess.waiting_for_receipt)

@dp.message(OrderProcess.waiting_for_receipt, F.photo | F.document)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user
    
    file_id = message.document.file_id if message.document else message.photo[-1].file_id
    callback_payload = f"{data['api_id']}_{data['vol']}_{user.id}"
    
    admin_text = (
        f"⚠️ ЗАПРОС НА АВТОРИЗАЦИЮ ЗАКАЗА\n\n"
        f"👤 От: @{user.username} (ID: {user.id})\n"
        f"📦 Услуга: {data['s_name']} (API ID: {data['api_id']})\n"
        f"🔢 Количество: {data['vol']}\n"
        f"💰 Ожидаемая сумма: {data['total']} ₸\n\n"
        f"🔗 Ссылка:\n{data['link']}"
    )
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="✅ ПОДТВЕРДИТЬ И ЗАПУСТИТЬ", callback_data=f"ok_{callback_payload}"))
    kb.row(types.InlineKeyboardButton(text="❌ Не та сумма", callback_data=f"no_{user.id}_1"))
    kb.row(types.InlineKeyboardButton(text="❌ Мало денег", callback_data=f"no_{user.id}_2"))
    kb.row(types.InlineKeyboardButton(text="❌ Переплата", callback_data=f"no_{user.id}_3"))
    kb.row(types.InlineKeyboardButton(text="❌ Это не чек", callback_data=f"no_{user.id}_4"))
    
    if message.document:
        await bot.send_document(ADMIN_ID, file_id, caption=admin_text, reply_markup=kb.as_markup())
    else:
        await bot.send_photo(ADMIN_ID, file_id, caption=admin_text, reply_markup=kb.as_markup())
        
    await message.answer("⏳ Чек принят системой! Администратор проверяет поступление средств. Уведомление о старте накрутки придет сюда же.")
    await state.clear()

# ==========================================
# 5. ПАНЕЛЬ УПРАВЛЕНИЯ ДЛЯ ТЕБЯ (АДМИНА)
# ==========================================

@dp.callback_query(F.data.startswith("ok_"))
async def admin_approve(callback: types.CallbackQuery):
    try:
        _, payload = callback.data.split("_", 1)
        api_id, vol, user_id = payload.split("_")
        
        link = ""
        lines = callback.message.caption.split("\n")
        for i, line in enumerate(lines):
            if "🔗 Ссылка:" in line:
                link = lines[i+1].strip() if i+1 < len(lines) else line.replace("🔗 Ссылка:", "").strip()
        
        if not link:
            await callback.answer("Ошибка: ссылка не обнаружена.", show_alert=True)
            return

        api_data = {
            'key': JAP_API_KEY,
            'action': 'add',
            'service': api_id,
            'link': link,
            'quantity': vol
        }
        
        response = requests.post(JAP_URL, data=api_data).json()
        
        if "order" in response:
            order_id = response['order']
            await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🟢 [УСПЕШНЫЙ ЗАПУСК. ЗАКАЗ JAP ID: {order_id}]")
            await bot.send_message(int(user_id), f"🎉 **Отличные новости!**\nВаша оплата подтверждена. Заказ передан в работу (ID: {order_id}).\nСпасибо, что выбрали нас!")
        else:
            api_err = response.get("error", "Неизвестная ошибка")
            await callback.message.answer(f"Сбой отправки JAP: {api_err}", show_alert=True)

    except Exception as e:
        await callback.message.answer(f"Сбой системы: {e}", show_alert=True)

@dp.callback_query(F.data.startswith("no_"))
async def admin_reject(callback: types.CallbackQuery):
    _, user_id, reason_code = callback.data.split("_")
    
    reasons = {
        "1": "Поступила неверная сумма.",
        "2": "Сумма перевода меньше стоимости заказа.",
        "3": "Обнаружена переплата. Обратитесь к администратору.",
        "4": "Загруженный файл не является действительным банковским чеком."
    }
    
    reject_msg = reasons.get(reason_code, "Отказ в авторизации.")
    
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🔴 [ОТКЛОНЕН: {reject_msg}]")
    await bot.send_message(int(user_id), f"❌ **К сожалению, ваш заказ не принят.**\n\nПричина: {reject_msg}\nЕсли вы уверены, что всё сделали правильно, свяжитесь с технической поддержкой.", parse_mode="Markdown")

async def main():
    logging.info("Система готова к приему заказов.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
