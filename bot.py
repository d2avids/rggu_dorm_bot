import os
import logging
import sys

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

import telegram
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

CREDS = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

EVENTS_SPREADSHEET_ID = '1pYIZt4S7ZtrDJqbJeaYr14cCqnQ1HhGbViOu_Jsrnrk'
EVENTS_INFO_RANGE = 'events!A1:C50'
COMMANDS_INFO_RANGE = 'commands!A1:B2'

# Статические сообщения для команд
START_MESSAGE = (
    'Привет! Это бот, разработанный @Achililes на '
    'некоммерческой основе. Ты можешь воспользоваться им '
    'для того, чтобы узнать всю необходимую информацию '
    'о жизни в общежитии РГГУ и не только :) '
    'Нажимай на значок "/" возле кнопки отправить '
    'для того, чтобы опробовать и ознакомиться со всеми командами.\n'
    '\nИсходный код бота доступен в свободном доступе тут: '
    'https://github.com/d2avids/rggu_dorm_bot'
)
CONTACTS_MESSAGE = (
    'Номера телефонов комендантов:\n'
    'Патимат +7-495-250-65-44\n'
    'Бахарева (зав. общежитием) +7-495-388-63-43'
)
CONTACTS2_MESSAGE = (
       'Международный отдел\n'
       '\nТелефон: +7 (495) 250-65-14\n'
       'Почта: adm_ums@rggu.ru\n'
       'Адрес: Москва, Миусская площадь, д. 6, корп. 6, каб. 303'
    )
GUEST_MESSAGE = 'Как пускать гостей описано тут:'
GRAF_MESSAGE = 'График смены белья ниже:'
GRAF0_MESSAGE = (
    '🔹 ДНЕВНЫЕ КОМЕНДАНТЫ:\n'
    'ПН-ЧТ: 9:30 до 17:45\n'
    'ПТ: 9:30 - 16:30\n'
    '🍽 Обед: 12:30-13:30\n'
    '\n🌃 Ночной комендант работает каждый '
    'день с 18:00 до 6:00 (найти можно в '
    'кабинете напротив поста охраны)'
)
GRAF1_MESSAGE = (
    '💰 ОТДЕЛ ПО СОЦИАЛЬНЫМ ВОПРОСАМ (226)\n'
    'Пн.-чт.: с 10:00 до 17.30\n'
    'Пт.: с 10:00 до 16.30\n'
    'Обед: с 14.00 до 15.00\n'

    'Номер телефона: +7 (495) 250-63-99\n'
    'Почта (выплаты и стипендии): stip@rggu.ru\n'
    'Почта (общежитие): hostel@rggu.ru\n'
)
GRAF2_MESSAGE = (
    'ПАСПОРТНЫЙ СТОЛ:\n'
    '\nПН-ВТ.: 9.30 - 17.00\n'
    'Среда: 9.30 - 12.30\n'
    'Четверг:  9.30 -17.00\n'
    'Пятница:  9.30 - 12.30\n'
    '\n🍽 Обед с 12.30 до 13.30'
)
GRAF3_MESSAGE = (
    'ВТОРОЙ ОТДЕЛ (ВОЕННО-УЧЕТНЫЙ СТОЛ) - 175\n'
    '\nпонедельник-четверг с 9.00 до 17.00\n'
    'пятница с 9.00 до 16.00\n'
    'перерыв на обед с 12.00 до 13.00\n'

    'Телефоны: +7 (499) 251-36-04  +7 (495) 250-69-30\n'
    'Почта: ii-otdel@rggu.ru'
)
GRAF4_MESSAGE = (
    'БЮРО ПРОПУСКОВ:\n'
    '\nПН.-ЧТ.: с 9:00 до 17:00\n'
    'ПТ.: с 9:00 до 16:00\n'
    'СБ.-ВС. – выходные дни'
)

SOCIAL_DEPARTMENT_URL = ('https://rsuh.ru/hostel/contacts'
                         '/the-department-of-work-with-students/')
