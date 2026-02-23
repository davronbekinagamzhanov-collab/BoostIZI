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

USD_TO_KZT = 530   
PROFIT_FACTOR = 3.5 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderProcess(StatesGroup):
    language = State()
    waiting_for_link = State()
    waiting_for_receipt = State()

# ==========================================
# СЛОВАРИ ПЕРЕВОДОВ (ПОЛНЫЕ И КРАСИВЫЕ ТЕКСТЫ)
# ==========================================
LANG_DICT = {
    "ru": {
        "welcome": "👋 **Добро пожаловать, {name}!**\n\nВы находитесь в сервисе умного и безопасного продвижения в социальных сетях 🚀\n\n✨ **Что мы умеем?**\nМы помогаем вашим аккаунтам расти. В нашем арсенале только проверенные мировые серверы, обеспечивающие высокую скорость и надежность.\n\n🛡 **Безопасность:** Нам не нужны ваши пароли — только ссылка на профиль или пост.\n💎 **Качество:** Вы сами выбираете тариф — от экономного старта до премиум-накрутки с гарантией от списаний до 365 дней.\n\n👇 Выберите действие ниже, чтобы начать:",
        "btn_start": "🚀 Начать продвижение",
        "btn_about": "ℹ️ О нас / Как это работает",
        "btn_lang": "🌍 Выбрать язык",
        "about_text": "ℹ️ **О нашем сервисе**\n\n🛠 **Как сделать заказ?**\n1. Нажмите «Начать продвижение» и выберите соцсеть.\n2. Выберите нужную услугу и уровень качества.\n3. Укажите объем и отправьте ссылку на ваш аккаунт/пост.\n4. Оплатите заказ переводом на Kaspi и отправьте боту скриншот чека.\n5. После проверки администратором заказ запустится автоматически! 🚀\n\n💡 **Что такое гарантия?**\nЕсли вы выбрали услугу с гарантией (например, 30 или 365 дней), то в случае отписок система автоматически восполнит потери абсолютно бесплатно.\n\n📞 **Поддержка:** Если возникли вопросы, свяжитесь с нами @davronbk7.",
        "btn_back": "⬅️ Назад",
        "choose_plat": "📱 **Выберите социальную сеть для продвижения:**",
        "choose_cat": "🎯 **Что именно будем накручивать?**",
        "choose_pack": "⚙️ **Выберите подходящий пакет (качество):**",
        "pack_info": "📦 Выбранный пакет: **{name}**\n\n⏱ **Время старта:** {start}\n🚀 **Скорость накрутки:** {speed}\n🛡 **Срок / Удержание:** {retention}\n\n🔢 **Укажите желаемый объем:**",
        "btn_cancel": "⬅️ Отмена",
        "link_req": "✅ Отлично!\n\n⚠ ВАЖНО: ВАШ АККАУНТ ДОЛЖЕН БЫТЬ ОТКРЫТЫМ\n\nВаш заказ: **{name}**\nОбъем: **{vol} шт.**\nСумма к оплате: **{total} ₸**\n\n🔗 **Отправьте ссылку** (на нужный профиль или публикацию) ответным сообщением:",
        "pay_req": "💳 **ДЕТАЛИ ОПЛАТЫ**\n\nК переводу: **{total} ₸**\n🏦 Kaspi Bank: `{kaspi}`\n\n📸 **Пожалуйста, отправьте скриншот или PDF-чек об оплате в этот чат.**\n\n*(Без чека заказ не будет передан в обработку)*"
    },
    "kk": {
        "welcome": "👋 **Қош келдіңіз, {name}!**\n\nСіз әлеуметтік желілердегі ақылды және қауіпсіз ілгерілету қызметіндесіз 🚀\n\n✨ **Біз не істей аламыз?**\nБіз сіздің аккаунттарыңыздың өсуіне көмектесеміз. Біздің арсеналда тек жоғары жылдамдық пен сенімділікті қамтамасыз ететін тексерілген әлемдік серверлер бар.\n\n🛡 **Қауіпсіздік:** Бізге сіздің құпия сөздеріңіз қажет емес — тек профильге немесе постқа сілтеме жеткілікті.\n💎 **Сапа:** Тарифті өзіңіз таңдайсыз — эконом-старттан бастап 365 күнге дейін жазылушылардың кемуінен кепілдігі бар премиум-накруткаға дейін.\n\n👇 Бастау үшін төмендегі әрекетті таңдаңыз:",
        "btn_start": "🚀 Ілгерілетуді бастау",
        "btn_about": "ℹ️ Біз туралы / Қалай жұмыс істейді",
        "btn_lang": "🌍 Тілді өзгерту",
        "about_text": "ℹ️ **Біздің қызметіміз туралы**\n\n🛠 **Тапсырысты қалай беруге болады?**\n1. «Ілгерілетуді бастау» түймесін басып, әлеуметтік желіні таңдаңыз.\n2. Қажетті қызмет пен сапа деңгейін таңдаңыз.\n3. Көлемін көрсетіп, аккаунтыңызға/постыңызға сілтеме жіберіңіз.\n4. Kaspi арқылы аударым жасап, тапсырысты төлеңіз және ботқа чектің скриншотын жіберіңіз.\n5. Әкімші тексергеннен кейін тапсырыс автоматты түрде басталады! 🚀\n\n💡 **Кепілдік дегеніміз не?**\nЕгер сіз кепілдігі бар қызметті таңдасаңыз (мысалы, 30 немесе 365 күн), жазылушылар кеміген жағдайда жүйе жоғалтқан көлемді толығымен тегін қалпына келтіреді.\n\n📞 **Қолдау:** Сұрақтарыңыз болса, бізбен байланысыңыз @davronbk7.",
        "btn_back": "⬅️ Артқа",
        "choose_plat": "📱 **Ілгерілету үшін әлеуметтік желіні таңдаңыз:**",
        "choose_cat": "🎯 **Нені көбейтеміз?**",
        "choose_pack": "⚙️ **Сәйкес пакетті (сапаны) таңдаңыз:**",
        "pack_info": "📦 Таңдалған пакет: **{name}**\n\n⏱ **Басталуы:** {start}\n🚀 **Жылдамдық:** {speed}\n🛡 **Мерзімі:** {retention}\n\n🔢 **Қажетті көлемді көрсетіңіз:**",
        "btn_cancel": "⬅️ Болдырмау",
        "link_req": "✅ Керемет!\n\n⚠ НАЗАР АУДАРЫҢЫЗ: АККАУНТЫҢЫЗ АШЫҚ БОЛУЫ ТИІС\n\nСіздің тапсырысыңыз: **{name}**\nКөлемі: **{vol} шт.**\nТөлем сомасы: **{total} ₸**\n\n🔗 **Сілтемені жіберіңіз** (профильге немесе постқа):",
        "pay_req": "💳 **ТӨЛЕМ ДЕТАЛЬДАРЫ**\n\nАударым сомасы: **{total} ₸**\n🏦 Kaspi Bank: `{kaspi}`\n\n📸 **Төлем чегін (скриншот немесе PDF) осы чатқа жіберіңіз.**\n\n*(Чексіз тапсырыс өңделмейді)*"
    },
    "uz": {
        "welcome": "👋 **Хуш келибсиз, {name}!**\n\nСиз ижтимоий тармоқларда ақлли ва хавфсиз ривожланиш хизматидасиз 🚀\n\n✨ **Биз нима қила оламиз?**\nБиз аккаунтларингиз ўсишига ёрдам берамиз. Бизнинг арсеналимизда фақат юқори тезлик ва ишончлиликни таъминлайдиган синовдан ўтган жаҳон серверлари мавжуд.\n\n🛡 **Хавфсизлик:** Бизга паролларингиз керак эмас — фақат профил ёки постга ҳавола кифоя.\n💎 **Сифат:** Тарифни ўзингиз танлайсиз — эконом стартдан тортиб, 365 кунгача кафолатланган премиум накруткагача.\n\n👇 Бошлаш учун қуйидаги ҳаракатни танланг:",
        "btn_start": "🚀 Ривожланишни бошлаш",
        "btn_about": "ℹ️ Биз ҳақимизда / Қандай ишлайди",
        "btn_lang": "🌍 Тилни ўзгартириш",
        "about_text": "ℹ️ **Бизнинг хизматимиз ҳақида**\n\n🛠 **Қандай қилиб буюртма бериш мумкин?**\n1. «Ривожланишни бошлаш» тугмасини босинг ва ижтимоий тармоқни танланг.\n2. Керакли хизмат ва сифат даражасини танланг.\n3. Миқдорни кўрсатинг ва аккаунтингиз/постингизга ҳавола юборинг.\n4. Kaspi орқали пул ўтказиб буюртмани тўланг ва ботга чек скриншотини юборинг.\n5. Администратор текширгандан сўнг буюртма автоматик равишда бошланади! 🚀\n\n💡 **Кафолат нима?**\nАгар сиз кафолатли хизматни танласангиз (масалан, 30 ёки 365 кун), обуначилар камайиб кетса, тизим йўқотилган миқдорни мутлақо бепул тиклайди.\n\n📞 **Қўллаб-қувватлаш:** Саволларингиз бўлса, биз билан боғланинг @davronbk7.",
        "btn_back": "⬅️ Орқага",
        "choose_plat": "📱 **Ривожлантириш учун ижтимоий тармоқни танланг:**",
        "choose_cat": "🎯 **Нимани кўпайтирамиз?**",
        "choose_pack": "⚙️ **Керакли пакетни (сифатни) танланг:**",
        "pack_info": "📦 Танланган пакет: **{name}**\n\n⏱ **Бошланиши:** {start}\n🚀 **Тезлик:** {speed}\n🛡 **Муддати:** {retention}\n\n🔢 **Керакли миқдорни кўрсатинг:**",
        "btn_cancel": "⬅️ Бекор қилиш",
        "link_req": "✅ Ажойиб!\n\n⚠ ДИҚҚАТ: АККАУНТИНГИЗ ОЧИҚ БЎЛИШИ КЕРАК\n\nБуюртмангиз: **{name}**\nМиқдори: **{vol} та**\nТўлов суммаси: **{total} ₸**\n\n🔗 **Ҳаволани юборинг** (профил ёки публикацияга):",
        "pay_req": "💳 **ТЎЛОВ ТАФСИЛОТЛАРИ**\n\nЎтказма суммаси: **{total} ₸**\n🏦 Kaspi Bank: `{kaspi}`\n\n📸 **Илтимос, тўлов чекини (скриншот ёки PDF) ушбу чатга юборинг.**\n\n*(Чексиз буюртма қабул қилинмайди)*"
    }
}

