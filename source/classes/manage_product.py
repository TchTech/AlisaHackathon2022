import csv
class InfoProduct():

    name: str = None #Название продукта
    weight: float = None #Вес 
    proteins: float = None #Белки
    fats: float = None #Жиры
    carbohydrates: float = None #Углеводы
    calories: float = None #Калории
    
    def __init__(self, product: str): #Инициализация объекта (конструктор)
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
        	return  f"В продукте \"{self.name}\" содержится:\n•Белков: {self.proteins}\n•Жиров: {self.fats}\n•Углеводов: {self.carbohydrates}\n•Калорий: {self.calories}"