GRAF_URL = 'https://t.me/newsyangelya/139'
CONTACTS_URL = 'https://t.me/newsyangelya/4'
GUESTS_URL = 'https://t.me/newsyangelya/52'
PRICE_BUTTON_URL = 'https://t.me/c/1189451602/165226'

# Названия файлов из static
BLANKS_FILE = 'Бланк на пропуск гостей.doc'
BLANKS1_FILE = 'Бланк на переселение в др. комнату.docx'
BLANKS2_FILE = 'Расписка при выселении.docx'
BLANKS3_FILE = 'Ввоз или вывоз вещей.docx'
BLANKS4_FILE = 'Бланк на въезд автомобиля.docx'
FINSUPPORT_FILE = 'Заявление на мат. помощь.docx'

# Сообщения ошибок
NO_TOKENS = (
            'Бот не может быть запущен без указания '
            'всех необходимых переменных окружения. '
            'Не хватает следующих: {tokens}'
        )
NO_KEYS_JSON = 'Отсутствует файл keys.json с ключами Google API.'
NO_REPLY = 'Ошибка API Telegram при отправке сообщения {}'
NOT_LIST_API = 'Ответ Google Sheets API ожидался в формате списка'
NOT_LIST_RAWS = 'Google Sheets API вернул строки в неожиданном формате'
GOOGLE_API_HTTPERROR = 'Ошибка запроса к Google Sheets API: {}'
GOOGLE_UNEXPECTED_ERROR = 'Неожиданная ошибка {}'
BOT_AUTH_ERROR = 'Не удалось авторизовать бота. Ошибка: {}'
TG_API_FAIL = 'Ошибка при взаимодействии с API {}'

# Сообщения INFO и DEBUG
BOT_AUTH_SUCCESS = 'Бот успешно авторизован!'
REPLY_SUCCESS = 'Реплай успешно отправлен!'

# Определяем место хранения файлов для отправки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger('bot')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(console_handler)


def check_tokens():
    """Проверка доступности токенов и ключей в окружении."""
    token_miss = []

    if not TELEGRAM_TOKEN:
        token_miss.append('TELEGRAM_TOKEN')

    if token_miss:
        error_message = NO_TOKENS.format(tokens=token_miss)
        logger.critical(error_message)
        return False

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        logger.critical(NO_KEYS_JSON)
        return False

    return True


def reply(update, message, keyboard=None):
    """Отправка сообщения или лог исключения."""
    try:
        update.message.reply_text(
            text=message,
            reply_markup=keyboard,
            parse_mode='HTML',
            )
        logger.debug(REPLY_SUCCESS)
    except telegram.error.TelegramError as e:
        logger.error(NO_REPLY.format(e))


def reply_file(update, file):
    """Отправка файла или лог исключения."""
    try:
        with open(file, 'rb') as file:
            update.message.reply_document(document=file)
            logger.debug(REPLY_SUCCESS)
    except telegram.error.TelegramError as e:
        logging.error(NO_REPLY.format(e))


def get_events():
    """Получить мероприятия из Excel файла."""
    try:
        service = build('sheets', 'v4', credentials=CREDS)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=EVENTS_SPREADSHEET_ID,
                                    range=EVENTS_INFO_RANGE).execute()
        data = result.get('values')
        return check_google_sheets_response(data)
    except HttpError as e:
        logging.error(GOOGLE_API_HTTPERROR.format(e))
    except Exception as e:
        logging.error(GOOGLE_UNEXPECTED_ERROR.format(e))


def get_command_text():
    """Получаем текст для команд из Excel файла."""
    try:
        service = build('sheets', 'v4', credentials=CREDS)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=EVENTS_SPREADSHEET_ID,
                                    range=COMMANDS_INFO_RANGE).execute()
        data = result.get('values')
        return check_google_sheets_response(data)
    except HttpError as e:
        logging.error(GOOGLE_API_HTTPERROR.format(e))
    except Exception as e:
        logging.error(GOOGLE_UNEXPECTED_ERROR.format(e))


