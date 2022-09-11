import datetime

print(datetime.datetime.now())

with open('time.txt','w') as file:
	date_time = datetime.datetime.now()
	date_time = date_time.replace(day=1)
	file.write(date_time.strftime("%d-%b-%Y (%H:%M:%S.%f)"))

with open('time.txt', 'r') as file:
	date_time = datetime.datetime.strptime(file.read(), "%d-%b-%Y (%H:%M:%S.%f)")
	print(date_time)
