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
# СЛОВАРИ ПЕРЕВОДОВ (С ЖЕСТКИМИ ПРЕДУПРЕЖДЕНИЯМИ)
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
        "pack_info": "📦 Выбранный пакет: **{name}**\n\nℹ️ **ОПИСАНИЕ И ГАРАНТИЯ:**\n_{desc}_\n\n⏱ **Время старта:** {start}\n🚀 **Скорость накрутки:** {speed}\n🛡 **Срок / Удержание:** {retention}\n\n🔢 **Укажите желаемый объем:**",
        "btn_cancel": "⬅️ Отмена",
        "link_req": "✅ Отлично! Ваш заказ сформирован.\n\n🚨 **ВНИМАНИЕ! СТРОГИЕ ПРАВИЛА:**\n1. Ваш профиль должен быть **ОТКРЫТЫМ** до полного завершения накрутки.\n2. Ссылка должна быть **на 100% правильной** (скопируйте её из приложения).\n📌 *Если вы скинете неверную ссылку, текст вместо ссылки или ваш профиль будет закрыт — система всё равно спишет деньги, накрутка не придет, и средства ВОЗВРАТУ НЕ ПОДЛЕЖАТ. Это ваша зона ответственности.*\n\nВаш заказ: **{name}**\nОбъем: **{vol} шт.**\nСумма к оплате: **{total} ₸**\n\n🔗 **Если всё понятно и вы согласны, отправьте правильную ссылку ответным сообщением:**",
        "pay_req": "💳 **ДЕТАЛИ ОПЛАТЫ**\n\nК переводу: **{total} ₸**\n🏦 Kaspi Bank: `{kaspi}`\n\n🚨 **ВНИМАНИЕ! СТРОГОЕ ПРАВИЛО:**\nПереводите **ТОЧНУЮ СУММУ**, указанную выше. Если вы переведете меньше или больше (даже на 1 тенге), система автоматически отклонит заказ. **В этом случае деньги ВОЗВРАТУ НЕ ПОДЛЕЖАТ!** Будьте внимательны.\n\n📸 **Отправьте скриншот или PDF-чек об оплате в этот чат.**",
        "wait_msg": "⏳ Чек отправлен! Администратор проверяет оплату.\n📞 Техподдержка: @davronbk7",
        "success_msg": "🎉 Оплата подтверждена! Заказ успешно запущен в работу (ID: {order_id}).\n📞 Связь с поддержкой: @davronbk7",
        "reject_msg": "❌ **К сожалению, ваш заказ не принят.**\n\nПричина: {reason}\n📞 Напишите в поддержку для решения проблемы: @davronbk7",
        "need_photo": "⚠️ Пожалуйста, отправьте именно ФОТО или PDF документ с чеком, а не текст.",
        "reasons": {
            "1": "Оплата не поступила на счет.",
            "2": "Неверная сумма перевода.",
            "3": "Загруженный файл не является действительным банковским чеком."
        }
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
        "pack_info": "📦 Таңдалған пакет: **{name}**\n\nℹ️ **СИПАТТАМА ЖӘНЕ КЕПІЛДІК:**\n_{desc}_\n\n⏱ **Басталуы:** {start}\n🚀 **Жылдамдық:** {speed}\n🛡 **Мерзімі:** {retention}\n\n🔢 **Қажетті көлемді көрсетіңіз:**",
        "btn_cancel": "⬅️ Болдырмау",
        "link_req": "✅ Керемет! Тапсырыс жасалды.\n\n🚨 **НАЗАР АУДАРЫҢЫЗ! ҚАТАҢ ЕРЕЖЕЛЕР:**\n1. Профиліңіз **АШЫҚ** болуы тиіс.\n2. Сілтеме **100% дұрыс** болуы керек (қосымшадан көшіріп алыңыз).\n📌 *Егер профиль жабық болса немесе сілтеме қате болса — жүйе ақшаны ұстап қалады, қызмет орындалмайды және ақша ҚАЙТАРЫЛМАЙДЫ. Бұл толығымен сіздің жауапкершілігіңіз.*\n\nТапсырыс: **{name}**\nКөлемі: **{vol} шт.**\nТөлем сомасы: **{total} ₸**\n\n🔗 **Егер бәрі түсінікті болса және келіссеңіз, дұрыс сілтемені жіберіңіз:**",
        "pay_req": "💳 **ТӨЛЕМ ДЕТАЛЬДАРЫ**\n\nАударым сомасы: **{total} ₸**\n🏦 Kaspi Bank: `{kaspi}`\n\n🚨 **НАЗАР АУДАРЫҢЫЗ! ҚАТАҢ ЕРЕЖЕ:**\nТек жоғарыда көрсетілген **НАҚТЫ СОМАНЫ** аударыңыз. Егер сома аз немесе көп болса (тіпті 1 теңгеге), тапсырыс автоматты түрде қабылданбайды. **Бұл жағдайда ақша ҚАЙТАРЫЛМАЙДЫ!** Мұқият болыңыз.\n\n📸 **Төлем чегін (скриншот немесе PDF) осы чатқа жіберіңіз.**",
        "wait_msg": "⏳ Чек жіберілді! Әкімші төлемді тексеруде.\n📞 Қолдау қызметі: @davronbk7",
        "success_msg": "🎉 Төлем расталды! Тапсырыс сәтті басталды (ID: {order_id}).\n📞 Қолдау қызметі: @davronbk7",
        "reject_msg": "❌ **Өкінішке орай, сіздің тапсырысыңыз қабылданбады.**\n\nСебебі: {reason}\n📞 Мәселені шешу үшін қолдау қызметіне жазыңыз: @davronbk7",
        "need_photo": "⚠️ Өтініш, текст емес, чек ФОТОСЫН немесе PDF құжатын жіберіңіз.",
        "reasons": {
            "1": "Төлем шотқа түспеді.",
            "2": "Аударым сомасы қате.",
            "3": "Жүктелген файл банк чегі емес."
        }
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
        "pack_info": "📦 Танланган пакет: **{name}**\n\nℹ️ **ТАВСИФИ ВА КАФОЛАТ:**\n_{desc}_\n\n⏱ **Бошланиши:** {start}\n🚀 **Тезлик:** {speed}\n🛡 **Муддати:** {retention}\n\n🔢 **Керакли миқдорни кўрсатинг:**",
        "btn_cancel": "⬅️ Бекор қилиш",
        "link_req": "✅ Ажойиб! Буюртмангиз шакллантирилди.\n\n🚨 **ДИҚҚАТ! ҚАТЪИЙ ҚОИДАЛАР:**\n1. Профилингиз **ОЧИҚ** бўлиши керак.\n2. Ҳавола **100% тўғри** бўлиши шарт.\n📌 *Агар профил ёпиқ бўлса ёки ҳавола нотўғри бўлса — тизим пулни ечиб олади, хизмат бажарилмайди ва пул ҚАЙТАРИЛМАЙДИ. Бу тўлиқ сизнинг жавобгарлигингиз.*\n\nБуюртма: **{name}**\nМиқдори: **{vol} та**\nТўлов суммаси: **{total} ₸**\n\n🔗 **Агар ҳаммаси тушунарли бўлса, тўғри ҳаволани юборинг:**",
        "pay_req": "💳 **ТЎЛОВ ТАФСИЛОТЛАРИ**\n\nЎтказма суммаси: **{total} ₸**\n🏦 Kaspi Bank: `{kaspi}`\n\n🚨 **ДИҚҚАТ! ҚАТЪИЙ ҚОИДА:**\nФақат юқорида кўрсатилган **АНИҚ СУММАНИ** ўтказинг. Агар сумма кам ёки кўп бўлса (ҳатто 1 тенгега), буюртма автоматик равишда рад этилади. **Бу ҳолатда пул ҚАЙТАРИЛМАЙДИ!** Эътиборли бўлинг.\n\n📸 **Илтимос, тўлов чекини (скриншот ёки PDF) ушбу чатга юборинг.**",
        "wait_msg": "⏳ Чек юборилди! Администратор тўловни текширмоқда.\n📞 Қўллаб-қувватлаш: @davronbk7",
        "success_msg": "🎉 Тўлов тасдиқланди! Буюртма ишга туширилди (ID: {order_id}).\n📞 Қўллаб-қувватлаш: @davronbk7",
        "reject_msg": "❌ **Афсуски, буюртмангиз қабул қилинмади.**\n\nСабаби: {reason}\n📞 Муаммони ҳал қилиш учун қўллаб-қувватлаш хизматига ёзинг: @davronbk7",
        "need_photo": "⚠️ Илтимос, матн эмас, чек ФОТОСУ ёки PDF ҳужжатини юборинг.",
        "reasons": {
            "1": "Тўлов ҳисобга келиб тушмади.",
            "2": "Сумма нотўғри.",
            "3": "Юкланган файл банк чеки эмас."
        }
    }
}

