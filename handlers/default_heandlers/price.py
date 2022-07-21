import requests
from keyboards.inline.inline_keyboards import city_markup, hotels_markup
from API_requests.endpoints import hotels_photo
from telebot.types import InputMediaPhoto, Message, CallbackQuery
from calendar_telegram import my_calendar
from states.information_user import UsersInfoState
from loader import bot
from loguru import logger


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def get_city(message: Message) -> None:
	if message.text == '/lowprice':
		bot.send_message(
			message.from_user.id,
			'Вы выбрали поиск самых дешевых отелей.\n'
			'\nВведите город, где будет проводиться поиск.\n\n‼️Поиск по городам РФ временно не доступен‼️'
		)
		bot.set_state(message.from_user.id, UsersInfoState.city)
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['commands'] = 'lowprice'
			data['price'] = 'PRICE'

	elif message.text == '/highprice':
		bot.send_message(
			message.from_user.id,
			'Вы выбрали поиск самых дорогих отелей.\n'
			'\nВведите город, где будет проводиться поиск.\n\n‼️Поиск по городам РФ временно не доступен‼️'
		)
		bot.set_state(message.from_user.id, UsersInfoState.city)
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['commands'] = 'highprice'
			data['price'] = 'PRICE_HIGHEST_FIRST'

	elif message.text == '/bestdeal':
		bot.send_message(
			message.from_user.id,
			'Вы выбрали поиск самых подходящих отелей по цене и расположению от центра.\n'
			'\nВведите город, где будет проводиться поиск.\n\n‼️Поиск по городам РФ временно не доступен‼️'
		)
		bot.set_state(message.from_user.id, UsersInfoState.price_min)
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['commands'] = 'bestdeal'
			data['price'] = 'DISTANCE_FROM_LANDMARK'
	logger.info('Выбор команды бота')


@bot.message_handler(state=UsersInfoState.price_min)
def get_price_min(message: Message) -> None:
	if message.text.isdigit():
		bot.send_message(message.from_user.id, 'Не корректный ввод! Попробуйте ввести заново🙅')
		bot.set_state(message.from_user.id, UsersInfoState.price_min)
	else:
		bot.send_message(message.from_user.id, 'Укажите минимальную стоимость отеля в рублях:')
		bot.set_state(message.from_user.id, UsersInfoState.price_max)

		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['city_name'] = message.text.capitalize()
	logger.info('Запрос стоимости отеля (мин)')


@bot.message_handler(state=UsersInfoState.price_max)
def get_price_max(message: Message) -> None:
	if message.text.isdigit():
		bot.send_message(message.from_user.id, 'Укажите максимальную стоимость отеля в рублях:')
		bot.set_state(message.from_user.id, UsersInfoState.max_distance_from_center)

		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['price_min'] = message.text
	else:
		bot.send_message(message.from_user.id, 'Не корректный ввод! Попробуйте ввести заново🙅')
		bot.set_state(message.from_user.id, UsersInfoState.price_max)
	logger.info('Запрос стоимости отеля (макс)')


@bot.message_handler(state=UsersInfoState.max_distance_from_center)
def get_max_distance(message: Message) -> None:
	if message.text.isdigit():
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			if int(data['price_min']) < int(message.text):
				bot.send_message(
					message.from_user.id, 'Укажите максимальное расстояние от центра (в км):'
				)
				bot.set_state(message.from_user.id, UsersInfoState.city)
				data['price_max'] = message.text
			else:
				bot.send_message(
					message.from_user.id,
					'Минимальная стоимость должна быть меньше максимальной!\n'
					'Попробуйте заново... нажмите на ➡ /help'
					)
				bot.set_state(message.from_user.id, UsersInfoState.city)
	else:
		bot.send_message(message.from_user.id, 'Не корректный ввод! Попробуйте ввести заново🙅')
		bot.set_state(message.from_user.id, UsersInfoState.max_distance_from_center)
	logger.info('Запрос расстояния от центра')


