import csv
import pymorphy2
import random
from config import category_imgs_id, DEFAULT_IMG_ID

##Класс с информацией о продукте
class InfoProduct:
    
    name: str = None #Название продукта
    weight: float = None #Вес 
    proteins: float = None #Белки
    fats: float = None #Жиры
    carbohydrates: float = None #Углеводы
    calories: float = None #Калории
    category: str = None ##Категория
    product_img: str = None ##Картинка
    
    def __init__(self, product: str, stop_list: list, users_products: list, check=False): #Инициализация объекта (конструктор)
        self.user_product = self.__go_to_nominative(product.lower()) ##Далее будет использовано в методе .beautiful_text()
        self.users_products_list = users_products
        self.stop_list = stop_list ##Стоп-лист

        self.product_img = None ##Ставим картинку по умолчанию

        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            
            all_products = {}

            for row in reader:
                all_products[row["Продукт"]] = [row["Вес (г)"], row["Белки"], row["Жиры"], row["Углеводы"], row["Калории"], row["Категория"]]
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
            
            ##Если до сих пор None - то пробуем пробежаться ещё раз
            if self.name is None:
                print(f"Был не найден продукт: {self.user_product}")
                self.stop_list = []

                ##Если мы прошлись только 1 раз
                if check == False:
                    self.__init__(self.user_product, self.stop_list, self.users_products_list, check=True)

                ##Пробегаемся по списку(словарю) всех продуктов, используя расстояние Левенштейна
                for key in all_products:
                    if self.levenshtein(key, self.user_product) < 6:
                        self.name = key
                        self.weight = all_products[key][0]
                        self.proteins = all_products[key][1]
                        self.fats = all_products[key][2]
                        self.carbohydrates = all_products[key][3]
                        self.calories = all_products[key][4]
                        self.category = all_products[key][5]

                        ##Картинка категории для отображения в карточке
                        self.product_img = category_imgs_id[self.category.lower()]
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
    def __go_to_nominative(self, text):
        not_to_nominative_words = ["суши", "сливки"] ##Слова которые не надо переводить в именительный падеж
        text = text.lower().split(" ")
        morph = pymorphy2.MorphAnalyzer()
        new_text_construct = []

        ##Цикл для того, чтобы все слова в продукте перевести в именительный падеж
        next_skip = False
        for word in range(len(text)):
                
            if text[word] in not_to_nominative_words:
                new_text_construct.append(text[word])
                continue

            if next_skip == True:
                new_text_construct.append(text[word])
                continue

            if len(text[word]) > 1:
                butyavka = morph.parse(text[word])[0]
                gent = butyavka.inflect({'nomn'})
                new_text_construct.append(gent.word)
            else:
                if text[word] in ["с", "со"]:    
                    new_text_construct.append(text[word])
                    next_skip = True

        return " ".join(new_text_construct).replace("ё", "е") ##Возвращаем слово в именительном падеже


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

    ##Метод с расстоянием Левенштейна
    def levenshtein(self, a: str, b: str):
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n, m)) space
            a, b = b, a
            n, m = m, n

        current_row = range(n + 1)  # Keep current and previous row, not entire matrix
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[n]

    ##Метод для красивого вывода текста или уведомления о ненаходе продукта
    def beautiful_text(self) -> str:

        ##Если ни один атрибут не равен None (т.е., продукт был найден) - отсылаем сообщение с информацией. Нулевой индекс - текст (с названием продукта из БД). Второй индекс - голосовй текст с названием продукта, как сказал пользователь
        if None not in (self.name, self.proteins, self.fats, self.carbohydrates, self.calories, self.category):
            
            ##Если названный продукт уже есть в списке продуктов
            if self.is_same_in_list(self.user_product, self.users_products_list) != True:
                return  (f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал""",
                        f"""В продукте \"{self.user_product}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал""")
            else:
                return  (f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал""",
                        f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал""")

        ##Если какой-то атрибут равен None (т.е., продукт не был найден) - отсылаем сообщение об ошибке         
        else:
            return (f"Продукт \"{self.user_product}\" не найден...\nВы можете отправить отчёт об ошибке с помощью команды \"Ошибка\"",
                    f"Продукт \"{self.user_product}\ не найден, но вы можете отправить отчёт об ошибке с помощью команды \"Ошибка\"")
    
    ##Метод проверки: есть ли продукт НАЗВАННЫЙ пользователем в списке всех его названных продуктов
    def is_same_in_list(self, product: str, users_products: list) -> bool:
        if product in users_products:
            return True
        else:
            return False

    ##Метод очистки списка всех продуктов пользователя
    def clear_users_products(self, users_products: list) -> list:

        ##Если длина всех названных продуктов превышает 5 - чистим
        if len(users_products) > 5:
            users_products = []
        
        return users_products

    ##Метод для возврата айди картинки
    def get_product_img(self):
        return self.product_img
        
##Класс для поиска продукта по определённым характеристикам
class ProductSearch:
    
    list_of_titles = ["Белки", "Жиры", "Углеводы", "Калории"]
    list_of_categories = ["грибы", "колбасы", "крупы и каши", "масла и жиры", "молочные продукты", "мука и мучные изделия", "хлебобулочные", "мясные продукты", "овощи и зелень", "орехи и сухофрукты", "рыба и морепродукты", "снэки, сыры и творог", "сырье и приправы", "фрукты, ягоды", "яйца", "кондитерские изделия и сладости", "мороженое, торты", "шоколад", "напитки алкогольные", "напитки безалкогольные", "соки и компоты", "салаты, первые блюда", "фастфуд, японская кухня", "детское питание", "спортивное питание"]
    list_of_limits = ["min", "max"]
    
    ##Инициализатор
    def __init__(self, stop_list: list):
        self.product_img = None ##Ставим картинку по умолчанию
        self.stop_list = stop_list

    ##Взятие рандомного продукта из БД
    def random_product(self):
        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile)

            list_all_products = [] ##Сюда мы занесём все продукты
            for row in reader:
                list_all_products.append([row["Продукт"], row["Вес (г)"], row["Белки"], row["Жиры"], row["Углеводы"], row["Калории"], row["Категория"]])

            random_product = random.choice(list_all_products) ##Выбираем случайный продукт из списка всех продуктов
            if random_product in self.stop_list: ##Если случайный продукт есть в стоп-листе
                random_product = list_all_products[list_all_products.index(random_product)-1]

            self.name, self.weight, self.proteins, self.fats, self.carbohydrates, self.calories, self.category = random_product
            self.product_img = category_imgs_id[self.category.lower()]
            return (self.beautiful_text(), self.get_product_img())

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

    ##Метод для возвращения красивого текста
    def beautiful_text(self):
        return f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал"""

    ##Метод для возврата картинки
    def get_product_img(self):
        return self.product_img