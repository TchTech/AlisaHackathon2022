import csv

class InfoProduct():
    
    name: str = None #Название продукта
    weight: float = None #Вес 
    proteins: float = None #Белки
    fats: float = None #Жиры
    carbohydrates: float = None #Углеводы
    calories: float = None #Калории
    
    def __init__(self, product: str): #Инициализация объекта (конструктор)
        self.user_product = product ##Далее будет использовано в методе .beautiful_text()
        
        with open('products.csv') as csvfile:
            reader = csv.DictReader(csvfile) 
            for row in reader: 
                if product.lower() in row["Продукт"].split(" ")[0]:
                    self.name = row["Продукт"]
                    self.weight = row["Вес (г)"]
                    self.proteins = row["Белки"]
                    self.fats = row["Жиры"]
                    self.carbohydrates = row["Углеводы"]
                    self.calories = row["Калории"]
                    break

    def get_json(self) -> dict: #Метод, создающий json с полями класса
        return {
            "Продукт" : self.name,
            "Вес (г)" : self.weight,
            "Белки" : self.proteins,
            "Жиры" : self.fats,
            "Углеводы" : self.carbohydrates,
            "Калории" : self.calories
        } 

    def beautiful_text(self) -> str:
        if None not in (self.name, self.proteins, self.fats, self.carbohydrates, self.calories):
            return  f"В продукте \"{self.name}\" содержится:\n•Белков: {self.proteins}\n•Жиров: {self.fats}\n•Углеводов: {self.carbohydrates}\n•Калорий: {self.calories}"
        else:
            return f"Продукт \"{self.user_product}\" не найден..."
        
        
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

                    if best_product is None:
                        best_product = row["Продукт"]
                        best_value = abs(float(row[category.lower().title()]) - value)
                        best_value_of_category = float(row[category.lower().title()])
                            
                    if abs(float(row[category.lower().title()]) - value) < best_value:
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

                    if best_product is None:
                        best_product = row["Продукт"]
                        best_value = float(row[category.lower().title()])
                        print(best_product)
                    
                    elif limit.lower() == "max" and float(best_value) < float(row[category.lower().title()]):
                        best_product = row["Продукт"]
                        best_value = float(row[category.lower().title()])

                    elif limit.lower() == "min" and float(best_value) > float(row[category.lower().title()]):
                        best_product = row["Продукт"]
                        best_value = float(row[category.lower().title()])
                        
            return [best_product, best_value]
        
        else:
            return ["Указанной категории не существует или указанный лимит неверный", 0]