@bot.message_handler(state=UsersInfoState.city)
def count_hotels(message: Message) -> None:
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if data['commands'] == 'bestdeal':
			if message.text.isdigit():
				bot.send_message(message.from_user.id, 'Какое максимальное количество отелей будем искать? (не более 15)')
				bot.set_state(message.from_user.id, UsersInfoState.numbers_hotels)
				data['max_distance_from_center'] = message.text
			else:
				bot.send_message(message.from_user.id, 'Не корректный ввод! Попробуйте ввести заново🙅')
				bot.set_state(message.from_user.id, UsersInfoState.city)
		elif data['commands'] == 'lowprice' or data['commands'] == 'highprice':
			if message.text.isdigit():
				bot.send_message(message.from_user.id, 'Не корректный ввод! Попробуйте ввести заново🙅')
				bot.set_state(message.from_user.id, UsersInfoState.city)
			else:
				bot.send_message(message.from_user.id, 'Какое количество отелей будем искать? (не более 15)')
				bot.set_state(message.from_user.id, UsersInfoState.numbers_hotels)
				data['city_name'] = message.text.capitalize()
	logger.info('Запрос кол-ва отелей для поиска')


@bot.message_handler(state=UsersInfoState.numbers_hotels)
def get_check_in_date(message: Message) -> None:
	if message.text.isdigit() and 0 < int(message.text) <= 25:
		my_calendar(message)

		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['number_of_hotels'] = message.text
			data['user_name'] = message.from_user.first_name

	else:
		bot.send_message(message.from_user.id, 'Не корректный ввод! Попробуйте ввести заново🙅')
		bot.set_state(message.from_user.id, UsersInfoState.numbers_hotels)
	logger.info('Календарь')


@bot.message_handler(state=UsersInfoState.city_selection)
def specify_the_city(message: Message) -> None:
	with bot.retrieve_data(message.chat.id, message.chat.id) as data:
		keyboard_city = city_markup(city_name=data['city_name'])
		if keyboard_city:
			bot.send_message(message.chat.id, 'Уточните пожалуйста:', reply_markup=keyboard_city)
		else:
			bot.send_message(
				message.chat.id,
				'К сожалению🥺 по вашему запросу город найден!'
				'\nПопробуйте заново... нажмите на ➡ /help'
			)
	logger.info('Клавиатура с выбором местоположения')


@bot.callback_query_handler(func=lambda call: str(bot.get_state(call.from_user.id)).endswith('keyboards_cities'))
def callback_city(call: CallbackQuery) -> None:
	bot.answer_callback_query(call.id, text='Город выбран! Пожалуйста подождите...')
	bot.edit_message_text(
		chat_id=call.message.chat.id,
		message_id=call.message.message_id,
		text='Выберите отель:',
		reply_markup=hotels_markup(id_user=call.message.chat.id, call=call.data)
		)
	bot.set_state(call.message.chat.id, UsersInfoState.keyboards_hotels)
	logger.info('Просмотр отелей')


@bot.callback_query_handler(func=lambda call: str(bot.get_state(call.from_user.id)).endswith('keyboards_hotels'))
def get_a_photo_question(call: CallbackQuery) -> None:
	bot.answer_callback_query(call.id, text='Отель выбран! Пожалуйста подождите...')
	bot.send_message(call.message.chat.id, 'Сколько фотографий отеля вы бы хотели видеть? (Не более 10)')
	bot.set_state(call.message.chat.id, UsersInfoState.answer_photo)

	with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
		data['name_hotel'] = call.message.json['reply_markup']['inline_keyboard'][0][0]['text']
		data['id_hotel_photo'] = call.data
	logger.info('Запрос кол-ва фотографий отеля')


@bot.message_handler(state=UsersInfoState.answer_photo)
def get_photo_hotel(message: Message) -> None:
	if message.text.isdigit() and 0 < int(message.text) <= 10:
		bot.set_state(message.from_user.id, UsersInfoState.keyboards_hotels)
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			number_photo = int(message.text)
			photos = hotels_photo(data['id_hotel_photo'])
			media = []
			for index, photo in enumerate(photos[:number_photo]):
				photo_verification = requests.get(photo)
				if photo_verification.status_code == 200:
					if index == 0:
						media.append(InputMediaPhoto(photo, caption=data['name_hotel']))
					else:
						media.append(InputMediaPhoto(photo))
			bot.send_media_group(message.chat.id, media)

	else:
		bot.send_message(message.from_user.id, 'Не корректный ввод! Попробуйте ввести заново🙅')
		bot.set_state(message.from_user.id, UsersInfoState.answer_photo)
	logger.info('Вывод фотографий')
