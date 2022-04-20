from flask import Flask, request
import random
import csv
from config import LOGO_IMG_ID, ERROR_IMG_ID
from classes.manage_words import JsonManager
from classes.manage_product import InfoProduct
from classes.responses import Responses
from classes.manage_words import CorrectString

##WSGI - приложение
app = Flask(__name__)

##Создание jsona
json = JsonManager("words.json")
phrases_json = json.json_object["Phrases"]
buttons_json = json.json_object["Buttons"]

##Наборы приветствий, прощаний и т.д.
HelloWords = phrases_json["HelloWords"] = ["привет", "приветствую", "прив", "приветик", "привит", "здравствуйте", "здравствуй", "зравия желаю", "здарова"]
ExitWords = phrases_json["ExitWords"] = ["выход", "выключись", "пока", "прощай", "как меня зовут", "переведи на английский"] ##Фразы при которых Алиса выйдет из сессии
LeaveWords = phrases_json["LeaveWords"] = ["Выключаюсь...", "Выключаю навык \"ИнфоЕд\"", "Выходим из \"Инфоеда\""] ##Фразы которые Алиса скажет когда выключит навык

##Активирующие слова
ActivationWords = phrases_json["ActivationWords"] = ["расскажи про", "скажи про", "посчитай", "рассчитай", "что насчет", "что насчёт", "как насчет", "как насчёт"]

##Разные наборы кнопок
EmptyButtons = buttons_json["EmptyButtons"] = []
UserFirstCommand = buttons_json["UserFirstCommand"] = [{"title": "Расскажи про чай", "hide": True}]
OnlyMoreButton = buttons_json["OnlyMoreButton"] = [{"title": "Помощь", "hide": True}]
OnlyErrorButton = buttons_json["OnlyExitButton"] = [{"title": "Ошибка", "hide": True}]
MoreAndErrorButtons = buttons_json["MoreAndErrorButtons"] = [
    {"title": "Ошибка", "hide": True},
    {"title": "Помощь", "hide": True}
    ]
DefaultButtons = buttons_json["DefaultButtons"] = [
    {"title": "Помощь", "hide": True},
    #{"title": "Выход", "hide": True}
]

##Сохранение наборов
json.save()

##Первые команды пользователей
users_first_command = {}  ##Ключ - айди пользователя; Значение - True/False (была использована пользователем команда или нет)

##Стоп-лист
users_stop_list_products = {} ##Ключ - айди пользователя; Значение - список с названиями продуктов

