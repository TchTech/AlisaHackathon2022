import csv
import pymorphy2

##Класс с информацией о продукте
class InfoProduct():
    
    name: str = None #Название продукта
    weight: float = None #Вес 
    proteins: float = None #Белки
    fats: float = None #Жиры
    carbohydrates: float = None #Углеводы
    calories: float = None #Калории
    
    def __init__(self, product: str): #Инициализация объекта (конструктор)
        self.user_product = self.__go_to_nominative(product.lower()) ##Далее будет использовано в методе .beautiful_text()
        
        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile) 
            for row in reader:
                #for i in row["Продукт"].split():
                    #if product == i:
            
                if self.__IsAlike(self.user_product, row["Продукт"]):
                    self.name = row["Продукт"]
                    self.weight = row["Вес (г)"]
                    self.proteins = row["Белки"]
                    self.fats = row["Жиры"]
                    self.carbohydrates = row["Углеводы"]
                    self.calories = row["Калории"]
                    #self.category = row["Категория"]
                    break

            if self.name is None:
                for row in reader:
                    if self.user_product.lower() in row["Продукт"].split(" ")[0] or self.user_product.lower() in row["Продукт"]:
                        self.name = row["Продукт"]
                        self.weight = row["Вес (г)"]
                        self.proteins = row["Белки"]
                        self.fats = row["Жиры"]
                        self.carbohydrates = row["Углеводы"]
                        self.calories = row["Калории"]
                        #self.category = row["Категория"]
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
            #"Категория" : self.category
        } 

    ##Метод для красивого вывода текста или уведомления о ненаходе продукта
    def beautiful_text(self) -> str:
        if None not in (self.name, self.proteins, self.fats, self.carbohydrates, self.calories):
            return  f"В продукте \"{self.name}\" на {self.weight} грамм содержится:\n• Белков: {self.proteins} грамм\n• Жиров: {self.fats} грамм\n• Углеводов: {self.carbohydrates} грамм\n• Калорий: {self.calories} ккал"
        else:
            return f"Продукт \"{self.user_product}\" не найден..."
        
##Класс для поиска продукта по определённым характеристикам
class ProductSearch():
    
    list_of_categories = ["Белки", "Жиры", "Углеводы", "Калории"]
    list_of_limits = ["min", "max"]
                    
    def search_by_value(self, value:float, category:str = "Калории") -> list:

        if category.lower().title() in self.list_of_categories:
            
            best_value: float = None
            best_product: str = None
            best_value_of_category: float = None

            with open('products.csv') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if (abs(float(row[category.lower().title()]) - value) < best_value) or (best_product is None):
                        best_product = row["Продукт"]
                        best_value = abs(float(row[category.lower().title()]) - value)
                        best_value_of_category = float(row[category.lower().title()])
                                
            return [best_product, best_value_of_category]

        else:
            return ["Категория не найдена!", 0]

    def search_by_limit(self, limit:str = "max", category:str = "Калории") -> list:
        
        if category.lower().title() in self.list_of_categories and limit.lower() in self.list_of_limits:
            
            best_product: str = None
            best_value: float = None
                
            with open('products.csv') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if (best_product is None) or (limit.lower() == "max" and float(best_value) < float(row[category.lower().title()])) or (limit.lower() == "min" and float(best_value) > float(row[category.lower().title()])):
                        best_product = row["Продукт"]
                        best_value = float(row[category.lower().title()])
            return [best_product, best_value]
        else:
            return ["Указанной категории не существует или указанный лимит неверный", 0]