def check_google_sheets_response(data):
    """Проверка корректности ответа Google Sheets API."""
    if not isinstance(data, list):
        raise TypeError(NOT_LIST_API)

    if not isinstance(data[0], list):
        raise TypeError(NOT_LIST_RAWS)

    return data


def price_button():
    """Кнопка с ценами и условиями на печать и скан."""
    button = telegram.InlineKeyboardButton(
        'Цены и условия',
        url=PRICE_BUTTON_URL,
    )
    keyboard = telegram.InlineKeyboardMarkup([[button]])
    return keyboard


def start(update, context):
    """Стартовое, ознакомительное сообщение при старте работы с ботом."""
    reply(update, START_MESSAGE)


def p_rint(update, context):
    """/print информация о печати в общежитии."""
    print_message = get_command_text()[1][0]
    reply(update, print_message, price_button())


def scan(update, context):
    """/scan информация о сканировании в общежитии."""
    scan_message = get_command_text()[1][1]
    reply(update, scan_message, price_button())


def guests(update, context):
    """/guests инструкция по запуску гостей в общежитие."""

    button = telegram.InlineKeyboardButton(
        'Как пускать гостей',
        url=GUESTS_URL,
    )
    keyboard = telegram.InlineKeyboardMarkup([[button]])

    reply(update, GUEST_MESSAGE, keyboard)


def contacts(update, context):
    """/contacts контакты комендантов."""
    button = telegram.InlineKeyboardButton(
        'График работы',
        url=CONTACTS_URL,
    )
    keyboard = telegram.InlineKeyboardMarkup([[button]])

    reply(update, CONTACTS_MESSAGE, keyboard)


def contacts1(update, context):
    """/contacts1 контакты соц. отдела"""
    button = telegram.InlineKeyboardButton(
        'Подробнее',
        url=SOCIAL_DEPARTMENT_URL,
    )
    keyboard = telegram.InlineKeyboardMarkup([[button]])

    reply(update, GRAF1_MESSAGE, keyboard)


def contacts2(update, context):
    """/contacts2 контакты международного отдела."""
    reply(update, CONTACTS2_MESSAGE)


def graf(update, context):
    """/graf информация о смене белья."""
    button = telegram.InlineKeyboardButton(
        'График смены белья',
        url=GRAF_URL,
    )
    keyboard = telegram.InlineKeyboardMarkup([[button]])

    reply(update, GRAF_MESSAGE, keyboard)


def graf0(update, context):
    """/graf0 информация о смене белья."""
    reply(update, GRAF0_MESSAGE)


def graf1(update, context):
    """/graf1 информация о работе соц.отдела."""
    button = telegram.InlineKeyboardButton(
        'Подробнее',
        url=SOCIAL_DEPARTMENT_URL,
    )
    keyboard = telegram.InlineKeyboardMarkup([[button]])

    reply(update, GRAF1_MESSAGE, keyboard)


def graf2(update, context):
    """/graf2 график паспортного стола."""
    reply(update, GRAF2_MESSAGE)


def graf3(update, context):
    """/graf3 график военного стола."""
    reply(update, GRAF3_MESSAGE)


def graf4(update, context):
    """/graf4 график бюро пропусков."""
    reply(update, GRAF4_MESSAGE)


def blanks(update, context):
    """/blanks бланк на пропуск гостей."""
    file_path = os.path.join(
        STATIC_DIR,
        BLANKS_FILE
    )
    reply_file(update, file_path)


def blanks1(update, context):
    """/blanks1 бланк на переселение в др. комнату."""
    file_path = os.path.join(
        STATIC_DIR,
        BLANKS1_FILE,
    )
    reply_file(update, file_path)


def blanks2(update, context):
    """/blanks2 расписка при выселении."""
    file_path = os.path.join(
        STATIC_DIR,
        BLANKS2_FILE,
    )
    reply_file(update, file_path)


