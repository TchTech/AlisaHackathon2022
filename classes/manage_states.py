import re

class States:
	def __init__(self):
		self.process_recommends = False

		self.say_sex = False
		self.say_age = False
		self.say_weight = False
		self.say_growth = False

		self.states_list = [self.say_sex, self.say_age, self.say_weight, self.say_growth]

		self.correctly_sex = None
		self.correctly_age = None
		self.correctly_weight = None
		self.correctly_growth = None


	def next(self):
		# определим индекс активного state
		index_active = None
		for attr in range(len(self.states_list)):
			if attr == True:
				index_active = attr
				break

		# изменим текущий на False, следующий на True
		for attr in range(len(self.states_list[index_active::])):
			if self.states_list[attr] == True and attr != len(self.states_list[index_active::]):
				self.states_list[attr] = False
				self.states_list[attr+1] = True
				break

	# запрос пола
	def ask_sex(self):
		sex = input("Скажи свой пол: ").lower()

		if sex[0] == "м":
			self.correctly_sex = re.findall(r"муж.{0,}", sex)[0]
		elif sex[0] == "ж":
			self.correctly_sex = re.findall(r"жен.{0,}", sex)[0]

		self.next()
		print(self.states_list)

	# запрос возраста
	def ask_age(self):
		age = input("Скажи свой возраст: ").lower()

		if age.isdigit():
			self.correctly_age = int(age)

		self.next()
		print(self.states_list)

	# запрос веса
	def ask_weight(self):
		weight = input("Скажи свой вес: ").lower()

		if weight.replace(".", "").isdigit():
			self.correctly_weight = float(weight)

		self.next()
		print(self.states_list)

	# запрос роста
	def ask_growth(self):
		# запрос роста
		growth = input("Скажи свой рост: ").lower()

		if growth.replace(".", "").isdigit():
			self.correctly_growth = float(growth)

		self.next()
		print(self.states_list)


	# возвращаем введённое
	def get_all(self):
		# печатаем
		print(f"Ваш пол: {self.correctly_sex}")
		print(f"Ваш возраст: {self.correctly_age}")
		print(f"Ваш вес: {self.correctly_weight}")
		print(f"Ваш рост: {self.correctly_growth}")

	# обнуляем состояния
	def reset_all(self):
		self.say_sex = True
		self.say_age = False
		self.say_weight = False
		self.say_growth = False

		self.correctly_sex = None
		self.correctly_age = None
		self.correctly_weight = None
		self.correctly_growth = None