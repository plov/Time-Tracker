import calendar
from typing import Iterable, List, Tuple
from datetime import date, datetime, timedelta


class CalendarLogic:

    MONTHS = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    @staticmethod
    def setFirsDayOfWeek(weekday: int) -> None:
        calendar.setfirstweekday(weekday)

    @staticmethod
    def convertMonthToNumber(month) -> int:
        if month in CalendarLogic.MONTHS:
            return CalendarLogic.MONTHS.index(month) + 1
        else:
            return 0

    @staticmethod
    def previousMonthAndYear(year: int, month: int) -> Tuple[int, int]:
        previousMonthDate = date(year, month, 1) - timedelta(days = 2)
        return previousMonthDate.month, previousMonthDate.year

    @staticmethod
    def nextMonthAndYear(year: int, month: int) -> Tuple[int, int]:
        lastDayOfMonth = calendar.monthrange(year, month)[1]
        nextMonthDate = date(year, month, lastDayOfMonth) + timedelta(days = 2)
        return nextMonthDate.month, nextMonthDate.year

    @staticmethod
    def current_date() -> Tuple[int, int, int]:
        today_date = datetime.date(datetime.now())
        return today_date.day, today_date.month, today_date.year

    @staticmethod
    def month_days(year: int, month: int) -> Iterable[date]:
        return calendar.Calendar(calendar.firstweekday()).itermonthdates(year, month)

    @staticmethod
    def month_days_with_weekday(year: int, month: int) -> List[List[int]]:
        return calendar.Calendar(calendar.firstweekday()).monthdayscalendar(year, month)