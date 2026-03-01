import datetime
today = datetime.datetime.now()
month_start = datetime.datetime(today.year,today.month,1)
print(month_start.strftime("%w"))

calander = {}

for day in range(1, 32):
    calander[day] = day

print(calander)
import calendar

month = calendar.monthcalendar(2026, 3)
print(month)
