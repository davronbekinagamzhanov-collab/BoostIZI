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
PEAKERR_API_KEY = "1bb6159c63783fb2a77f693b6844428d"
PEAKERR_URL = "https://peakerr.com/api/v2"

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
# СЛОВАРИ ПЕРЕВОДОВ 
# ==========================================
LANG_DICT = {
    "ru": {
        "welcome": "👋 **Добро пожаловать, {name}!**\n\nВы находитесь в сервисе умного и безопасного продвижения в социальных сетях 🚀\n\n✨ **Что мы умеем?**\nМы помогаем вашим аккаунтам расти. В нашем арсенале только проверенные мировые серверы, обеспечивающие высокую скорость и надежность.\n\n🛡 **Безопасность:** Нам не нужны ваши пароли — только ссылка на профиль или пост.\n💎 **Качество:** Вы сами выбираете тариф — от экономного старта до премиум-накрутки с пожизненной гарантией (Lifetime).\n\n👇 Выберите действие ниже, чтобы начать:",
        "btn_start": "🚀 Начать продвижение",
        "btn_about": "ℹ️ О нас / Как это работает",
        "btn_lang": "🌍 Выбрать язык",
        "about_text": "ℹ️ **О нашем сервисе**\n\n🛠 **Как сделать заказ?**\n1. Нажмите «Начать продвижение» и выберите соцсеть.\n2. Выберите нужную услугу и уровень качества.\n3. Укажите объем и отправьте ссылку на ваш аккаунт/пост.\n4. Оплатите заказ переводом на Kaspi и отправьте боту скриншот чека.\n5. После проверки администратором заказ запустится автоматически! 🚀\n\n💡 **Что такое гарантия?**\nЕсли вы выбрали услугу с гарантией (например, Lifetime или 365 дней), то в случае отписок система восстановит потери абсолютно бесплатно.\n\n📞 **Поддержка:** Если возникли вопросы, свяжитесь с нами @davronbk7.",
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
# 2. ГЛОБАЛЬНАЯ БАЗА УСЛУГ (ПРОСТЫЕ И ПОНЯТНЫЕ НАЗВАНИЯ)
# ==========================================
SERVICES = {
    "inst": {
        "name": "📸 Instagram",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "eco": {"id": "29641", "name": "🌱 Самые дешевые (Без гарантии, возможны отписки)", "rate": 0.54, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Возможны списания"},
                    "r30": {"id": "29642", "name": "🛡 Стандартные (С гарантией восстановления 30 дней)", "rate": 0.67, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Месяц защиты"},
                    "r365": {"id": "28039", "name": "💎 Премиум (Гарантия от списаний на целый год)", "rate": 1.06, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Защита на год"},
                    "unlim": {"id": "29483", "name": "👑 VIP качество (Пожизненная гарантия восстановления)", "rate": 0.81, "start": "Мгновенно", "speed": "До 500k/день", "retention": "НАВСЕГДА (Lifetime)"},
                    "prem": {"id": "29524", "name": "🔥 Самые лучшие (Живые аккаунты, Без списаний)", "rate": 0.90, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненная гарантия"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "eco": {"id": "29653", "name": "🌱 Простые лайки (Самые дешевые, без гарантии)", "rate": 0.12, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Могут списаться"},
                    "r30": {"id": "27958", "name": "🛡 Надежные лайки (Гарантия 30 дней)", "rate": 0.14, "start": "Мгновенно", "speed": "До 100k/день", "retention": "30 дней"},
                    "r365": {"id": "29629", "name": "💎 Премиум лайки (Не списываются, гарантия год)", "rate": 0.16, "start": "Мгновенно", "speed": "До 200k/день", "retention": "1 Год защиты"},
                    "power": {"id": "29442", "name": "🚀 Мощные лайки (От реальных людей с фото)", "rate": 0.09, "start": "Мгновенно", "speed": "До 20k/день", "retention": "Пожизненно (Lifetime)"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Views)",
                "items": {
                    "video": {"id": "29004", "name": "🔥 Просмотры Видео / Reels (Молниеносные)", "rate": 0.025, "start": "Мгновенно", "speed": "Молниеносно", "retention": "Пожизненно"},
                    "cheap": {"id": "27050", "name": "📉 Простые просмотры (Самая низкая цена)", "rate": 0.002, "start": "Мгновенно", "speed": "До 100M/день", "retention": "Без списаний"},
                    "reach": {"id": "25019", "name": "📈 Просмотры + Охват (Для выхода в ТОП)", "rate": 0.12, "start": "Мгновенно", "speed": "До 500K/час", "retention": "Пожизненно"}
                }
            },
            "comments": {
                "name": "💬 Комментарии",
                "items": {
                    "rand": {"id": "29487", "name": "💬 Случайные комментарии (От живых людей)", "rate": 0.68, "start": "0-3 часа", "speed": "До 100k/день", "retention": "30 дней защиты"},
                    "custom": {"id": "29491", "name": "✍️ Ваш текст комментариев (Напишите сами)", "rate": 0.93, "start": "0-7 часов", "speed": "До 100k/день", "retention": "30 дней защиты"},
                    "power": {"id": "26743", "name": "🔥 VIP Комментарии (От популярных аккаунтов)", "rate": 3.75, "start": "Мгновенно", "speed": "До 1K/день", "retention": "Супер-качество"}
                }
            },
            "stats": {
                "name": "📈 Статистика (Репосты/Сохранения)",
                "items": {
                    "saves": {"id": "26988", "name": "📌 Сохранения публикаций (Улучшает статистику)", "rate": 0.06, "start": "0-10 минут", "speed": "До 2k/день", "retention": "Не списываются"},
                    "shares": {"id": "29247", "name": "🚀 Репосты ваших записей", "rate": 0.26, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"},
                    "profile": {"id": "29200", "name": "👤 Увеличение охвата и показов профиля", "rate": 0.07, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"}
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
                    "eco": {"id": "29820", "name": "🌱 Простые подписчики (Самые дешевые)", "rate": 0.51, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Среднее удержание"},
                    "std": {"id": "29969", "name": "🛡 Качественные (Гарантия восстановления 30 дней)", "rate": 1.75, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Защита 30 дней"},
                    "unlim": {"id": "28185", "name": "💎 Лучшие подписчики (Пожизненная гарантия)", "rate": 0.92, "start": "Мгновенно", "speed": "До 200k/день", "retention": "НАВСЕГДА (Auto Refill)"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "eco": {"id": "28171", "name": "🌱 Простые лайки (Самая низкая цена)", "rate": 0.02, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненно"},
                    "prem": {"id": "26305", "name": "💎 Качественные лайки (От живых аккаунтов)", "rate": 0.07, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненно"},
                    "power": {"id": "28160", "name": "🚀 VIP Лайки (Никогда не списываются)", "rate": 0.14, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненно"}
                }
            },
            "views": {
                "name": "👀 Просмотры / Репосты",
                "items": {
                    "fast": {"id": "29549", "name": "🚀 Очень быстрые просмотры", "rate": 0.006, "start": "Мгновенно", "speed": "Молниеносно", "retention": "Не списываются"},
                    "unlim": {"id": "25997", "name": "💎 Качественные просмотры (Навсегда)", "rate": 0.016, "start": "Мгновенно", "speed": "До 5M/день", "retention": "Пожизненно"},
                    "saves": {"id": "28136", "name": "📌 Сохранения видео (Для рекомендаций)", "rate": 0.007, "start": "Мгновенно", "speed": "До 100K/день", "retention": "Пожизненно"},
                    "share": {"id": "29453", "name": "🚀 Репосты вашего видео", "rate": 0.016, "start": "Мгновенно", "speed": "До 500K/день", "retention": "Пожизненно"}
                }
            },
            "live": {
                "name": "🔴 Прямые трансляции (Live)",
                "items": {
                    "min15": {"id": "27534", "name": "👁 Зрители на стрим (15 минут)", "rate": 0.68, "start": "Мгновенно", "speed": "Сразу", "retention": "15 минут"},
                    "min60": {"id": "27536", "name": "👁 Зрители на стрим (1 час)", "rate": 2.75, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"},
                    "comments": {"id": "27965", "name": "💬 Ваши комментарии прямо в прямой эфир", "rate": 0.56, "start": "Мгновенно", "speed": "Быстро", "retention": "Во время Live"}
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
                    "std": {"id": "28864", "name": "🌱 Обычные подписчики (Гарантия 3 месяца)", "rate": 0.98, "start": "Мгновенно", "speed": "До 100k/день", "retention": "90 дней защиты"},
                    "prem": {"id": "29546", "name": "💎 100% Живые люди (Никогда не отпишутся)", "rate": 0.63, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Пожизненная защита"},
                    "vip": {"id": "28457", "name": "🚀 Премиум подписчики Telegram (С просмотрами)", "rate": 3.60, "start": "Мгновенно", "speed": "Быстро", "retention": "7 Дней Non Drop"}
                }
            },
            "views": {
                "name": "👀 Просмотры постов",
                "items": {
                    "post1": {"id": "15972", "name": "👁 Просмотры на 1 последний пост", "rate": 0.015, "start": "Мгновенно", "speed": "Молниеносно", "retention": "Не списываются"},
                    "post5": {"id": "28479", "name": "💎 Просмотры сразу на 5 последних постов", "rate": 0.50, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"}
                }
            },
            "reacts": {
                "name": "🔥 Реакции",
                "items": {
                    "pos": {"id": "28576", "name": "👍 Позитивные реакции (Микс + Просмотры)", "rate": 0.02, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"},
                    "like": {"id": "23335", "name": "👍 Реакция Лайк (Навсегда)", "rate": 0.03, "start": "Мгновенно", "speed": "Быстро", "retention": "Пожизненно"}
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
                    "vip": {"id": "27929", "name": "💎 VIP Подписчики (Самое высокое качество, Навсегда)", "rate": 33.62, "start": "В течение дня", "speed": "Естественная", "retention": "Пожизненно (Auto Refill)"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Views)",
                "items": {
                    "native": {"id": "28692", "name": "🌱 Настоящие просмотры (От реальных людей)", "rate": 0.93, "start": "0-4 часа", "speed": "До 200k/день", "retention": "Пожизненно"},
                    "vip": {"id": "27906", "name": "💎 VIP Просмотры (С гарантией навсегда)", "rate": 1.28, "start": "0-4 часа", "speed": "До 2k/день", "retention": "Пожизненно"},
                    "retention": {"id": "27909", "name": "⏱ Просмотры с долгим удержанием (Смотрят видео)", "rate": 3.43, "start": "0-4 часа", "speed": "До 2k/день", "retention": "Пожизненно"}
                }
            },
            "likes": {
                "name": "❤️ Лайки / Комменты",
                "items": {
                    "like": {"id": "27930", "name": "👍 Лайки на видео (Никогда не пропадают)", "rate": 0.52, "start": "0-1 час", "speed": "Быстро", "retention": "Пожизненно"},
                    "comment": {"id": "28756", "name": "💬 Ваши личные комментарии под видео", "rate": 3.00, "start": "1 час", "speed": "Быстро", "retention": "Пожизненно"}
                }
            },
            "live": {
                "name": "🔴 Прямые трансляции (Live)",
                "items": {
                    "min15": {"id": "27517", "name": "👁 Зрители на прямой эфир (15 минут)", "rate": 0.31, "start": "Мгновенно", "speed": "Сразу", "retention": "15 минут"},
                    "min60": {"id": "27519", "name": "👁 Зрители на прямой эфир (1 час)", "rate": 1.25, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"}
                }
            }
        }
    },
    "fb": {
        "name": "📘 Facebook",
        "cats": {
            "subs": {
                "name": "👥 Подписчики и Страницы",
                "items": {
                    "page": {"id": "29815", "name": "🌱 Лайки на Страницу + Подписчики", "rate": 0.37, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Пожизненно (Lifetime)"},
                    "prof": {"id": "29444", "name": "💎 Подписчики на личный профиль (Гарантия месяц)", "rate": 0.10, "start": "Мгновенно", "speed": "До 300k/день", "retention": "30 дней"}
                }
            },
            "likes": {
                "name": "❤️ Лайки / Реакции",
                "items": {
                    "std": {"id": "29582", "name": "👍 Лайки на пост или фото (Навсегда)", "rate": 0.17, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Пожизненно"},
                    "love": {"id": "29631", "name": "❤️ Реакция Супер (Сердечко)", "rate": 0.09, "start": "Мгновенно", "speed": "До 10k/день", "retention": "Держатся стабильно"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Видео/Live)",
                "items": {
                    "video": {"id": "29449", "name": "📱 Просмотры видео и Reels (Навсегда)", "rate": 0.02, "start": "Мгновенно", "speed": "До 30k/день", "retention": "Пожизненно"},
                    "live": {"id": "29051", "name": "🔴 Зрители на прямой эфир (1 час)", "rate": 4.56, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"}
                }
            }
        }
    },
    "tw": {
        "name": "🐦 Twitter (X)",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "std": {"id": "15030", "name": "🌱 Надежные подписчики", "rate": 3.68, "start": "0-30 минут", "speed": "Быстро", "retention": "Долгосрочные"}
                }
            },
            "views": {
                "name": "👀 Просмотры постов",
                "items": {
                    "std": {"id": "29865", "name": "📱 Просмотры твитов и видео", "rate": 0.005, "start": "Мгновенно", "speed": "До 2M/день", "retention": "Пожизненно (Lifetime)"}
                }
            }
        }
    },
    "spot": {
        "name": "🎧 Spotify",
        "cats": {
            "views": {
                "name": "🎵 Прослушивания",
                "items": {
                    "std": {"id": "28251", "name": "🔥 Прослушивания треков (Premium качество)", "rate": 0.91, "start": "Мгновенно", "speed": "До 1k/день", "retention": "Не списываются"}
                }
            }
        }
    },
    "twitch": {
        "name": "👾 Twitch",
        "cats": {
            "live": {
                "name": "🔴 Зрители на трансляцию",
                "items": {
                    "min60": {"id": "21850", "name": "👁 Зрители на стрим (1 час)", "rate": 2.20, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"}
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
        f"⚠️ АВТОРИЗАЦИЯ ЗАКАЗА (Платформа Peakerr)\n"
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
# 5. АДМИН ПАНЕЛЬ (ПОДКЛЮЧЕНО К PEAKERR)
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
        
        api_data = {'key': PEAKERR_API_KEY, 'action': 'add', 'service': api_id, 'link': link, 'quantity': vol}
        response = requests.post(PEAKERR_URL, data=api_data).json()
        
        if "order" in response:
            await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🟢 [УСПЕХ. ЗАКАЗ ID: {response['order']}]")
            await bot.send_message(int(user_id), f"🎉 Оплата подтверждена! Заказ запущен (ID: {response['order']}).")
        else:
            await callback.message.answer(f"Ошибка Peakerr: {response.get('error', 'Unknown')}", show_alert=True)
    except Exception as e:
        await callback.message.answer(f"Сбой: {e}", show_alert=True)

@dp.callback_query(F.data.startswith("no_"))
async def admin_reject(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🔴 [ОТКЛОНЕН]")
    await bot.send_message(int(user_id), "❌ Чек отклонен. Обратитесь в поддержку.")

async def main():
    logging.info("Система работает на Peakerr API.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
