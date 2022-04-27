import csv

with open("products.csv", "r", encoding='cp1251') as file:
	reader = csv.DictReader(file)

	for line in reader:
		print("line: ", line)