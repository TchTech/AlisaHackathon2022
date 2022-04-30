class Person():

    sexs = ["мужской", "женский"]
    plans = ["для похудения", None]

    def __init__(self, sex, age, weight, growth, plan = None):
        
        self.age = age
        self.weight = weight
        self.growth = growth

        if sex in self.sexs and plan in self.plans:
            self.sex = sex
            self.plan = plan
        else:
            
            self.sex = "мужской"
            self.plan = None

    def get_PFC(self):
        __male_calories = (((10 * self.weight) + (6.25 * self.growth) - (5 * self.age) + 5) * 1.4) // 1
        __woman_calories = (((10 * self.weight) + (6.25 * self.growth) - (5 * self.age) - 161) * 1.4) // 1
    
        if self.sex == "мужской" and self.plan is None:
            self.calories = __woman_calories

        elif self.sex == "женский" and self.plan is None:
            self.calories = __woman_calories

        if self.plan == "для похудения":
            self.proteins = (self.calories * 0.3) / 4
            self.fats = (self.calories * 0.2) / 9
            self.carbohydrates = (self.calories * 0.5) / 4
        elif self.plan is None:
            self.proteins = (self.calories * 0.3) / 4
            self.fats = (self.calories * 0.3) / 9
            self.carbohydrates = (self.calories * 0.4) / 4

        return (round(self.proteins, 1), round(self.fats, 1), round(self.carbohydrates, 1), int(self.calories))