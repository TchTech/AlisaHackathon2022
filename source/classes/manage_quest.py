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
                if self.first[self.list_of_titles_im[self.index_of_category]] > self.second[self.list_of_titles_im[self.index_of_category]]\
                and self.first[self.list_of_titles_im[self.index_of_category]] > self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.first
                elif self.second[self.list_of_titles_im[self.index_of_category]] > self.first[self.list_of_titles_im[self.index_of_category]]\
                and self.second[self.list_of_titles_im[self.index_of_category]] > self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.second
                elif self.thirth[self.list_of_titles_im[self.index_of_category]] > self.first[self.list_of_titles_im[self.index_of_category]]\
                and self.thirth[self.list_of_titles_im[self.index_of_category]] > self.second[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.thirth
                else:
                    while self.first["Продукт"].split()[0] == self.second["Продукт"].split()[0]\
                    or self.first["Продукт"].split()[0] == self.thirth["Продукт"].split()[0]:
                        self.first = self.__randomizer()
                        self.second = self.__randomizer()
                        self.thirth = self.__randomizer()

            elif self.lim == "маленьким":
                if self.first[self.list_of_titles_im[self.index_of_category]] < self.second[self.list_of_titles_im[self.index_of_category]]\
                and self.first[self.list_of_titles_im[self.index_of_category]] < self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.first
                elif self.second[self.list_of_titles_im[self.index_of_category]] < self.first[self.list_of_titles_im[self.index_of_category]]\
                and self.second[self.list_of_titles_im[self.index_of_category]] < self.thirth[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.second
                elif self.thirth[self.list_of_titles_im[self.index_of_category]] < self.first[self.list_of_titles_im[self.index_of_category]]\
                and self.thirth[self.list_of_titles_im[self.index_of_category]] < self.second[self.list_of_titles_im[self.index_of_category]]:
                    self.right_answer = self.thirth
                else:
                    while self.first["Продукт"].split()[0] == self.second["Продукт"].split()[0]\
                    or self.first["Продукт"].split()[0] == self.thirth["Продукт"].split()[0]:
                        self.first = self.__randomizer()
                        self.second = self.__randomizer()
                        self.thirth = self.__randomizer()

            while self.first["Продукт"].split()[0] == self.second["Продукт"].split()[0]\
            or self.first["Продукт"].split()[0] == self.thirth["Продукт"].split()[0]:
                self.first = self.__randomizer()
                self.second = self.__randomizer()
                self.thirth = self.__randomizer()

    ##Выводим на запись вступление
    def PrintRules(self):
        return [
            f"Алиса хочет съесть продукт с {self.lim} содержанием {self.list_of_titles[self.index_of_category]}. Что ей лучше съесть?\n1. {self.first['Продукт']}\n2. {self.second['Продукт']}\n3. {self.thirth['Продукт']}",
            f"Алиса хочет съесть продукт с {self.lim} содержанием {self.list_of_titles[self.index_of_category]}. Что ей лучше съесть?\nпервое. {self.first['Продукт']}\nвторое. {self.second['Продукт']}\nтретье. {self.thirth['Продукт']}"
        ]

    ##Проверка введённого текста пользователем на правильный ответ
    def IsRightAnswer(self, answer: str) -> list:
        
        for i in answer.lower().split():
            if i in self.right_answer["Продукт"].replace("-", " ").split():
                return [True,
                "Молодец, ты правильно угадал!",
                [{"title": f"Расскажи про {self.right_answer['Продукт']}"}]
                ]
        
        return [False,
        f"Неправильно! Правильным был ответ: {self.right_answer['Продукт']}, в данном продукте содержится {self.right_answer[self.list_of_titles_im[self.index_of_category]]} {self.list_of_titles[self.index_of_category]} на 100 грамм.",
        [{"title": f"Расскажи про {self.right_answer['Продукт']}"}]
        ]

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
        txt_first_btn = self.first["Продукт"].split()[0].title()
        txt_second_btn = self.second["Продукт"].split()[0].title()
        txt_thirth_btn = self.thirth["Продукт"].split()[0].title()

        ##Окончания прилагательных кладём в список
        adject_endings = ["ой", "ий", "ый", "ая", "ья", "ое", "ее", "ье", "ые", "ие", "ьи"]

        ##Проверки для того, чтобы не отобразить пользователю одно лишь прилагательное
        if txt_first_btn.endswith("ой") or txt_first_btn.endswith("ий")\
        or txt_first_btn.endswith("ый") or txt_first_btn.endswith("ая")\
        or txt_first_btn.endswith("ое") or txt_first_btn.endswith("ее")\
        or txt_first_btn.endswith("ие") or txt_first_btn.endswith("ые")\
        or txt_first_btn.endswith("ья") and self.first["Продукт"].split()[1][-2::] not in adject_endings\
        or txt_first_btn.endswith("ье") and self.first["Продукт"].split()[1][-2::] not in adject_endings\
        or txt_first_btn.endswith("ьи") and self.first["Продукт"].split()[1][-2::] not in adject_endings:

            txt_first_btn += f" {self.first['Продукт'].split()[1]}"

        if txt_second_btn.endswith("ой") or txt_second_btn.endswith("ий")\
        or txt_second_btn.endswith("ый") or txt_second_btn.endswith("ая")\
        or txt_second_btn.endswith("ое") or txt_second_btn.endswith("ее")\
        or txt_second_btn.endswith("ие") or txt_second_btn.endswith("ые")\
        or txt_second_btn.endswith("ья") and self.second["Продукт"].split()[1][-2::] not in adject_endings\
        or txt_second_btn.endswith("ье") and self.second["Продукт"].split()[1][-2::] not in adject_endings\
        or txt_second_btn.endswith("ьи") and self.second["Продукт"].split()[1][-2::] not in adject_endings:

            txt_second_btn += f" {self.second['Продукт'].split()[1]}"


        if txt_thirth_btn.endswith("ой") or txt_thirth_btn.endswith("ий")\
        or txt_thirth_btn.endswith("ый") or txt_thirth_btn.endswith("ая")\
        or txt_thirth_btn.endswith("ое") or txt_thirth_btn.endswith("ее")\
        or txt_thirth_btn.endswith("ие") or txt_thirth_btn.endswith("ые")\
        or txt_thirth_btn.endswith("ья") and self.thirth["Продукт"].split()[1][-2::] not in adject_endings\
        or txt_thirth_btn.endswith("ье") and self.thirth["Продукт"].split()[1][-2::] not in adject_endings\
        or txt_thirth_btn.endswith("ьи") and self.thirth["Продукт"].split()[1][-2::] not in adject_endings:

            txt_thirth_btn += f" {self.thirth['Продукт'].split()[1]}"
        
        ##Возвращаем в виде списка со словарями
        return [
            {"title": txt_first_btn, "hide": False},
            {"title": txt_second_btn, "hide": False},
            {"title": txt_thirth_btn, "hide": False},
            {"title": "Покинуть квест", "hide": True}
        ]