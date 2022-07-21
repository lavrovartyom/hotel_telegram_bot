from peewee import IntegerField, DateField, CharField, SqliteDatabase, Model
from datetime import datetime
from typing import Any

db = SqliteDatabase('users.db')


class BaseModel(Model):

	class Meta:
		database = db


class User(BaseModel):
	telegram_id = IntegerField()
	date = DateField(default=datetime.now)
	name = CharField()
	commands = CharField()
	city = CharField()
	hotel_photo = CharField()
	hotel = CharField()


def add_info_db(id_user: Any, name: Any, commands: Any, city: Any, hotel_photo: Any, hotel: Any) -> None:
	"""
	Функция записи в БД
	:param id_user:
	:param name:
	:param commands:
	:param city:
	:param hotel_photo:
	:param hotel:
	:return:
	"""
	with db:
		User.create(telegram_id=id_user, name=name, commands=commands, city=city, hotel_photo=hotel_photo, hotel=hotel)


def get_info_db(id_user: int) -> Any:
	"""
	Функция получения данных из БД
	:param id_user:
	:return:
	"""
	with db:
		info_db = User.select().where(User.telegram_id == id_user)
		return info_db


