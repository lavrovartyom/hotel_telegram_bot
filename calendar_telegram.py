from telegram_bot_calendar import DetailedTelegramCalendar
from telebot.types import Message, CallbackQuery
from datetime import date, timedelta
from loader import bot
from handlers.default_heandlers import price
from states.information_user import UsersInfoState

ALL_STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'}


def get_calendar(is_process=False, callback_data=None, **kwargs):
    """
    Функция формирования календаря
    :param is_process:
    :param callback_data:
    :param kwargs:
    :return:
    """
    if is_process:
        result, key, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                     current_date=kwargs.get('current_date'),
                                                     min_date=kwargs['min_date'],
                                                     max_date=kwargs['max_date'],
                                                     locale=kwargs['locale']).process(callback_data.data)
        return result, key, step
    else:
        calendar, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                  current_date=kwargs.get('current_date'),
                                                  min_date=kwargs['min_date'],
                                                  max_date=kwargs['max_date'],
                                                  locale=kwargs['locale']).build()
        return calendar, step


def my_calendar(message: Message) -> None:
    """
    Календарь даты заезда
    :param message:
    :return:
    """
    today = date.today()
    calendar, step = get_calendar(calendar_id=1,
                                  current_date=today,
                                  min_date=today,
                                  max_date=today + timedelta(days=365*2),
                                  locale="ru")
    bot.send_message(message.from_user.id, f"Выберите дату заезда: \n{ALL_STEPS[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def handle_arrival_date(call: CallbackQuery):
    """
    Функция колбек для первого календаря
    :param call:
    :return:
    """
    today = date.today()
    result, key, step = get_calendar(calendar_id=1,
                                     current_date=today,
                                     min_date=today,
                                     max_date=today + timedelta(days=365*2),
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                              call.from_user.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['arrival_date'] = result
            bot.edit_message_text(f"Дата вашего заезда: {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

            calendar, step = get_calendar(calendar_id=2,
                                          min_date=result,
                                          max_date=result + timedelta(days=365*2),
                                          locale="ru",
                                          )

            bot.send_message(call.from_user.id,
                             f"Выберите дату выезда:"
                             f"\n Год",
                             reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def handle_departure_date(call: CallbackQuery):
    """
    Функция колбэк для второго календаря
    :param call:
    :return:
    """
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        today = date.today()
        result, key, step = get_calendar(calendar_id=2,
                                         current_date=today,
                                         min_date=data['arrival_date'] + timedelta(days=1),
                                         max_date=today + timedelta(days=365*2),
                                         locale="ru",
                                         is_process=True,
                                         callback_data=call)
        if not result and key:
            bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                                  call.from_user.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            data['date_of_departure'] = result
            bot.edit_message_text(
                f"Дата вашего выезда: <b>{result}</b>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='html'
            )
            bot.answer_callback_query(call.id, text='Идёт поиск города! Пожалуйста подождите...')
            bot.set_state(call.from_user.id, UsersInfoState.keyboards_cities)
            price.specify_the_city(call.message)

