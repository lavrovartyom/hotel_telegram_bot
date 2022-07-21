from loader import bot
import handlers
from utils.set_bot_commands import set_default_commands
from telebot.custom_filters import StateFilter
from loguru import logger
from data_base import *


if __name__ == '__main__':
    User.create_table()
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    logger.add('logs.log', format='{time} {level} {message}', level='DEBUG')
    logger.debug('Error')
    logger.info('Старт бота')
    logger.warning('Warning')
    bot.infinity_polling()
