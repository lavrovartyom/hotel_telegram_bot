from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Привет 🖐, {message.from_user.first_name}, '
                                           f'<b>\nЯ БОТ ПО ПОБОДБОРУ ОТЕЛЕЙ!</b>', parse_mode='html')
    bot.send_message(message.from_user.id, '<b>И вот что я умею:\n'
                                           '/help — помощь по командам бота\n'
                                           '\n'
                                           '/lowprice — вывод самых дешёвых отелей в городе\n'
                                           '\n'
                                           '/highprice — вывод самых дорогих отелей в городе\n'
                                           '\n'
                                           '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению '
                                           'отцентра\n'
                                           '\n'
                                           '/history — вывод истории поиска отелей</b>', parse_mode='html')

