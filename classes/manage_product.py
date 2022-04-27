import csv
import pymorphy2
import random
from config import category_imgs_id, DEFAULT_IMG_ID
import threading
from time import sleep


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
        self.user_product_not_nominative = product
        self.users_products_list = users_products
        print(f"{self.user_product}, {self.user_product_not_nominative} ---------------- ", product)
        self.stop_list = stop_list ##Стоп-лист
        self.title_card = None ##Далее будем использовать для выдачи заголовка для карточки

        self.product_img = None ##Ставим картинку по умолчанию

        with open('products.csv', 'r', encoding='cp1251') as csvfile:
            reader = csv.DictReader(csvfile)
            
            all_products = {}

            #timer = threading.Thread(target=self.timer, args=(), daemon=True)
            #timer.start()
            for row in reader:
                if len(row["Продукт"]) <= len(self.user_product)+3\
                    and row["Продукт"].lower()[0] == self.user_product_not_nominative[0]:

                    all_products[row["Продукт"]] = [row["Вес (г)"], row["Белки"], row["Жиры"], row["Углеводы"], row["Калории"], row["Категория"]]

                if self.__IsAlike(self.user_product, row["Продукт"]) and row["Продукт"] not in self.stop_list\
                    or row["Продукт"].lower() == self.user_product_not_nominative: ##ТУТ БЫЛО ДОБАВЛЕНО ЭТО, РЕШЕНИЕ НЕ 100%, НАДО НЕ ЗАБЫТЬ УЛУЧШИТЬ!!!!!!!
                    self.name = row["Продукт"]
                    self.weight = row["Вес (г)"]
                    self.proteins = row["Белки"] if float(row["Белки"]) > 0.0 else row["Белки"].replace("0.0", "менее 0.1")
                    self.fats = row["Жиры"] if float(row["Жиры"]) > 0.0 else row["Жиры"].replace("0.0", "менее 0.1")
                    self.carbohydrates = row["Углеводы"] if float(row["Углеводы"]) > 0.0 else row["Углеводы"].replace("0.0", "менее 0.1")
                    self.calories = row["Калории"] if float(row["Калории"]) > 0.0 else row["Калории"].replace("0", "менее 0.1")
                    self.category = row["Категория"]

                    ##Картинка категории для отображения в карточке
                    self.product_img = category_imgs_id[self.category.lower()]

                    ##Если продукт совпал напрямую - то в заголовок карточки ставим название из БД
                    if row["Продукт"].lower() == self.user_product_not_nominative:
                        self.title_card = self.user_product_not_nominative.split()[0].title() + " " + " ".join(self.user_product_not_nominative.split()[1::]) + f" ({self.category})" ##Первое слово в продукте делаем с заглавной буквой, далее пишем пробел, далее всё остальное. Потом прибавляем категорию продукта
                    else:
                        self.title_card = self.user_product.split()[0].title() + " " + " ".join(self.user_product.split()[1::]) + f" ({self.category})" ##Первое слово в продукте делаем с заглавной буквой, далее пишем пробел, далее всё остальное. Потом прибавляем категорию продукта

                    break
            
            ##Если до сих пор None - то пробуем пробежаться ещё раз
            if self.name is None:
                print(f"Был не найден продукт: {self.user_product}")
                self.stop_list = []

                ##Если мы прошлись только 1 раз
                #if check == False:
                    #self.__init__(self.user_product, self.stop_list, self.users_products_list, check=True)

                ##Пробегаемся по списку(словарю) всех продуктов, используя расстояние Левенштейна
                for key in all_products:
                    if (self.levenshtein(key, self.user_product) < 3 or self.levenshtein(key, self.user_product_not_nominative) <= 4)\
                        and self.user_product_not_nominative[0] == key[0]:
                        self.name = key
                        self.weight = all_products[key][0]
                        self.proteins = all_products[key][1] if float(all_products[key][1]) > 0.0 else all_products[key][1].replace("0.0", "менее 0.1")
                        self.fats = all_products[key][2] if float(all_products[key][2]) > 0.0 else all_products[key][2].replace("0.0", "менее 0.1")
                        self.carbohydrates = all_products[key][3] if float(all_products[key][3]) > 0.0 else all_products[key][3].replace("0.0", "менее 0.1")
                        self.calories = all_products[key][4] if float(all_products[key][4]) > 0.0 else all_products[key][4].replace("0", "менее 0.1")
                        self.category = all_products[key][5]

                        ##Картинка категории для отображения в карточке
                        self.product_img = category_imgs_id[self.category.lower()]
                        self.title_card = self.name.split()[0].title() + " " + " ".join(self.name.split()[1::]) + f" ({self.category})" ##Первое слово в продукте делаем с заглавной буквой, далее пишем пробел, далее всё остальное. Потом прибавляем категорию продукта
                        break
                
    ##Таймер (на всякий случай)
    def timer(self):
        i = 0
        while True:
            if i >= 2:
                self.beautiful_text()
                return
            i += 1
            sleep(1)

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
        not_to_nominative_words = ["суши", "сливки", "сушки"] ##Слова которые не надо переводить в именительный падеж
        text = text.lower().split(" ")
        morph = pymorphy2.MorphAnalyzer()
        new_text_construct = []

        ##Цикл для того, чтобы все слова в продукте перевести в именительный падеж
        next_skip = False
        for word in range(len(text)):
            try:
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
                    if text[word] in ["с", "со", "к"]:    
                        new_text_construct.append(text[word])
                        next_skip = True
            except:
                new_text_construct.append(text[word])

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
                        f"""В продукте \"{self.user_product}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грам,  калорий: {self.calories} ккал""")
            else:
                return  (f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал""",
                        f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грам, калорий: {self.calories} ккал""")

        ##Если какой-то атрибут равен None (т.е., продукт не был найден) - отсылаем сообщение об ошибке         
        else:
            return (f"Продукт \"{self.user_product_not_nominative}\" не найден...\nВы можете отправить отчёт об ошибке с помощью команды \"Ошибка\"",
                    f"Продукт \"{self.user_product_not_nominative}\ не найден, но вы можете отправить отчёт об ошибке с помощью команды \"Ошибка\"")
    
    ##Метод проверки: есть ли продукт НАЗВАННЫЙ пользователем в списке всех его названных продуктов
    def is_same_in_list(self, product: str, users_products: list) -> bool:
        if product in users_products:
            print(f"Продукт {product} в {users_products}")
            return True
        else:
            print(f"Продукт {product} не в {users_products}")
            return False
    
    ##Считаем бжу продукта на определённый вес
    def calculate(self, weight: str): 
        
        try:
            weight = weight.split()
            weight_for_user = int(weight[0])
            coefficient = (float(weight[0]))/100
        except ValueError: ##Ошибка будет если не был указан вес
            return f"Необходимо указать корректный вес!\nНапример: посчитай {self.user_product_not_nominative} на 100 грамм"

        ##Если продукт БЫЛ НАЙДЕН - осуществляем манипуляции с переменными и выводим бжу на n-грамм продукта
        if self.name != None:
            if "кил" in weight[1] or "кел" in weight[1] or "кг" == weight[1]:
                coefficient *= 1000
                weight_for_user *= 1000

            proteins = round(float(self.proteins) * coefficient, 2)
            fats = round(float(self.fats) * coefficient, 2)
            carbohydrates = round(float(self.carbohydrates) * coefficient, 2)
            calories = int(self.calories) * coefficient

            return (f"В продукте \"{self.name}\" на {weight_for_user} грамм содержится:\n• Белков: {proteins} грамм\n• Жиров: {fats} грамм\n• Углеводов: {carbohydrates} грамм\n• Калорий: {calories} ккал",
                    f"В продукте \"{self.name}\" на {weight_for_user} грамм содержится:\n• Белков: {proteins} грамм\n• Жиров: {fats} грамм\n• Углеводов: {carbohydrates} грамм\n• Калорий: {calories} ккал"
            )
        else: ##Если продукт не был найден - возвращаем это пользователю
            return (f"Продукт \"{self.user_product_not_nominative}\" не найден...\nВы можете отправить отчёт об ошибке с помощью команды \"Ошибка\"",
                    f"Продукт \"{self.user_product_not_nominative}\" не найден...\nВы можете отправить отчёт об ошибке с помощью команды \"Ошибка\""
            )

    ##Метод для возврата заголовка карточки
    def get_title_card(self):
        return self.title_card

    ##Метод для получения списка последних 5 продуктов пользователя
    def get_users_products(self):
        if self.user_product_not_nominative not in self.users_products_list:
            self.users_products_list.append(self.user_product_not_nominative) ##Добавляем в список с продуктами пользователя введённый им продукт

        if len(self.users_products_list) > 5:
            self.users_products_list = []

        return self.users_products_list

    ##Метод для возврата айди картинки
    def get_product_img(self):
        return self.product_img
        
