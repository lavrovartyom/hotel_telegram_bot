from telebot.handler_backends import State, StatesGroup


class UsersInfoState(StatesGroup):
	start = State()
	city = State()
	numbers_hotels = State()
	price_min = State()
	price_max = State()
	max_distance_from_center = State()
	city_selection = State()
	hotel_selection = State()
	answer_photo = State()
	keyboards_cities = State()
	keyboards_hotels = State()

