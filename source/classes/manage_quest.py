import random
import csv

##Класс с квестом
class Quest():
    list_of_titles = ["белков", "жиров", "углеводов", "калорий"]
    list_of_titles_im = ["Белки", "Жиры", "Углеводы", "Калории"]
    list_of_limits = ["большим", "маленьким"]

    ##Инициализатор с определениями важных переменных
    def __init__(self):
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

    def PrintRules(self):
        return [
            f"Алиса хочет съесть продукт с {self.lim} содержанием {self.list_of_titles[self.index_of_category]}. Что ей лучше съесть?\n1. {self.first['Продукт']}\n2. {self.second['Продукт']}\n3. {self.thirth['Продукт']}",
            f"Алиса хочет съесть продукт с {self.lim} содержанием {self.list_of_titles[self.index_of_category]}. Что ей лучше съесть?\nпервое. {self.first['Продукт']}\nвторое. {self.second['Продукт']}\nтретье. {self.thirth['Продукт']}"
        ]

    ##Проверка введённого текста пользователем на правильный ответ
    def IsRightAnswer(self, answer: str) -> list:
        
        for i in answer.lower().split():
            if i in self.right_answer["Продукт"].split():
                return [True, "Молодец, ты правильно угадал!"]
        
        return [False, f"Неправильно! Правильный ответ: {self.right_answer['Продукт']}, в нем содержится {self.right_answer[self.list_of_titles_im[self.index_of_category]]} {self.list_of_titles[self.index_of_category]} на 100 грамм."]

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

    ##Геттер для правильного ответа
    def get_right_answer(self):
        return self.right_answer

    ##Геттер для кнопок ответов
    def get_buttons_answers(self):
        return [
            {"title": self.first["Продукт"].split()[0].title(), "hide": False},
            {"title": self.second["Продукт"].split()[0].title(), "hide": False},
            {"title": self.thirth["Продукт"].split()[0].title(), "hide": False},
            {"title": "Покинуть квест", "hide": True}
        ]