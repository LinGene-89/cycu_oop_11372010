# create a list fill with weekdays from Monday to Sunday
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#create a list fill with Month from January to December
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


# get user input for the month
month = input('Enter the month: ')
# print the English name of the month from the list
print(months[int(month) - 1])