def blanks3(update, context):
    """/blanks3 бланк на ввоз/вывоз техники и мебели"""
    file_path = os.path.join(
        STATIC_DIR,
        BLANKS3_FILE,
    )
    reply_file(update, file_path)


def blanks4(update, context):
    """/blanks4 бланк на въезд автомобиля."""
    file_path = os.path.join(
        STATIC_DIR,
        BLANKS4_FILE,
    )
    reply_file(update, file_path)


def finsupport(update, context):
    """/finsupport заявление на мат. помощь."""
    file_path = os.path.join(
        STATIC_DIR,
        FINSUPPORT_FILE,
    )
    reply_file(update, file_path)


def events(update, context):
    """/events reply ответ со списком мероприятий."""
    date = get_events()

    text = 'Список ближайших мероприятий:\n'
    for i in range(1, len(date)):
        text += (
            f'\n{date[0][0]} 🕘: {date[i][0]}\n'
            f'{date[0][1]} 🎲: {date[i][1]}\n'
            f'{date[0][2]} ✍️: Читать подробнее можно '
            f'<a href="{date[i][2]}">здесь</a>\n'
        )

    reply(update, text)


def main():
    "Основная логика работы бота."
    try:
        updater = Updater(TELEGRAM_TOKEN, use_context=True)
    except telegram.error.TelegramError as e:
        logger.error(TG_API_FAIL.format(e))

    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    print_handler = CommandHandler('print', p_rint)
    scan_hadnler = CommandHandler('scan', scan)
    guests_handler = CommandHandler('guests', guests)
    contacts_handler = CommandHandler('contacts', contacts)
    contacts1_handler = CommandHandler('contacts1', contacts1)
    contacts2_handler = CommandHandler('contacts2', contacts2)
    graf_handler = CommandHandler('graf', graf)
    graf_0_handler = CommandHandler('graf0', graf0)
    graf_1_handler = CommandHandler('graf1', graf1)
    graf_2_handler = CommandHandler('graf2', graf2)
    graf_3_handler = CommandHandler('graf3', graf3)
    graf_4_handler = CommandHandler('graf4', graf4)
    blanks_handler = CommandHandler('blanks', blanks)
    blanks_handler = CommandHandler('blanks', blanks)
    blanks_1_handler = CommandHandler('blanks1', blanks1)
    blanks_2_handler = CommandHandler('blanks2', blanks2)
    blanks_3_handler = CommandHandler('blanks3', blanks3)
    blanks_4_handler = CommandHandler('blanks4', blanks4)
    finsup_handler = CommandHandler('finsupport', finsupport)
    events_handler = CommandHandler('events', events)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(print_handler)
    dispatcher.add_handler(scan_hadnler)
    dispatcher.add_handler(guests_handler)
    dispatcher.add_handler(contacts_handler)
    dispatcher.add_handler(contacts1_handler)
    dispatcher.add_handler(contacts2_handler)
    dispatcher.add_handler(graf_handler)
    dispatcher.add_handler(graf_0_handler)
    dispatcher.add_handler(graf_1_handler)
    dispatcher.add_handler(graf_2_handler)
    dispatcher.add_handler(graf_3_handler)
    dispatcher.add_handler(graf_4_handler)
    dispatcher.add_handler(blanks_handler)
    dispatcher.add_handler(blanks_1_handler)
    dispatcher.add_handler(blanks_2_handler)
    dispatcher.add_handler(blanks_3_handler)
    dispatcher.add_handler(blanks_4_handler)
    dispatcher.add_handler(finsup_handler)
    dispatcher.add_handler(events_handler)

    try:
        updater.start_polling()
        logger.info(BOT_AUTH_SUCCESS)
        updater.idle()
    except telegram.error.TelegramError as e:
        logger.critical(BOT_AUTH_ERROR.format(e))
        raise


if __name__ == '__main__':
    if not check_tokens():
        sys.exit(1)
    main()
