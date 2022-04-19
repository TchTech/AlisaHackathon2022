import json


class JsonManager():
        json_object: dict = None
        filename: str = None
        
        def __init__(self, filename):
                self.filename = filename
                with open(filename, 'r', encoding='utf8') as file:
                        self.json_object = json.load(file)
        def save(self):
                with open(self.filename, 'w') as file:
                        json.dump(self.json_object, file, indent=4)


##Класс для различных правок строк
class CorrectString:

        ##Инициализатор с присваиванием атрибуту класса string значения передаваемого string
        def __init__(self, string):
                self.string = string.lower().replace("пожалуйста", "").strip()

        ##Метод для удаления всего кроме названия продукта
        def remove_other_words(self, activation_names: list) -> str:

                final_activation_names = []
                for activation_name in activation_names:
                        activation_name = activation_name.split()
                        final_activation_names.append(activation_name[-1])
                        
                text = self.string.split()

                for word in range(len(text)):
                        if text[word] in final_activation_names:
                                break
                        else:
                                text[word] = ""
                for word in range(len(text)):
                        if text[word] != "":
                                text[word] +=  " "
                
                text = "".join(text).split()
                del text[0]
                text = " ".join(text)

                return text