# ==========================================
# 2. ГЛОБАЛЬНАЯ БАЗА УСЛУГ (ИЗ ФАЙЛА)
# ==========================================
SERVICES = {
    "inst": {
        "name": "📸 Instagram",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "eco": {"id": "10146", "name": "🌱 Эконом (Без гарантии)", "rate": 0.375, "start": "0-1 час", "speed": "До 200k/день", "retention": "Возможны списания"},
                    "r30": {"id": "10131", "name": "🛡 Стандарт (Гарантия 30 дней)", "rate": 0.5278, "start": "0-2 часа", "speed": "До 20k/день", "retention": "Среднее (Месяц защиты)"},
                    "r365": {"id": "10143", "name": "💎 Вечные (Гарантия 365 дней)", "rate": 0.95, "start": "0-2 часа", "speed": "До 500k/день", "retention": "Высокое (Защита на год)"},
                    "unlim": {"id": "10085", "name": "👑 БЕЗЛИМИТ ВОССТАНОВЛЕНИЕ", "rate": 7.375, "start": "Мгновенно", "speed": "До 200k/день", "retention": "НАВСЕГДА (Бесконечная гарантия)"},
                    "prem": {"id": "5951", "name": "🔥 Premium Quality (Non Drop)", "rate": 5.235, "start": "0-24 часа", "speed": "До 5k/день", "retention": "Вечные (Без списаний)"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "eco": {"id": "5626", "name": "🌱 Эконом", "rate": 0.1375, "start": "0-1 час", "speed": "До 100k/день", "retention": "Могут списаться"},
                    "r365": {"id": "10066", "name": "💎 Вечные (Гарантия 365 дней)", "rate": 0.286, "start": "0-1 час", "speed": "До 20k/день", "retention": "Держатся стабильно"},
                    "power": {"id": "3476", "name": "🚀 POWER Likes (Высочайшее качество)", "rate": 0.7875, "start": "1 час", "speed": "До 5k/день", "retention": "Максимальное удержание"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Views)",
                "items": {
                    "video": {"id": "798", "name": "🔥 Видео / Reels", "rate": 0.0063, "start": "Мгновенно", "speed": "До 1 млн/день", "retention": "Пожизненно"},
                    "story": {"id": "312", "name": "📱 Истории (Story)", "rate": 0.0032, "start": "0-1 час", "speed": "До 100k/день", "retention": "На время истории"}
                }
            },
            "comments": {
                "name": "💬 Комментарии",
                "items": {
                    "rand": {"id": "112", "name": "💬 Случайные (Микс)", "rate": 4.375, "start": "0-3 часа", "speed": "До 25k/день", "retention": "30 дней защиты"},
                    "emoji": {"id": "5867", "name": "😍 Эмодзи (HQ Качество)", "rate": 3.125, "start": "0-6 часов", "speed": "До 1k/день", "retention": "Пожизненно (LIFETIME)"},
                    "custom": {"id": "3382", "name": "✍️ Свои тексты (Custom)", "rate": 11.25, "start": "1 час", "speed": "До 300/день", "retention": "Без списаний (NON-DROP)"},
                    "power": {"id": "5980", "name": "🔥 Power Comments (от 10k+ аккаунтов)", "rate": 4.80, "start": "0-1 час", "speed": "Быстро", "retention": "Супер-качество"}
                }
            },
            "stats": {
                "name": "📈 Статистика (Репосты/Охват)",
                "items": {
                    "reach": {"id": "1068", "name": "📊 Охват + Показы", "rate": 0.8125, "start": "0-1 час", "speed": "До 100k/день", "retention": "Не списываются"},
                    "saves": {"id": "448", "name": "📌 Сохранения", "rate": 0.20, "start": "0-1 час", "speed": "До 15k/день", "retention": "Не списываются"},
                    "shares": {"id": "584", "name": "🚀 Репосты (Shares)", "rate": 0.1775, "start": "0-1 час", "speed": "До 20k/день", "retention": "Не списываются"},
                    "profile": {"id": "8220", "name": "👤 Визиты профиля + Охват", "rate": 0.075, "start": "0-1 час", "speed": "До 50k/день", "retention": "Не списываются"}
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
                    "std": {"id": "6678", "name": "🌱 Базовые", "rate": 1.20, "start": "0-1 час", "speed": "До 10k/день", "retention": "Среднее удержание"},
                    "unlim": {"id": "8960", "name": "💎 БЕЗЛИМИТ ВОССТАНОВЛЕНИЕ", "rate": 4.50, "start": "0-2 часа", "speed": "До 5k/день", "retention": "НАВСЕГДА (Защита от списаний)"}
                }
            },
            "views": {
                "name": "👀 Просмотры",
                "items": {
                    "fast": {"id": "2211", "name": "🚀 Мгновенные", "rate": 0.002, "start": "Мгновенно", "speed": "Молниеносно", "retention": "Не списываются"}
                }
            }
        }
    },
    "yt": {
        "name": "▶️ YouTube",
        "cats": {
            "views": {
                "name": "👀 Просмотры (Views)",
                "items": {
                    "std": {"id": "7709", "name": "🌱 Стандартные просмотры", "rate": 1.50, "start": "0-6 часов", "speed": "До 10k/день", "retention": "Нормальное"},
                    "unlim": {"id": "8466", "name": "💎 LIFETIME (Вечные просмотры)", "rate": 1.175, "start": "0-4 часа", "speed": "До 5M/день", "retention": "Пожизненно (LIFETIME)"},
                    "rav": {"id": "3912", "name": "🔥 Уникальные RAV™ + Вовлеченность", "rate": 3.125, "start": "0-1 час", "speed": "До 2k/день", "retention": "90 дней (Высокое удержание)"},
                    "retention": {"id": "9254", "name": "⏱ Удержание 1-5 минут (External)", "rate": 1.75, "start": "0-2 часа", "speed": "До 2k/день", "retention": "Пожизненно"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "std": {"id": "7002", "name": "👍 Лайки на видео", "rate": 2.50, "start": "0-1 час", "speed": "Естественная", "retention": "Долгосрочные"}
                }
            }
        }
    },
    "fb": {
        "name": "📘 Facebook",
        "cats": {
            "subs": {
                "name": "👥 Подписчики и Лайки (Pages)",
                "items": {
                    "std": {"id": "6297", "name": "🌱 Лайки Страницы (Гарантия 30 дней)", "rate": 1.375, "start": "0-1 час", "speed": "До 5k/день", "retention": "30 дней"},
                    "prem": {"id": "1722", "name": "💎 Лайки Страницы (Вечные)", "rate": 1.025, "start": "0-8 часов", "speed": "До 500k/день", "retention": "Пожизненно (LIFETIME)"}
                }
            },
            "post_likes": {
                "name": "❤️ Лайки на посты",
                "items": {
                    "std": {"id": "4351", "name": "👍 Лайки (Гарантия 30 дней)", "rate": 0.475, "start": "0-1 час", "speed": "До 1k/день", "retention": "30 дней"},
                    "emoji": {"id": "225", "name": "❤️ Реакция LOVE (Эмодзи)", "rate": 1.00, "start": "1 час", "speed": "До 50k/день", "retention": "30 дней"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Видео/Reels)",
                "items": {
                    "reels": {"id": "357", "name": "📱 Facebook Reels Views", "rate": 0.0875, "start": "0-1 час", "speed": "До 200k/день", "retention": "Высокое"},
                    "video": {"id": "428", "name": "🔥 Просмотры Видео (3 Seconds)", "rate": 0.65, "start": "0-1 час", "speed": "До 500k/день", "retention": "Высокое"}
                }
            }
        }
    },
    "tg": {
        "name": "✈️ Telegram",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "std": {"id": "9378", "name": "🌱 Стандарт", "rate": 0.68, "start": "0-1 час", "speed": "До 500k/день", "retention": "Среднее удержание"},
                    "prem": {"id": "9382", "name": "💎 Премиум", "rate": 1.50, "start": "0-1 час", "speed": "До 50k/день", "retention": "Долгосрочные"}
                }
            }
        }
    }
}