##Класс для поиска продукта по определённым характеристикам
class ProductSearch:
    
    list_of_titles = ["Белки", "Жиры", "Углеводы", "Калории"]
    dict_of_titles_changing = {
        "белки": "белков",
        "жиры": "жиров",
        "углеводы": "углеводов",
        "калории": "килокалорий"
    }
    list_of_categories = ["грибы", "колбасы", "крупы и каши", "масла и жиры", "молочные продукты", "мука и мучные изделия", "хлебобулочные", "мясные продукты", "овощи и зелень", "орехи и сухофрукты", "рыба и морепродукты", "снэки, сыры и творог", "сырье и приправы", "фрукты, ягоды", "яйца", "кондитерские изделия и сладости", "мороженое, торты", "шоколад", "напитки алкогольные", "напитки безалкогольные", "соки и компоты", "салаты, первые блюда", "фастфуд, японская кухня", "детское питание", "спортивное питание"]
    list_of_limits = ["min", "max"]
    
    ##Инициализатор
    def __init__(self, stop_list: list):
        self.product_img = None ##Ставим картинку по умолчанию
        self.stop_list = stop_list

    ##Взятие рандомного продукта из БД
    def random_product(self):
        with open('products.csv', 'r', encoding='cp1251') as csvfile:
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

            with open('products.csv', 'r', encoding='cp1251') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    if row["Категория"] == category:
                        list_by_category.append(row["Продукт"])

            return random.choice(list_by_category)

    ##Поиск по: посоветуй продукт где 100 белков на 100 грамм          
    def search_by_value(self, value:float, category:str, stop_list:list) -> list:
        print(f"На входе: {stop_list}")
        print(category.lower().title(), type(category.lower().title()))

        ##Проверка на категории, на случай, если pymorphy сам не справится (в большинстве случаев)
        if category[0:3] in ["бел", "бил"]:
            category = self.list_of_titles[0].lower()
        elif category[0:3] in ["жир", "жыр"]:
            category = self.list_of_titles[1].lower()
        elif category[0:3] in ["угл", "укл"]:
            category = self.list_of_titles[2].lower()
        elif category[0:3] in ["кал", "кол", "кил", "кел"]:
            category = self.list_of_titles[3].lower()


        if category.lower().title() in self.list_of_titles:

            best_value: float = None
            best_product: str = None
            best_value_of_category: float = None

            with open('products.csv', 'r', encoding='cp1251') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:

                    if best_product is None:
                        best_product = row["Продукт"]
                        best_value = abs(float(row[category.lower().title()]) - value)
                        best_value_of_category = float(row[category.lower().title()])
                        type_of_product = row["Категория"]
      
                    if abs(float(row[category.lower().title()]) - value) < best_value and row["Продукт"] not in stop_list:
                        best_product = row["Продукт"]
                        best_value = abs(float(row[category.lower().title()]) - value)
                        best_value_of_category = float(row[category.lower().title()])
                        type_of_product = row["Категория"]


                stop_list.append(best_product) ##Добавляем название продукта в стоп-лист

                print(f"На выходе: {stop_list}")
                ##Если длина более 5 элементов или же 5 - будем чистить стоп-лист
                if len(stop_list) >= 5:
                    stop_list = []

            title_card = best_product.split()[0].title() + " " + " ".join(best_product.split()[1::])
            ##Возвращаем. 0 - название продукта, 1 - цифра характеристики, 2 - родительный падеж характеристики, 3 - стоп лист
            if self.dict_of_titles_changing[category] == "килокалорий":
                return [
                [title_card, type_of_product],
                int(best_value_of_category),
                self.dict_of_titles_changing[category],
                category_imgs_id[type_of_product],
                stop_list
                ]
            else:
                return [
                [best_product, type_of_product],
                best_value_of_category,
                "грамм " + self.dict_of_titles_changing[category],
                category_imgs_id[type_of_product],
                stop_list
                ]


    def search_by_limit(self, limit:str = "max", title:str = "Калории") -> list:
        
        if title.lower().title() in self.list_of_titles and limit.lower() in self.list_of_limits:
            
            best_product: str = None
            best_value: float = None
                
            with open('products.csv', 'r', encoding='cp1251') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if (best_product is None) or (limit.lower() == "max" and float(best_value) < float(row[title.lower().title()])) or (limit.lower() == "min" and float(best_value) > float(row[title.lower().title()])):
                        best_product = row["Продукт"]
                        best_value = float(row[title.lower().title()])
                        
            return [best_product, best_value]

    ##Метод для удаления всех слов, кроме количества какой-либо характеристики
    def remove_all_in_specification(self, text: str):
        text = text.split()
        new_text_construct = [] ##Сюда будем класть количество(цифру) и характеристику

        digit_index = None
        for word in range(len(text)):
            if text[word].replace(".", "").replace(",", "").isdigit():
                if len(new_text_construct) > 0:
                    new_text_construct.insert(0, text[word])
                    new_text_construct.pop()
                else:
                    new_text_construct.insert(0, text[word])

                digit_index = word

        for word in text[digit_index::]:
                if word[0] in "бжук":
                    new_text_construct.append(word)
                    break

        for word in new_text_construct:
            if not word.isdigit() and word[0:3] not in ["бел", "бил", "жир", "жыр", "угл", "укл", "кал", "кол", "кил", "кел"]:
                new_text_construct.remove(word)

        text = " ".join(new_text_construct)
        new_text_construct = []

        ##Здесь начинаем переводить в именительный падеж
        morph = pymorphy2.MorphAnalyzer()

        for word in text.split():
            if not word.replace(".", "").replace(",", "").isdigit():
                butyavka = morph.parse(word)[0]
                gent = butyavka.inflect({'nomn'})
                new_text_construct.append(gent.word)
            else:
                new_text_construct.append(word)

        return " ".join(new_text_construct)

    ##Метод для возвращения красивого текста
    def beautiful_text(self):
        return f"""В продукте \"{self.name}\" на {self.weight} грамм содержится: белков: {self.proteins} грамм, жиров: {self.fats} грамм, углеводов: {self.carbohydrates} грамм, калорий: {self.calories} ккал"""

    ##Метод для возврата картинки
    def get_product_img(self):
        return self.product_img