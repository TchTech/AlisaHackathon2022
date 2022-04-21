import json
import pymorphy2

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
                self.string = string.lower().replace("пожалуйста", "").replace("опять", "").strip()

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
                print(f"text = {text}")
                del text[0]
                text = " ".join(text)

                ##Ставим все слова в тексте в именительный падеж
                text = self.go_to_nominative(text)

                return text

        def go_to_nominative(self, word_to_nominative):
                not_to_nominative_words = ["суши", "сливки"] ##Слова которые не надо переводить в именительный падеж

                morph = pymorphy2.MorphAnalyzer()
                new_word_construct = []

                ##Цикл для того, чтобы все слова в продукте перевести в именительный падеж
                for i in word_to_nominative.split(" "):
                        ##Если слова нет в списке слов, которые менять не нужно
                        if i not in not_to_nominative_words:
                                word = morph.parse(i)[0]
                                new_word = word.inflect({'nomn'}) ##Переводим слово из косвенного падежа в именительный
                                if new_word is None:
                                        return word_to_nominative
                                else:
                                        new_word_construct.append(new_word.word)
                        else: ##Слово изменять не надо, поэтому просто добавляем
                                new_word_construct.append(i)

                return " ".join(new_word_construct).replace("ё", "е") ##Возвращаем слово в именительном падеже