# ==========================================
# 3. ИНТЕРФЕЙС И ЯЗЫКИ
# ==========================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"))
    kb.row(types.InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kk"))
    kb.row(types.InlineKeyboardButton(text="🇺🇿 Ўзбекча", callback_data="lang_uz"))
    
    await message.answer("🌍 Выберите язык / Тілді таңдаңыз / Тилни танланг:", reply_markup=kb.as_markup())

# Кнопка НАЗАД (Вернуться к выбору языка)
@dp.callback_query(F.data == "change_lang")
async def change_lang(callback: types.CallbackQuery, state: FSMContext):
    await cmd_start(callback.message, state)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    
    t = LANG_DICT[lang]
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text=t["btn_start"], callback_data="platforms"))
    kb.row(types.InlineKeyboardButton(text=t["btn_about"], callback_data="about"))
    kb.row(types.InlineKeyboardButton(text=t["btn_lang"], callback_data="change_lang"))
    
    # Подставляем имя пользователя в текст
    welcome_text = t['welcome'].format(name=callback.from_user.first_name)
    await callback.message.edit_text(welcome_text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "home")
async def go_home(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text=t["btn_start"], callback_data="platforms"))
    kb.row(types.InlineKeyboardButton(text=t["btn_about"], callback_data="about"))
    kb.row(types.InlineKeyboardButton(text=t["btn_lang"], callback_data="change_lang"))
    
    welcome_text = t['welcome'].format(name=callback.from_user.first_name)
    await callback.message.edit_text(welcome_text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text=t["btn_back"], callback_data="home"))
    await callback.message.edit_text(t["about_text"], reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "platforms")
