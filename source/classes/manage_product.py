import csv
import pymorphy2
import random
from config import category_imgs_id

##Класс с информацией о продукте
class InfoProduct():
    
    name: str = None #Название продукта
    weight: float = None #Вес 
    proteins: float = None #Белки
    fats: float = None #Жиры
    carbohydrates: float = None #Углеводы
    calories: float = None #Калории
    category: str = None ##Категория
    product_img: str = None ##Картинка
    
    def __init__(self, product: str, stop_list): #Инициализация объекта (конструктор)
        self.user_product = self.__go_to_nominative(product.lower()) ##Далее будет использовано в методе .beautiful_text()
        self.stop_list = stop_list

        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile) 
            for row in reader: 
                if self.__IsAlike(self.user_product, row["Продукт"]) and row["Продукт"] not in self.stop_list:
                    self.name = row["Продукт"]
                    self.weight = row["Вес (г)"]
                    self.proteins = row["Белки"]
                    self.fats = row["Жиры"]
                    self.carbohydrates = row["Углеводы"]
                    self.calories = row["Калории"]
                    self.category = row["Категория"]

                    ##Картинка категории для отображения в карточке
                    self.product_img = category_imgs_id[self.category.lower()]
                    break

            if self.name is None:
                self.stop_list = []

                self.__init__(self.user_product, self.stop_list)

                for row in reader:
                    if self.user_product.lower() in row["Продукт"].split(" ")[0] or self.user_product.lower() in row["Продукт"]:
                        self.name = row["Продукт"]
                        self.weight = row["Вес (г)"]
                        self.proteins = row["Белки"]
                        self.fats = row["Жиры"]
                        self.carbohydrates = row["Углеводы"]
                        self.calories = row["Калории"]
                        self.category = row["Категория"]
                        break
    
    def __IsAlike(self, userinput: str, product: str) -> bool:
    
        _userinput_arr = userinput.lower().split(" ")
        _product_arr = product.lower().split(" ")
    
        for i in _userinput_arr:
            if i in _product_arr:
                continue
            else:
                return False
    
        return True
    
    ##Метод возвращающий слово в именительном падеже
    def __go_to_nominative(self, word_to_nominative):
        morph = pymorphy2.MorphAnalyzer()
        new_word_construct = []

        ##Цикл для того, чтобы все слова в продукте перевести в именительный падеж
        for i in word_to_nominative.split(" "):
            word = morph.parse(i)[0]
            new_word = word.inflect({'nomn'}) ##Переводим слово из косвенного падежа в именительный
            if new_word is None:
                return word_to_nominative
            else:
                new_word_construct.append(new_word.word)

        return " ".join(new_word_construct).replace("ё", "е") ##Возвращаем слово в именительном падеже

    def get_json(self) -> dict: #Метод, создающий json с полями класса
        return {
            "Продукт" : self.name,
            "Вес (г)" : self.weight,
            "Белки" : self.proteins,
            "Жиры" : self.fats,
            "Углеводы" : self.carbohydrates,
            "Калории" : self.calories,
            "Категория" : self.category
        } 

    ##Метод для красивого вывода текста или уведомления о ненаходе продукта
    def beautiful_text(self) -> str:
        if None not in (self.name, self.proteins, self.fats, self.carbohydrates, self.calories, self.category):
            return  (f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал""",
                    f"""В продукте \"{self.user_product}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал""")
        else:
            return (f"Продукт \"{self.user_product}\" не найден...\nВы можете отправить отчёт об ошибке с помощью команды \"Ошибка\"",
                    f"Продукт \"{self.user_product}\ не найден, но вы можете отправить отчёт об ошибке с помощью команды \"Ошибка\"")
    
    ##Метод для возврата айди картинки
    def get_product_img(self):
        return self.product_img
        
##Класс для поиска продукта по определённым характеристикам
class ProductSearch():
    
    list_of_titles = ["Белки", "Жиры", "Углеводы", "Калории"]
    list_of_categories = ["грибы", "колбасы", "крупы и каши", "масла и жиры", "молочные продукты", "мука и мучные изделия", "мясные продукты", "овощи и зелень", "орехи и сухофрукты", "рыба и морепродукты", "снэки, сыры и творог", "сырье и приправы", "фрукты, ягоды", "яйца", "кондитерские изделия и сладости", "мороженое, торты", "шоколад", "напитки алкогольные", "напитки безалкогольные", "соки и компоты", "салаты, первые блюда", "фастфуд, японская кухня", "детское питание", "спортивное питание"]
    list_of_limits = ["min", "max"]

    def random_product(self):
        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile)

            all_rows = 1
            for row in reader:
                all_nums += 1

            random_num = random.randint(1, all_nums)

            num = 1
            for row in reader:
                if num == random_num:
                    return [
                    row["Продукт"], 
                    row["Вес (г)"], 
                    row["Белки"], 
                    row["Жиры"], 
                    row["Углеводы"], 
                    row["Калории"], 
                    row["Категория"]
                    ]
                num += 1


    def random_product_by_category(self, category: str) -> str:
        if category.lower() in self.list_of_categories:
            list_by_category = []

            with open('products.csv') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    if row["Категория"] == category:
                        list_by_category.append(row["Продукт"])

            return random.choice(list_by_category)
                    
    def search_by_value(self, value:float, title:str = "Калории") -> list:

        if title.lower().title() in self.list_of_titles:
            
            best_value: float = None
            best_product: str = None
            best_value_of_title: float = None

            with open('products.csv') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if (abs(float(row[title.lower().title()]) - value) < best_value) or (best_product is None):
                        best_product = row["Продукт"]
                        best_value = abs(float(row[title.lower().title()]) - value)
                        best_value_of_title = float(row[title.lower().title()])
                                
            return [best_product, best_value_of_title]


    def search_by_limit(self, limit:str = "max", title:str = "Калории") -> list:
        
        if title.lower().title() in self.list_of_titles and limit.lower() in self.list_of_limits:
            
            best_product: str = None
            best_value: float = None
                
            with open('products.csv') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if (best_product is None) or (limit.lower() == "max" and float(best_value) < float(row[title.lower().title()])) or (limit.lower() == "min" and float(best_value) > float(row[title.lower().title()])):
                        best_product = row["Продукт"]
                        best_value = float(row[title.lower().title()])
            return [best_product, best_value]
