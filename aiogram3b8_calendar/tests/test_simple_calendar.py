import calendar
from datetime import date
from unittest.mock import AsyncMock

import pytest

from aiogram3b8_calendar import SimpleCalendar, SimpleCalCallback
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# checking that overall structure of returned object is correct
@pytest.mark.asyncio
async def test_start_calendar():
    result = SimpleCalendar.start_calendar()

    assert isinstance(result, InlineKeyboardMarkup)
    
    assert result.inline_keyboard
    
    kb = result.inline_keyboard
    assert isinstance(kb, list)

    for i in kb:
        assert isinstance(i, list)

    assert isinstance(kb[0][1], InlineKeyboardButton)
    now = date.today()
    assert kb[0][1].text == f'{calendar.month_name[now.month]} {str(now.year)}'
    assert isinstance(kb[0][1].callback_data, str)


# checking if we can pass different years & months as start periods
testset = [
    (2022, 2, 'February 2022'),
    (2022, None, f'{calendar.month_name[date.today().month]} 2022'),
    (None, 5, f'May {date.today().year}'),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("year, month, expected", testset)
async def test_start_calendar_params(year, month, expected):
    if year and month:
        result = SimpleCalendar().start_calendar(year=year, month=month)
    elif year:
        result = SimpleCalendar().start_calendar(year=year)
    elif month:
        result = SimpleCalendar().start_calendar(month=month)
    kb = result.inline_keyboard
    assert kb[0][1].text == expected


testset_deprecated = [
    ({'@': 'simple_calendar', 'act': 'IGNORE', 'year': '2022', 'month': '8', 'day': '0'}, (None)),
    ({'@': 'simple_calendar', 'act': 'DAY', 'year': '2022', 'month': '8', 'day': '1'}, (date(2022, 8, 1))),
    ({'@': 'simple_calendar', 'act': 'DAY', 'year': '2021', 'month': '7', 'day': '16'}, (date(2021, 7, 16))),
    ({'@': 'simple_calendar', 'act': 'DAY', 'year': '1900', 'month': '10', 'day': '8'}, (date(1900, 10, 8))),
    ({'@': 'simple_calendar', 'act': 'PREV-YEAR', 'year': '2022', 'month': '8', 'day': '1'}, (None)),
    ({'@': 'simple_calendar', 'act': 'PREV-MONTH', 'year': '2021', 'month': '8', 'day': '0'}, (None)),
    ({'@': 'simple_calendar', 'act': 'NEXT-YEAR', 'year': '2022', 'month': '8', 'day': '1'}, (None)),
    ({'@': 'simple_calendar', 'act': 'NEXT-MONTH', 'year': '2021', 'month': '8', 'day': '0'}, (None)),
]

testset = [
    (SimpleCalCallback(act=test[0]['act'],
                       year=test[0]['year'],
                       month=test[0]['month'],
                       day=test[0]['day']),
     test[1]) for test in testset_deprecated
]


@pytest.mark.asyncio
@pytest.mark.parametrize("callback_data, expected", testset)
async def test_process_selection(callback_data, expected):
    query = AsyncMock()
    result = await SimpleCalendar.process_selection(query=query, data=callback_data)
    assert result == expected
