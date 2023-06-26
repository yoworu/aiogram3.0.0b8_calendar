from datetime import date

from unittest.mock import AsyncMock

import pytest


from aiogram3b8_calendar import DialogCalendar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram3b8_calendar import DialogCalCallback



# checking that overall structure of returned object is correct
@pytest.mark.asyncio
async def test_start_calendar():
    result = DialogCalendar.start_calendar()

    assert isinstance(result, InlineKeyboardMarkup)
     
    kb = result.inline_keyboard
    assert isinstance(kb, list)

    for i in kb:
        assert isinstance(i, list)

    assert isinstance(kb[0][0], InlineKeyboardButton)
    year = date.today().year

    assert int(kb[0][0].text) == (year - 2)
    assert isinstance(kb[0][0].callback_data, str)


# checking if we can pass different years start period to check the range of buttons
testset = [
    (2020, 2018, 2022),
    (None, date.today().year - 2, date.today().year + 2),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("year, expected1, expected2", testset)
async def test_start_calendar_params(year, expected1, expected2):
    if year:
        result = DialogCalendar.start_calendar(year=year)
    else:
        result = DialogCalendar.start_calendar()
    kb = result.inline_keyboard
    assert int(kb[0][0].text) == expected1
    assert int(kb[0][4].text) == expected2


testset_deprecated = [
    ({'@': 'dialog_calendar', 'act': 'IGNORE', 'year': '2022', 'month': '8', 'day': '0'}, (None)),
    (
        {'@': 'dialog_calendar', 'act': 'SET-DAY', 'year': '2022', 'month': '8', 'day': '1'},
        (date(2022, 8, 1))
    ),
    (
        {'@': 'dialog_calendar', 'act': 'SET-DAY', 'year': '2021', 'month': '7', 'day': '16'},
        (date(2021, 7, 16))
    ),
    (
        {'@': 'dialog_calendar', 'act': 'SET-DAY', 'year': '1900', 'month': '10', 'day': '8'},
        (date(1900, 10, 8))
    ),
    ({'@': 'dialog_calendar', 'act': 'PREV-YEARS', 'year': '2022', 'month': '8', 'day': '1'}, (None)),
    ({'@': 'dialog_calendar', 'act': 'NEXT-YEARS', 'year': '2021', 'month': '8', 'day': '0'}, (None)),
    ({'@': 'dialog_calendar', 'act': 'SET-MONTH', 'year': '2022', 'month': '8', 'day': '1'}, (None)),
    ({'@': 'dialog_calendar', 'act': 'SET-YEAR', 'year': '2021', 'month': '8', 'day': '0'}, (None)),
    ({'@': 'dialog_calendar', 'act': 'START', 'year': '2021', 'month': '8', 'day': '0'}, (None)),
]


testset = [
    (DialogCalCallback(act=test[0]['act'],
                       year=test[0]['year'],
                       month=test[0]['month'],
                       day=test[0]['day']),
     test[1]) for test in testset_deprecated
]


@pytest.mark.asyncio
@pytest.mark.parametrize("callback_data, expected", testset)
async def test_process_selection(callback_data, expected):
    query = AsyncMock()
    result = await DialogCalendar.process_selection(query=query, data=callback_data)
    assert result == expected
    