# ==========================================
# 2. ГЛОБАЛЬНАЯ БАЗА УСЛУГ (БЕЗ ИЗМЕНЕНИЙ)
# ==========================================
SERVICES = {
    "inst": {
        "name": "📸 Instagram",
        "cats": {
            "subs": {
                "name": "👥 Подписчики",
                "items": {
                    "eco": {"id": "29641", "name": "🌱 Самые дешевые (Без гарантии, возможны отписки)", "desc": "⚠️ Внимание: Выполняется ботами или старыми пустыми аккаунтами. Алгоритмы соцсетей могут списать их. Гарантии восстановления нет. Заказывайте на свой страх и риск.", "rate": 0.54, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Возможны списания"},
                    "r30": {"id": "29642", "name": "🛡 Стандартные (С гарантией восстановления 30 дней)", "desc": "✅ Качественные аккаунты. В случае отписок наша система абсолютно бесплатно восстановит их обратно в течение 30 дней.", "rate": 0.67, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Месяц защиты"},
                    "r365": {"id": "28039", "name": "💎 Премиум (Гарантия от списаний на целый год)", "desc": "💎 Максимально стабильная база. Списаний крайне мало, а если и будут — мы будем восстанавливать их бесплатно на протяжении 365 дней.", "rate": 1.06, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Защита на год"},
                    "unlim": {"id": "29483", "name": "👑 VIP качество (Пожизненная гарантия восстановления)", "desc": "👑 Лучшее, что есть на рынке! Вы покупаете один раз, и если Инстаграм когда-либо удалит этих подписчиков, система вернет их бесплатно навсегда (Lifetime).", "rate": 0.81, "start": "Мгновенно", "speed": "До 500k/день", "retention": "НАВСЕГДА (Lifetime)"},
                    "prem": {"id": "29524", "name": "🔥 Самые лучшие (Живые аккаунты, Без списаний)", "desc": "🔥 100% Живые аккаунты с аватарками и своими постами. Алгоритм не видит разницы между ними и вашими реальными друзьями.", "rate": 0.90, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненная гарантия"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "eco": {"id": "29653", "name": "🌱 Простые лайки (Самые дешевые, без гарантии)", "desc": "⚠️ Дешевые лайки от системных аккаунтов. Без гарантии, Инстаграм может их удалить при обновлении.", "rate": 0.12, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Могут списаться"},
                    "r30": {"id": "27958", "name": "🛡 Надежные лайки (Гарантия 30 дней)", "desc": "✅ Стабильные лайки от хороших аккаунтов. Если спишут, восстановим в течение 30 дней.", "rate": 0.14, "start": "Мгновенно", "speed": "До 100k/день", "retention": "30 дней"},
                    "r365": {"id": "29629", "name": "💎 Премиум лайки (Не списываются, гарантия год)", "desc": "💎 Качественные лайки, которые мертвой хваткой остаются на публикациях. Гарантия восстановления — 1 год.", "rate": 0.16, "start": "Мгновенно", "speed": "До 200k/день", "retention": "1 Год защиты"},
                    "power": {"id": "29442", "name": "🚀 Мощные лайки (От реальных людей с фото)", "desc": "🚀 Так называемые Power Likes от реальных пользователей. Идеально подходят для вывода вашего поста в ТОП и рекомендации.", "rate": 0.09, "start": "Мгновенно", "speed": "До 20k/день", "retention": "Пожизненно (Lifetime)"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Views)",
                "items": {
                    "video": {"id": "29004", "name": "🔥 Просмотры Видео / Reels (Молниеносные)", "desc": "🔥 Очень быстрые просмотры для ваших Reels и видео. Помогают создать вирусный эффект.", "rate": 0.025, "start": "Мгновенно", "speed": "Молниеносно", "retention": "Пожизненно"},
                    "cheap": {"id": "27050", "name": "📉 Простые просмотры (Самая низкая цена)", "desc": "📉 Большой объем по копеечной цене. Без гарантий, но отлично работает для массовости.", "rate": 0.002, "start": "Мгновенно", "speed": "До 100M/день", "retention": "Без списаний"},
                    "reach": {"id": "25019", "name": "📈 Просмотры + Охват (Для выхода в ТОП)", "desc": "📈 Умная услуга: алгоритм не только крутит просмотры, но и улучшает внутреннюю статистику (Охват), что продвигает вас в алгоритмах.", "rate": 0.12, "start": "Мгновенно", "speed": "До 500K/час", "retention": "Пожизненно"}
                }
            },
            "comments": {
                "name": "💬 Комментарии",
                "items": {
                    "rand": {"id": "29487", "name": "💬 Случайные комментарии (От живых людей)", "desc": "💬 Позитивные комментарии по тематике от качественных живых аккаунтов.", "rate": 0.68, "start": "0-3 часа", "speed": "До 100k/день", "retention": "30 дней защиты"},
                    "custom": {"id": "29491", "name": "✍️ Ваш текст комментариев (Напишите сами)", "desc": "✍️ После заказа скиньте ссылку, и мы накрутим любые ваши фразы и слова с качественных аккаунтов.", "rate": 0.93, "start": "0-7 часов", "speed": "До 100k/день", "retention": "30 дней защиты"},
                    "power": {"id": "26743", "name": "🔥 VIP Комментарии (От популярных аккаунтов)", "desc": "🔥 Комментарии от мощных, прокачанных страниц, которые сразу привлекают внимание к вашему профилю.", "rate": 3.75, "start": "Мгновенно", "speed": "До 1K/день", "retention": "Супер-качество"}
                }
            },
            "stats": {
                "name": "📈 Статистика (Репосты/Сохранения)",
                "items": {
                    "saves": {"id": "26988", "name": "📌 Сохранения публикаций (Улучшает статистику)", "desc": "📌 Инстаграм продвигает посты, которые часто сохраняют. Это лучшая инвестиция в алгоритм.", "rate": 0.06, "start": "0-10 минут", "speed": "До 2k/день", "retention": "Не списываются"},
                    "shares": {"id": "29247", "name": "🚀 Репосты ваших записей", "desc": "🚀 Имитация вирусности. Системные аккаунты будут массово делиться вашим Reels или постом.", "rate": 0.26, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"},
                    "profile": {"id": "29200", "name": "👤 Увеличение охвата и показов профиля", "desc": "👤 Прокачивает внутреннюю (теневую) статистику аккаунта для бизнес-страниц.", "rate": 0.07, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"}
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
                    "eco": {"id": "29820", "name": "🌱 Простые подписчики (Самые дешевые)", "desc": "⚠️ Выполняется ботами. ТикТок очень жестко их блокирует. Возможны огромные списания. Гарантии нет.", "rate": 0.51, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Среднее удержание"},
                    "std": {"id": "29969", "name": "🛡 Качественные (Гарантия восстановления 30 дней)", "desc": "✅ Отличный старт. Если алгоритм ТикТока удалит подписчиков в течение месяца, мы бесплатно докрутим новых.", "rate": 1.75, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Защита 30 дней"},
                    "unlim": {"id": "28185", "name": "💎 Лучшие подписчики (Пожизненная гарантия)", "desc": "💎 Самое топовое предложение! Покупаете один раз, и мы следим за вашим числом подписчиков всегда. Упало - восстановим.", "rate": 0.92, "start": "Мгновенно", "speed": "До 200k/день", "retention": "НАВСЕГДА (Auto Refill)"}
                }
            },
            "likes": {
                "name": "❤️ Лайки",
                "items": {
                    "eco": {"id": "28171", "name": "🌱 Простые лайки (Самая низкая цена)", "desc": "⚠️ Очень дешево, но накручивается с пустых аккаунтов. ТикТок может их списать.", "rate": 0.02, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненно"},
                    "prem": {"id": "26305", "name": "💎 Качественные лайки (От живых аккаунтов)", "desc": "💎 Лайки с оформленных страниц, которые остаются под вашим видео навсегда.", "rate": 0.07, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненно"},
                    "power": {"id": "28160", "name": "🚀 VIP Лайки (Никогда не списываются)", "desc": "🚀 Идеально для вывода видео в реки. Максимальная защита от отписок ТикТока.", "rate": 0.14, "start": "Мгновенно", "speed": "До 200k/день", "retention": "Пожизненно"}
                }
            },
            "views": {
                "name": "👀 Просмотры / Репосты",
                "items": {
                    "fast": {"id": "29549", "name": "🚀 Очень быстрые просмотры", "desc": "🚀 Залейте просмотры на видео, чтобы оно выглядело популярным. Идут моментально.", "rate": 0.006, "start": "Мгновенно", "speed": "Молниеносно", "retention": "Не списываются"},
                    "unlim": {"id": "25997", "name": "💎 Качественные просмотры (Навсегда)", "desc": "💎 Просмотры, которые 100% не спишутся и останутся на вашей статистике навсегда.", "rate": 0.016, "start": "Мгновенно", "speed": "До 5M/день", "retention": "Пожизненно"},
                    "saves": {"id": "28136", "name": "📌 Сохранения видео (Для рекомендаций)", "desc": "📌 Один из важнейших параметров для алгоритма TikTok: чем больше сохранений, тем чаще видео в реках.", "rate": 0.007, "start": "Мгновенно", "speed": "До 100K/день", "retention": "Пожизненно"},
                    "share": {"id": "29453", "name": "🚀 Репосты вашего видео", "desc": "🚀 ТикТок видит, что видео репостят, и дает ему больше органических показов.", "rate": 0.016, "start": "Мгновенно", "speed": "До 500K/день", "retention": "Пожизненно"}
                }
            },
            "live": {
                "name": "🔴 Прямые трансляции (Live)",
                "items": {
                    "min15": {"id": "27534", "name": "👁 Зрители на стрим (15 минут)", "desc": "🔴 Загоним активных зрителей на вашу трансляцию на 15 минут.", "rate": 0.68, "start": "Мгновенно", "speed": "Сразу", "retention": "15 минут"},
                    "min60": {"id": "27536", "name": "👁 Зрители на стрим (1 час)", "desc": "🔴 Выводит эфир в топы! Зрители будут находиться у вас 60 минут.", "rate": 2.75, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"},
                    "comments": {"id": "27965", "name": "💬 Ваши комментарии прямо в прямой эфир", "desc": "💬 Напишите нам нужный текст, и боты будут писать его во время вашей трансляции.", "rate": 0.56, "start": "Мгновенно", "speed": "Быстро", "retention": "Во время Live"}
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
                    "std": {"id": "28864", "name": "🌱 Обычные подписчики (Гарантия 3 месяца)", "desc": "✅ Стандартные аккаунты для массы канала. Если отпишутся, восстановим в течение 90 дней.", "rate": 0.98, "start": "Мгновенно", "speed": "До 100k/день", "retention": "90 дней защиты"},
                    "prem": {"id": "29546", "name": "💎 100% Живые люди (Никогда не отпишутся)", "desc": "💎 Настоящие аккаунты Telegram. Защищены от любых чисток алгоритмов Дурова.", "rate": 0.63, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Пожизненная защита"},
                    "vip": {"id": "28457", "name": "🚀 Премиум подписчики Telegram (С просмотрами)", "desc": "🚀 Это люди с Premium-статусом в Telegram. Поднимают канал в глобальном поиске.", "rate": 3.60, "start": "Мгновенно", "speed": "Быстро", "retention": "7 Дней Non Drop"}
                }
            },
            "views": {
                "name": "👀 Просмотры постов",
                "items": {
                    "post1": {"id": "15972", "name": "👁 Просмотры на 1 последний пост", "desc": "👁 Мгновенно накрутим глазки на вашу последнюю запись.", "rate": 0.015, "start": "Мгновенно", "speed": "Молниеносно", "retention": "Не списываются"},
                    "post5": {"id": "28479", "name": "💎 Premium просмотры на 5 последних постов", "desc": "💎 Просмотры от аккаунтов с Premium-подпиской. Дает огромный траст каналу.", "rate": 0.50, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"}
                }
            },
            "reacts": {
                "name": "🔥 Реакции",
                "items": {
                    "pos": {"id": "28576", "name": "👍 Позитивные реакции (Микс + Просмотры)", "desc": "👍 Сразу пачка классных эмодзи (лайки, огоньки, сердечки) под вашим постом.", "rate": 0.02, "start": "Мгновенно", "speed": "Быстро", "retention": "Не списываются"},
                    "like": {"id": "23335", "name": "👍 Реакция Лайк (Навсегда)", "desc": "👍 Накрутим только классические лайки на ваш пост.", "rate": 0.03, "start": "Мгновенно", "speed": "Быстро", "retention": "Пожизненно"}
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
                    "vip": {"id": "27929", "name": "💎 VIP Подписчики (Самое высокое качество, Навсегда)", "desc": "💎 Самые безопасные подписчики для монетизации. Идут плавно, чтобы Ютуб не забанил канал. Гарантия навсегда.", "rate": 33.62, "start": "В течение дня", "speed": "Естественная", "retention": "Пожизненно (Auto Refill)"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Views)",
                "items": {
                    "native": {"id": "28692", "name": "🌱 Настоящие просмотры (От реальных людей)", "desc": "🌱 Выполняются живыми людьми. Ютуб их обожает. Полная гарантия от списаний.", "rate": 0.93, "start": "0-4 часа", "speed": "До 200k/день", "retention": "Пожизненно"},
                    "vip": {"id": "27906", "name": "💎 VIP Просмотры (С гарантией навсегда)", "desc": "💎 Безопасные просмотры высокого качества для любых видео.", "rate": 1.28, "start": "0-4 часа", "speed": "До 2k/день", "retention": "Пожизненно"},
                    "retention": {"id": "27909", "name": "⏱ Просмотры с долгим удержанием (Смотрят видео)", "desc": "⏱ Алгоритм не просто кликает, а смотрит ваше видео более 1 минуты. Идеально для алгоритмов YouTube.", "rate": 3.43, "start": "0-4 часа", "speed": "До 2k/день", "retention": "Пожизненно"}
                }
            },
            "likes": {
                "name": "❤️ Лайки / Комменты",
                "items": {
                    "like": {"id": "27930", "name": "👍 Лайки на видео (Никогда не пропадают)", "desc": "👍 Качественные лайки от пользователей. Пожизненная гарантия восстановления.", "rate": 0.52, "start": "0-1 час", "speed": "Быстро", "retention": "Пожизненно"},
                    "comment": {"id": "28756", "name": "💬 Ваши личные комментарии под видео", "desc": "💬 Напишите нам свой текст, и мы оставим его под вашим роликом от лица живых людей.", "rate": 3.00, "start": "1 час", "speed": "Быстро", "retention": "Пожизненно"}
                }
            },
            "live": {
                "name": "🔴 Прямые трансляции (Live)",
                "items": {
                    "min15": {"id": "27517", "name": "👁 Зрители на прямой эфир (15 минут)", "desc": "🔴 Зрители будут сидеть на вашей трансляции ровно 15 минут.", "rate": 0.31, "start": "Мгновенно", "speed": "Сразу", "retention": "15 минут"},
                    "min60": {"id": "27519", "name": "👁 Зрители на прямой эфир (1 час)", "desc": "🔴 Идеально для вывода стрима в ТОП. Удержание ровно 1 час.", "rate": 1.25, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"}
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
                    "page": {"id": "29815", "name": "🌱 Лайки на Страницу + Подписчики", "desc": "🌱 Увеличиваем число подписчиков и лайков вашей публичной страницы (Паблика). Гарантия навсегда.", "rate": 0.37, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Пожизненно (Lifetime)"},
                    "prof": {"id": "29444", "name": "💎 Подписчики на личный профиль (Гарантия месяц)", "desc": "💎 Накрутка друзей/подписчиков на вашу личную анкету. Защита 30 дней.", "rate": 0.10, "start": "Мгновенно", "speed": "До 300k/день", "retention": "30 дней"}
                }
            },
            "likes": {
                "name": "❤️ Лайки / Реакции",
                "items": {
                    "std": {"id": "29582", "name": "👍 Лайки на пост или фото (Навсегда)", "desc": "👍 Обычный классический лайк Фейсбука. Не пропадают.", "rate": 0.17, "start": "Мгновенно", "speed": "До 100k/день", "retention": "Пожизненно"},
                    "love": {"id": "29631", "name": "❤️ Реакция Супер (Сердечко)", "desc": "❤️ Делаем красивые реакции в виде сердечка на ваши фото и посты.", "rate": 0.09, "start": "Мгновенно", "speed": "До 10k/день", "retention": "Держатся стабильно"}
                }
            },
            "views": {
                "name": "👀 Просмотры (Видео/Live)",
                "items": {
                    "video": {"id": "29449", "name": "📱 Просмотры видео и Reels (Навсегда)", "desc": "📱 Разгоняем статистику видео. Полная гарантия от списаний.", "rate": 0.02, "start": "Мгновенно", "speed": "До 30k/день", "retention": "Пожизненно"},
                    "live": {"id": "29051", "name": "🔴 Зрители на прямой эфир (1 час)", "desc": "🔴 Держим активных зрителей весь ваш эфир (до 60 минут).", "rate": 4.56, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"}
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
                    "std": {"id": "15030", "name": "🌱 Надежные подписчики", "desc": "🌱 Качественные пользователи из США. Хорошо держатся в профиле.", "rate": 3.68, "start": "0-30 минут", "speed": "Быстро", "retention": "Долгосрочные"}
                }
            },
            "views": {
                "name": "👀 Просмотры постов",
                "items": {
                    "std": {"id": "29865", "name": "📱 Просмотры твитов и видео", "desc": "📱 Поднимает охваты и популярность вашего Твита. Гарантия навсегда.", "rate": 0.005, "start": "Мгновенно", "speed": "До 2M/день", "retention": "Пожизненно (Lifetime)"}
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
                    "std": {"id": "28251", "name": "🔥 Прослушивания треков (Premium качество)", "desc": "🔥 Прослушивания от пользователей с Premium аккаунтами. Продвигает трек в алгоритмах.", "rate": 0.91, "start": "Мгновенно", "speed": "До 1k/день", "retention": "Не списываются"}
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
                    "min60": {"id": "21850", "name": "👁 Зрители на стрим (1 час)", "desc": "🔴 Обязательно для стримеров. Люди заходят и сидят на вашем эфире целый час.", "rate": 2.20, "start": "Мгновенно", "speed": "Сразу", "retention": "60 минут"}
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
    # При /start можно сбросить язык, чтобы человек выбрал его заново
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
    
    text = t["pack_info"].format(
        name=service['name'], 
        desc=service.get('desc', 'Без описания'), 
        start=service['start'], 
        speed=service['speed'], 
        retention=service['retention']
    )
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

# ЗАЩИТА: Если скинули текст вместо чека
@dp.message(OrderProcess.waiting_for_receipt, F.text)
async def fallback_receipt_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    await message.answer(t["need_photo"])

@dp.message(OrderProcess.waiting_for_receipt, F.photo | F.document)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user
    lang = data.get("lang", "ru")
    t = LANG_DICT[lang]
    
    file_id = message.document.file_id if message.document else message.photo[-1].file_id
    # Передаем язык клиента в callback, чтобы админка знала, на каком языке отвечать
    callback_payload = f"{data['api_id']}_{data['vol']}_{user.id}_{lang}"
    
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
    kb.row(types.InlineKeyboardButton(text="❌ Оплата не поступила", callback_data=f"no_{user.id}_1_{lang}"))
    kb.row(types.InlineKeyboardButton(text="❌ Неверная сумма", callback_data=f"no_{user.id}_2_{lang}"))
    kb.row(types.InlineKeyboardButton(text="❌ Это не чек", callback_data=f"no_{user.id}_3_{lang}"))
    
    if message.document: await bot.send_document(ADMIN_ID, file_id, caption=admin_text, reply_markup=kb.as_markup())
    else: await bot.send_photo(ADMIN_ID, file_id, caption=admin_text, reply_markup=kb.as_markup())
        
    await message.answer(t["wait_msg"])
    
    # БЕЗОПАСНАЯ ОЧИСТКА ПАМЯТИ: сохраняем язык!
    await state.clear()
    await state.update_data(lang=lang)

# ==========================================
# 5. АДМИН ПАНЕЛЬ (ПОДКЛЮЧЕНО К PEAKERR)
# ==========================================

@dp.callback_query(F.data.startswith("ok_"))
async def admin_approve(callback: types.CallbackQuery):
    try:
        parts = callback.data.split("_")
        api_id = parts[1]
        vol = parts[2]
        user_id = parts[3]
        lang = parts[4] if len(parts) > 4 else "ru"
        
        t = LANG_DICT.get(lang, LANG_DICT["ru"])
        
        link = ""
        lines = callback.message.caption.split("\n")
        for i, line in enumerate(lines):
            if "🔗 Ссылка:" in line:
                link = lines[i+1].strip() if i+1 < len(lines) else line.replace("🔗 Ссылка:", "").strip()
        
        api_data = {'key': PEAKERR_API_KEY, 'action': 'add', 'service': api_id, 'link': link, 'quantity': vol}
        response = requests.post(PEAKERR_URL, data=api_data).json()
        
        if "order" in response:
            await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🟢 [УСПЕХ. ЗАКАЗ ID: {response['order']}]")
            success_message = t["success_msg"].format(order_id=response['order'])
            await bot.send_message(int(user_id), success_message)
        else:
            await callback.message.answer(f"Ошибка Peakerr: {response.get('error', 'Unknown')}", show_alert=True)
    except Exception as e:
        await callback.message.answer(f"Сбой: {e}", show_alert=True)

@dp.callback_query(F.data.startswith("no_"))
async def admin_reject(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    user_id = parts[1]
    reason_code = parts[2]
    lang = parts[3] if len(parts) > 3 else "ru"
    
    t = LANG_DICT.get(lang, LANG_DICT["ru"])
    reject_reason_localized = t["reasons"].get(reason_code, "Отказ в авторизации.")
    
    admin_reasons = {
        "1": "Оплата не поступила",
        "2": "Неверная сумма",
        "3": "Это не чек"
    }
    admin_reason = admin_reasons.get(reason_code, "Отказ")
    
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n🔴 [ОТКЛОНЕН: {admin_reason}]")
    
    reject_message = t["reject_msg"].format(reason=reject_reason_localized)
    await bot.send_message(int(user_id), reject_message)

async def main():
    logging.info("Система работает на Peakerr API.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
