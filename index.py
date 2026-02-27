import calendar

# Create an HTMLCalendar instance.
# Optional: set the first day of the week (0=Monday, 6=Sunday).
# Default is Monday (0)
hc = calendar.HTMLCalendar(calendar.MONDAY) 

year = 2025
month = 1

# Generate the HTML for the month
html_calendar_string = hc.formatmonth(year, month)

print(html_calendar_string)
