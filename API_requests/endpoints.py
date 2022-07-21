import requests
import re
import json
from loguru import logger
from config_data.config import RAPID_API_KEY
from loader import bot
from requests import Response


def request_func(url: str, querystring: dict) -> Response | bool:
	"""
	Универсальная функция, которая делает запросы к API
	:param url:
	:param querystring:
	:return:
	"""
	headers = {
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
		"X-RapidAPI-Key": RAPID_API_KEY
	}
	try:
		response = requests.request("GET", url=url, headers=headers, params=querystring, timeout=30)
		if response.status_code == requests.codes.ok:
			return response
	except requests.exceptions.ReadTimeout as exc:
		logger.exception(exc)
		return False
	logger.info('Запрос к RAPID API')


def city_founding(city: str) -> list[dict[str, str]] | bool:
	"""
	Функция для получения информации о городе
	:param city: принимает аргумент с названием города
	:return: возвращат список городов, либо False
	"""
	url = "https://hotels4.p.rapidapi.com/locations/v2/search"
	querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}

	response = request_func(url=url, querystring=querystring)
	try:
		if response:
			pattern = r'(?<="CITY_GROUP",).+?[\]]'
			find = re.search(pattern, response.text)
			suggestions = json.loads(f"{{{find[0]}}}")
			cities = list()

			for dest_id in suggestions['entities']:
				name = re.sub(r"<span class='highlighted'>|<|/span>", '', dest_id['caption'])
				cities.append({'city_name': name, 'destination': dest_id['destinationId']})

			return cities
	except LookupError as exc:
		logger.exception(exc)
		return False
	logger.info('Запрос информации о городе')


def get_response_hotels(id_user: str, dest_id: str) -> Response | bool:
	"""
	Функция для отправки запроса по данным об отелях
	:param id_user: id пользователя
	:param dest_id: id города
	:return:
	"""
	with bot.retrieve_data(id_user, id_user) as data:
		ckeck_in = data['arrival_date']
		check_out = data['date_of_departure']
		sortOrder = data['price']
		landmarkIds = ''
		priceMin = ''
		priceMax = ''

		if data['commands'] == 'bestdeal':
			priceMin = data['price_min']
			priceMax = data['price_max']
			landmarkIds = 'центр города'

		url = "https://hotels4.p.rapidapi.com/properties/list"

		querystring = {
			"destinationId": dest_id, "pageNumber": "2", "pageSize": "25", "checkIn": ckeck_in,
			"checkOut": check_out, "adults1": "1", "priceMin": priceMin, "priceMax": priceMax, "sortOrder": sortOrder,
			"locale": "ru_RU", "currency": "RUB", "landmarkIds": landmarkIds
		}
		response = request_func(url=url, querystring=querystring)

		if response:
			return response
		else:
			return False


def hotel_information_extraction(id_user: str, dest_id: str) -> list[dict[str, str]] | bool:
	"""
	Функция, принимающая ответ запроса по отелям и формированию информации по каждому отелю.
	:param id_user:
	:param dest_id:
	:return:
	"""
	response = get_response_hotels(id_user, dest_id)
	hotels_list = list()

	with bot.retrieve_data(id_user, id_user) as data:
		if response:
			try:
				pattern = r'(?<=,)"results":.+?(?=,"pagination)'
				find = re.search(pattern, response.text)
				suggestions = json.loads(f"{{{find[0]}}}")

				for i_hotel in suggestions['results']:
					try:
						info_hotel = (
								{
									'name_hotel': i_hotel['name'],
									'price': i_hotel['ratePlan']['price']['current'],
									'address': f'{i_hotel["address"]["countryName"]} {i_hotel["address"].get("streetAddress", "")}',
									'distance_center': i_hotel['landmarks'][0]['distance'],
									'rating': i_hotel.get('guestReviews', {}).get('rating', 'нет данных').replace(',', '.'),
									'id_hotel': i_hotel['id'],
									'photo_hotel': i_hotel['optimizedThumbUrls']['srpDesktop']
								}
							)
						if data['commands'] == 'bestdeal':
							distance_of_hotel = re.sub(r",", ".", i_hotel['landmarks'][0]['distance'][:-3])
							max_dist = float(data['max_distance_from_center'])

							if float(distance_of_hotel) <= max_dist:
								hotels_list.append(info_hotel)

						else:
							hotels_list.append(info_hotel)
					except KeyError as exc:
						logger.error(exc)
						continue
				return hotels_list
			except TypeError as exc:
				logger.error(exc)
		else:
			return False
		logger.info('Запрос получения данных об отелях')


def hotels_photo(id_hotel: str) -> list | bool:
	"""
	Функция запроса данных о фотографиях отелей
	:param id_hotel: id отеля
	:return: возвращает список с фотографиями отеля, либо False
	"""
	url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
	querystring = {"id": id_hotel}

	photos = []
	response = request_func(url=url, querystring=querystring)
	logger.info('Запрос фотографий')

	if response:
		data = json.loads(response.text)
		for photo in data['hotelImages']:
			url = photo['baseUrl'].replace('_{size}', '_z')
			photos.append(url)
		return photos
	else:
		return False
