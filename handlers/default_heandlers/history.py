from loader import bot
from telebot.types import Message
from loguru import logger
from data_base import get_info_db


@bot.message_handler(commands=['history'])
def get_history(message: Message) -> None:
	history = get_info_db(int(message.from_user.id))

	if history:
		bot.send_message(message.from_user.id, 'Ваша история поиска.')
		for story in history:
			text = f'Дата запроса: {story.date}\n' \
				   f'Название команды: {story.commands}\n' \
				   f'Город: {story.city}\n' \
				   f'Отель: {story.hotel}'
			bot.send_photo(message.from_user.id, story.hotel_photo)
			bot.send_message(message.from_user.id, text)
	else:
		bot.send_message(message.from_user.id, 'Ваша история поиска пуста!')
	logger.info('Выбор команды history')
