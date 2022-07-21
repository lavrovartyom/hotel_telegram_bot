from telebot import types
from API_requests.endpoints import city_founding, hotel_information_extraction
from loader import bot
from data_base import add_info_db
from typing import Any
from telebot.types import InlineKeyboardMarkup


def city_markup(city_name: str) -> InlineKeyboardMarkup | bool:
	"""
	Функция для формирования inline кнопок с названием города
	:param city_name:
	:return:
	"""
	cities = city_founding(city=city_name)
	keyboard = types.InlineKeyboardMarkup()
	if cities:
		for city in cities:
			item = types.InlineKeyboardButton(text=city['city_name'], callback_data=city['destination'])
			keyboard.add(item)
		return keyboard
	else:
		return False


def hotels_markup(id_user: Any, call: str) -> None:
	"""
	Функция для формирования inline кнопок с названиями отелей,
	а так же отправляет данные в запись БД
	:param id_user:
	:param call:
	:return:
	"""
	hotels = hotel_information_extraction(id_user=id_user, dest_id=call)
	if hotels:
		with bot.retrieve_data(id_user, id_user) as data:
			for hotel in hotels[:int(data['number_of_hotels'])]:
				add_info_db(
					id_user=id_user,
					name=data['user_name'],
					commands=data['commands'],
					city=data['city_name'],
					hotel_photo=hotel['photo_hotel'],
					hotel=hotel['name_hotel']
				)  # отправка данных в запись БД

				keyboard = types.InlineKeyboardMarkup()
				item = types.InlineKeyboardButton(text='Фото отеля: ' + hotel['name_hotel'], callback_data=str(hotel['id_hotel']))
				keyboard.add(item)
				bot.send_photo(id_user, hotel['photo_hotel'])
				bot.send_message(
					id_user,
					f'🏨 Название отеля : {hotel["name_hotel"]}'
					f'\n🗺 Адрес: {hotel["address"]}'
					f'\n💰 Цена за сутки: {hotel["price"]}'
					f'\n🥇 Рейтинг: {hotel["rating"]}'
					f'\n🚍 Дистанция от центра: {hotel["distance_center"]}'
					f'\n📅 Дата вашего заезда: {data["arrival_date"]}'
					f'\n📅 Дата вашего выезда: {data["date_of_departure"]}\n'
					f'\n🌐 Сайт отеля: https://www.hotels.com/ho{hotel["id_hotel"]}\n'
					f'\n⬇ Чтобы увидеть фото отеля, нажмите на кнопку ниже ⬇',
					reply_markup=keyboard
				)
	else:
		bot.send_message(
			id_user,
			'К сожалению🥺 по вашему запросу отелей не найдено!'
			'\nПопробуйте заново... нажмите на ➡ /help'
		)