async def show_platforms(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    kb = InlineKeyboardBuilder()
    buttons = [types.InlineKeyboardButton(text=p_data["name"], callback_data=f"p_{p_key}") for p_key, p_data in SERVICES.items()]
    for i in range(0, len(buttons), 2): kb.row(*buttons[i:i+2])
    kb.row(types.InlineKeyboardButton(text=t["btn_back"], callback_data="home"))
    
    await callback.message.edit_text(t["choose_plat"], reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("p_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    p_key = callback.data.split("_")[1]
    plat_data = SERVICES[p_key]
    
    kb = InlineKeyboardBuilder()
    buttons = [types.InlineKeyboardButton(text=c_data["name"], callback_data=f"c_{p_key}_{c_key}") for c_key, c_data in plat_data["cats"].items()]
    for i in range(0, len(buttons), 2): kb.row(*buttons[i:i+2])
    kb.row(types.InlineKeyboardButton(text=t["btn_back"], callback_data="platforms"))
    
    await callback.message.edit_text(f"**{plat_data['name']}**\n\n{t['choose_cat']}", reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("c_"))
async def choose_quality(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    _, p_key, c_key = callback.data.split("_")
    cat_data = SERVICES[p_key]["cats"][c_key]
    
    kb = InlineKeyboardBuilder()
    for q_key, q_data in cat_data["items"].items():
        kb.row(types.InlineKeyboardButton(text=q_data['name'], callback_data=f"q_{p_key}_{c_key}_{q_key}"))
        
    kb.row(types.InlineKeyboardButton(text=t["btn_back"], callback_data=f"p_{p_key}"))
    await callback.message.edit_text(t["choose_pack"], reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("q_"))
async def choose_volume(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    _, p_key, c_key, q_key = callback.data.split("_")
    service = SERVICES[p_key]["cats"][c_key]["items"][q_key]
    
    unit_price = (service["rate"] * USD_TO_KZT * PROFIT_FACTOR) / 1000
    
    await state.update_data(api_id=service["id"], s_name=service["name"], unit_price=unit_price)
    
    kb = InlineKeyboardBuilder()
    
    if unit_price < 0.1:
        volumes = [5000, 10000, 50000, 100000, 500000, 1000000]
    else:
        volumes = [100, 500, 1000, 2000, 5000, 10000]
    
    vol_buttons = []
    for vol in volumes:
        total = math.ceil(vol * unit_price)
        if total < 200: total = 200 
        vol_buttons.append(types.InlineKeyboardButton(text=f"🛒 {vol} — {total} ₸", callback_data=f"v_{vol}"))
        
    for i in range(0, len(vol_buttons), 2): kb.row(*vol_buttons[i:i+2])
    kb.row(types.InlineKeyboardButton(text=t["btn_cancel"], callback_data="platforms"))
    
    text = t["pack_info"].format(name=service['name'], start=service['start'], speed=service['speed'], retention=service['retention'])
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

# ==========================================
# 4. ОФОРМЛЕНИЕ И ОПЛАТА
# ==========================================

@dp.callback_query(F.data.startswith("v_"))
async def request_link(callback: types.CallbackQuery, state: FSMContext):
    vol = int(callback.data.split("_")[1])
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    total = math.ceil(vol * data["unit_price"])
    if total < 200: total = 200
    
    await state.update_data(vol=vol, total=total)
    
    text = t["link_req"].format(name=data['s_name'], vol=vol, total=total)
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(OrderProcess.waiting_for_link)

@dp.message(OrderProcess.waiting_for_link)
async def request_receipt(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    text = t["pay_req"].format(total=data['total'], kaspi=KASPI_NUMBER)
    await message.answer(text, parse_mode="Markdown")
    await state.set_state(OrderProcess.waiting_for_receipt)

@dp.message(OrderProcess.waiting_for_receipt, F.photo | F.document)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user
    
    file_id = message.document.file_id if message.document else message.photo[-1].file_id
    callback_payload = f"{data['api_id']}_{data['vol']}_{user.id}"
    
    admin_text = (
        f"⚠️ АВТОРИЗАЦИЯ ЗАКАЗА\n"
        f"От: @{user.username} (ID: {user.id})\n"
        f"Услуга: {data['s_name']} (API: {data['api_id']})\n"
        f"Кол-во: {data['vol']}\n"
        f"Сумма: {data['total']} ₸\n\n"
        f"🔗 Ссылка:\n{data['link']}"
    )
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="✅ ЗАПУСТИТЬ", callback_data=f"ok_{callback_payload}"))
    kb.row(types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"no_{user.id}"))
    
    if message.document: await bot.send_document(ADMIN_ID, file_id, caption=admin_text, reply_markup=kb.as_markup())
    else: await bot.send_photo(ADMIN_ID, file_id, caption=admin_text, reply_markup=kb.as_markup())
        
    await message.answer("⏳ Чек отправлен админу. Ожидайте запуска!")
    await state.clear()

# ==========================================
# 5. АДМИН ПАНЕЛЬ
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
        
        api_data = {'key': JAP_API_KEY, 'action': 'add', 'service': api_id, 'link': link, 'quantity': vol}
        response = requests.post(JAP_URL, data=api_data).json()
        
        if "order" in response:
            await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🟢 [УСПЕХ. ЗАКАЗ ID: {response['order']}]")
            await bot.send_message(int(user_id), f"🎉 Оплата подтверждена! Заказ запущен (ID: {response['order']}).")
        else:
            await callback.message.answer(f"Ошибка JAP: {response.get('error', 'Unknown')}", show_alert=True)
    except Exception as e:
        await callback.message.answer(f"Сбой: {e}", show_alert=True)

@dp.callback_query(F.data.startswith("no_"))
async def admin_reject(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🔴 [ОТКЛОНЕН]")
    await bot.send_message(int(user_id), "❌ Чек отклонен. Обратитесь в поддержку.")

async def main():
    logging.info("Система работает.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
