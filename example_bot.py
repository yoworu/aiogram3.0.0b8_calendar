import logging
import asyncio 

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram3b8_calendar1 import SimpleCalCallback, SimpleCalendar, DialogCalCallback, DialogCalendar

from config import API_TOKEN

# API_TOKEN = '' uncomment and insert your telegram bot API key here

router = Router()


start_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='Navigation Calendar'),
        KeyboardButton(text='Dialog Calendar')]
    ]
)


# starting bot when user sends `/start` command, answering with inline calendar
@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.reply('Pick a calendar', reply_markup=start_kb)


@router.message(F.text.title() == 'Navigation Calendar')
async def nav_cal_handler(message: Message):
    await message.answer("Please select a date: ", reply_markup=SimpleCalendar.start_calendar())


# simple calendar usage
@router.callback_query(SimpleCalCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: SimpleCalCallback):
    date = await SimpleCalendar.process_selection(callback_query, callback_data)
    if date:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )


@router.message(F.text.title() == 'Dialog Calendar')
async def simple_cal_handler(message: Message):
    await message.answer("Please select a date: ", reply_markup=DialogCalendar.start_calendar())


# dialog calendar usage
@router.callback_query(DialogCalCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: DialogCalCallback):
    date = await DialogCalendar.process_selection(callback_query, callback_data)
    if date:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )


async def main() -> None:
    # Initialize bot and dispatcher
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    # Run bot
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
