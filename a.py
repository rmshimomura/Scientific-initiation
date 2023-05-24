from datetime import datetime

dates = ['15/10/20', '27/10/21']

# Convert the dates to datetime objects
date_objects = [datetime.strptime(date, '%d/%m/%y').date() for date in dates]

# Calculate the average date
average_date = datetime.fromordinal(sum(date.toordinal() for date in date_objects) // len(date_objects)).date()

# Convert the average date to the desired format
average_date_formatted = average_date.strftime('%d/%m/%y')

print(average_date_formatted)
