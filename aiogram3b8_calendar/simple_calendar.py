import calendar
from datetime import timedelta, date


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# setting callback_data prefix and parts
class CalendarCallback(CallbackData, prefix='simple_calendar'):
    act: str
    year: int
    month: int
    day: int
    

class SimpleCalendar:

    @staticmethod
    def start_calendar(
        year: int = date.today().year,
        month: int = date.today().month
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """
        inline_kb = InlineKeyboardBuilder()

        ignore_callback = CalendarCallback(act="IGNORE", year=year, month=month, day=0).pack()  # for buttons with no answer
        # First row - Month and Year
        inline_kb.row(
            InlineKeyboardButton(
                text="<<",
                callback_data=CalendarCallback(act="PREV-YEAR", year=year, month=month, day=1).pack()
            ),
            InlineKeyboardButton(
                text=f'{calendar.month_name[month]} {str(year)}',
                callback_data=ignore_callback
            ),
            InlineKeyboardButton(
                text=">>",
                callback_data=CalendarCallback(act="NEXT-YEAR", year=year, month=month, day=1).pack()
            ),
            width=3
        )
        # Second row - Week Days
        second_row = [
            InlineKeyboardButton(text=day, callback_data=ignore_callback) for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        ]
        inline_kb.row(*second_row, width=7)
        
        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            calendar_rows = []
            for day in week:
                if (day == 0): 
                    calendar_rows.append(InlineKeyboardButton(text=" ", callback_data=ignore_callback))
                    continue
                calendar_rows.append(InlineKeyboardButton(
                    text=str(day), callback_data=CalendarCallback(act="DAY", year=year, month=month, day=day).pack()
                ))
            inline_kb.row(*calendar_rows, width=7)

        # Last row - Buttons
        inline_kb.row(
            InlineKeyboardButton(
               text="<", callback_data=CalendarCallback(act="PREV-MONTH", year=year, month=month, day=day).pack()
            ),
            InlineKeyboardButton(text=" ", callback_data=ignore_callback),
            InlineKeyboardButton(
                text=">", callback_data=CalendarCallback(act="NEXT-MONTH", year=year, month=month, day=day).pack()
            )
        )

        return inline_kb.as_markup()
    
    @classmethod
    async def process_selection(cls, query: CallbackQuery, data: CalendarCallback) -> date | None:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a date or None.
        """
        return_data = None
        temp_date = date(int(data.year), int(data.month), 1)
        # processing empty buttons, answering with no action
        if data.act == "IGNORE":
            await query.answer(cache_time=60)
        # user picked a day button, return date
        if data.act == "DAY":
            await query.message.delete_reply_markup()   # removing inline keyboard
            return_data = date(int(data.year), int(data.month), int(data.day))
        # user navigates to previous year, editing message with new calendar
        if data.act == "PREV-YEAR":
            prev_date = date(int(data.year) - 1, int(data.month), 1)
            await query.message.edit_reply_markup(reply_markup=cls.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next year, editing message with new calendar
        if data.act == "NEXT-YEAR":
            next_date = date(int(data.year) + 1, int(data.month), 1)
            await query.message.edit_reply_markup(reply_markup=cls.start_calendar(int(next_date.year), int(next_date.month)))
        # user navigates to previous month, editing message with new calendar
        if data.act == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(reply_markup=cls.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next month, editing message with new calendar
        if data.act == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(reply_markup=cls.start_calendar(int(next_date.year), int(next_date.month)))
        # at some point user clicks DAY button, returning date
        return return_data
