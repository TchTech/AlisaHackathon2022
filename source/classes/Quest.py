import random
import csv

class Quest():
    list_of_titles = ["белков", "жиров", "углеводов", "калорий"]
    list_of_titles_im = ["Белки", "Жиры", "Углеводы", "Калории"]
    list_of_limits = ["большим", "маленьким"]

    def PrintRules(self):
        self.index_of_category = random.randint(0, 3)
        self.lim = random.choice(self.list_of_limits)


        self.first = self.__randomizer()
        self.second = self.__randomizer()
        self.thirth = self.__randomizer()


        self.right_answer = None


        while self.right_answer is None:

            if self.lim == "большим":
                if self.first[self.list_of_titles_im[self.index_of_category]] > self.second[self.list_of_titles_im[self.index_of_category]] and self.first[self.list_of_titles_im[self.index_of_category]] > self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.first
                elif self.second[self.list_of_titles_im[self.index_of_category]] > self.first[self.list_of_titles_im[self.index_of_category]] and self.second[self.list_of_titles_im[self.index_of_category]] > self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.second
                elif self.thirth[self.list_of_titles_im[self.index_of_category]] > self.first[self.list_of_titles_im[self.index_of_category]] and self.thirth[self.list_of_titles_im[self.index_of_category]] > self.second[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.thirth
                else:
                    self.first = self.__randomizer()
                    self.second = self.__randomizer()
                    self.thirth = self.__randomizer()

            elif self.lim == "маленьким":
                if self.first[self.list_of_titles_im[self.index_of_category]] < self.second[self.list_of_titles_im[self.index_of_category]] and self.first[self.list_of_titles_im[self.index_of_category]] < self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.first
                elif self.second[self.list_of_titles_im[self.index_of_category]] < self.first[self.list_of_titles_im[self.index_of_category]] and self.second[self.list_of_titles_im[self.index_of_category]] < self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.second
                elif self.thirth[self.list_of_titles_im[self.index_of_category]] < self.first[self.list_of_titles_im[self.index_of_category]] and self.thirth[self.list_of_titles_im[self.index_of_category]] < self.second[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.thirth
                else:
                    self.first = self.__randomizer()
                    self.second = self.__randomizer()
                    self.thirth = self.__randomizer()



        return f"Алиса хочет съесть продукт с {self.lim} содержанием {self.list_of_titles[self.index_of_category]}. Что ей лучше съесть?\n1. {self.first['Продукт']}\n2. {self.second['Продукт']}\n3. {self.thirth['Продукт']}"

    def IsRightAnswer(self, answer):

        if answer.lower() in self.right_answer["Продукт"]:
            return "Молодец, ты правильно угадал!"
        else:
            return f"Неправильно! Правильный ответ: {self.right_answer['Продукт']}, в нем содержится {self.right_answer[self.list_of_titles_im[self.index_of_category]]} {self.list_of_titles[self.index_of_category]}"

    def __randomizer(self):
        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile)

            list_all_products = [] ##Сюда мы занесём все продукты
            for row in reader:
                list_all_products.append({
                    "Продукт": row["Продукт"], 
                    "Вес (г)" : row["Вес (г)"], 
                    "Белки": row["Белки"], 
                    "Жиры": row["Жиры"], 
                    "Углеводы": row["Углеводы"], 
                    "Калории": row["Калории"], 
                    "Категория": row["Категория"]
                    })

            return random.choice(list_all_products)##Выбираем случайный продукт из списка всех продуктов


for i in range(100):
    quest = Quest()
    print(quest.PrintRules())
    print("\n")
    print(quest.IsRightAnswer(input("Введи ответ:")))
    print("\n\n")

input()