##Обработчик куда алиса пришлёт ответ, а мы станем отвечать на него
@app.route("/", methods=["POST"])
def main():
    req = request.json ##Ответ от алисы
    text = req["request"]["command"].lower().strip().replace(",", "").replace(".", "") ##Текст пользователя
    version = req["version"] ##Версия (алисы)
    user_id = req["session"]["user_id"] ##id пользователя
    end = False ##Выходим из навыка (True/False)
    meet_again = False

    ##Переменные для пользователя
    title_card = "ИнфоЕда"
    response_text = "" ##Текст ответа на письме
    response_speak = "" ##Голосовой текст ответа
    response_img = None ##Картинка для вставки потом в карточку

    ##Объект для разных способов ответа
    response_to_alice = Responses(end=end, version=version)

    try:
        buttons = DefaultButtons if users_first_command[user_id] == True else UserFirstCommand
    except Exception as err: ##Ошибка будет ловиться если нет ключа с таким айди. Такого ключа может не быть при первом запуске пользователем навыка
        buttons = UserFirstCommand

    if text:     
        ##Если айди пользователя нет в словаре, но он всё равно ввел какой-либо текст (т.е., у него УЖЕ было открыто диалоговое окно навыка)
        if user_id not in users_first_command:
            #first_start = True
            title_card = "Эгей, тебя давно не было в \"ИнфоЕде\"!"
            response_text = "Навык \"ИнфоЕд\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи про\" и скажи название продукта.\nНапример: расскажи про чай"
            response_speak = "Навык \"Инфо+Еда\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи пр+о\" и скажи название продукта.\nНапример: расскажи пр+о чай"

            users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду

        ##Делаем условие, что активационные слова есть в тексте
        if ("расскажи" in text and "про" in text) or ("скажи" in text and "про" in text) or ("что" in text or "как" in text and "насчёт" in text) or ("посчитай" in text) or ("рассчитай" in text): 
            product = CorrectString(text).remove_other_words(ActivationWords)

            ##Проверка на то, был ли введён продукт
            if len(product) != 0: ##Т.е., product != ""
                info = InfoProduct(product, users_stop_list_products[user_id]) ##Инициализируем объект класса, в котором будет храниться вся информация о продукте
                
                title_card = info.user_product.split()[0].title() + " " + " ".join(info.user_product.split()[1::]) + f"({info.category})" ##Первое слово в продукте делаем с заглавной буквой, далее пишем пробел, далее всё остальное. Потом прибавляем категорию продукта

                response_text = info.beautiful_text()[0] ##.beautiful_text возвращает кортеж, нулевой элемент - письменный текст
                response_speak = info.beautiful_text()[1] ##Первый элемент - голосовой текст
                response_img = info.get_product_img()  ##Получаем картинку продукта
                users_stop_list_products[user_id] = info.stop_list ##Получаем стоп-лист от атрибута класса

                ##Проверим на предел вместимости стоп-листа (5 элементов)
                if len(users_stop_list_products[user_id]) >= 5:
                    users_stop_list_products[user_id] = [] ##Если больше 5 элементов было в стоп-листе - очищаем его
                else: ##Иначе - добавляем очередной продукт от пользователя к стоп-листу
                    if info.name not in users_stop_list_products[user_id]: ##Если такого продукта нет в стоп-листе
                        users_stop_list_products[user_id] = users_stop_list_products[user_id] + [*[info.name]]
    
                ##Если пользователь вводит команду впервые и продукт был найден
                if not users_first_command[user_id] and info.name != None:
                    ##Сделаем response_speak для пользователя, который ввёл свою первую команду
                    response_speak = "Молодец, у тебя круто получается!\n\n" + response_speak + "\n\nХочешь узнать больше о моих возможностях - вводи команду \"Помощь\"."

                    users_first_command[user_id] = True ##Ставим использование первой команды пользователем в True, дабы не писать более "Молодец!"
                    buttons = DefaultButtons
                    #(f"Пользователь с айди: {user_id}\n{users_first_command[user_id]}")

                ##Если продукт не был найден
                if info.name == None:
                    title_card = "Ошибка"
                    buttons = MoreAndErrorButtons ##В кнопки ставим "Помощь" и "Ошибка"
                    #response_img = ERROR_IMG_ID
                    response_img = None ##Внизу есть проверка и если картинка == None - карточка показываться не будет

            else: ##Если пользователь ввёл только активационное слово
                response_text = "Эй, надо же сказать и продукт!"
                response_speak = response_text


        elif text.split(" ")[0] in ["помощь"]: ##Если пользователь хочет узнать больше информации о командах
            response_text = "Я умею:\n• Считать пищевую ценность продукта при помощи команды \"Расскажи про\" (расскажи про чай)"
            response_speak = "Я умею:\nпервое. Считать пищевую ценность продукта при помощи команды \"Расскажи пр+о\"\n•\n•\n•"
            buttons = [] ##Пользователь уже в помощи, поэтому кнопки оставляем пустыми
            response_img = None

            ##Отправляем алисе сразу ответ
            return response_to_alice.simply_response(response_text, response_speak, buttons)

        elif text in HelloWords: ##Если пользователь приветствует
            response_text = random.choice(HelloWords).title()
            response_speak = response_text

        elif text in ExitWords: ##Если пользователь прощается
            response_text = random.choice(LeaveWords).title()
            response_speak = response_text
            end = True
    else:
        ##По сути, можно запихнуть в elif, но не очень уверен что тогда всё будет корректно работать
        if user_id not in users_first_command or users_first_command[user_id] == False:
            title_card = "Приветствуем тебя в \"ИнфоЕде\"!"
            response_text = "Навык \"ИнфоЕда\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи про\" и скажи название продукта.\nНапример: расскажи про чай"
            response_speak = "Навык \"Инфо+Еда\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи пр+о\" и скажи название продукта.\nНапример: расскажи пр+о чай"
            response_img = LOGO_IMG_ID ##Это первый ввод команты пользователем и поэтому отслылаем карточку с логотипом

            users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду
            users_stop_list_products[user_id] = [] ##В значение стоп листа стави пустой список, дабы потом в него осуществлять добавку при вводе пользователем продуктов

            #print(f"Пользователь с айди: {user_id}\n{users_first_command[user_id]}")

        ##Если пользователь уже был в навыке и вводил первую команду (грубо говоря, если пользователь очистил диалоговое окно с навыком)
        elif user_id in users_first_command and users_first_command[user_id] == True:
            title_card = "Инфоеда успешно запущен!"
            response_text = f"И снова здравствуй!\nЧтобы узнать пищевую ценность - вводи команду \"Расскажи про\" и название продукта (например: расскажи про чай). \nХочешь узнать больше о моих возможностях - вводи команду \"Помощь\"."
            response_speak = f"И снова здравствуй!\nЧтобы узнать пищевую ценность - вводи команду \"Расскажи пр+о\" и название продукта (например: расскажи пр+о чай). \nХочешь узнать больше о моих возможностях - вводи команду \"Помощь\"."
            buttons = DefaultButtons
            response_img = LOGO_IMG_ID
            meet_again = True
    
    ##Если пользователь впервые в навыке или если очистил окно с диалогом внутри навыка (за это и отвечает meet_again)
    if users_first_command[user_id] == False or meet_again and response_img != None:
        ##Ответ при первом запуске     
        return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)

    ##Если картинка не None (если в ответе будет картинка, т.е., ответ подразумевается в виде карточки)
    if response_img != None:
        return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)
    else:
        ##Ответ с помощью объекта response (для полноты смотреть classes -> responses.py -> Responses)
        return response_to_alice.simply_response(response_text, response_speak, buttons)

##Точка входа
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)