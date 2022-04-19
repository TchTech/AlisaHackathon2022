from flask import Flask, request
import random
import csv
from config import LOGO_IMG_ID
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
#ActivationWords = ["расскажи про", "посчитай", "рассчитай", "что насчет", "как насчёт"]
ActivationWords = ["расскажи про", "посчитай", "рассчитай", "что насчёт", "как насчёт"]

##Разные наборы кнопок
EmptyButtons = buttons_json["EmptyButtons"] = []
UserFirstCommand = buttons_json["UserFirstCommand"] = [{"title": "Расскажи про чай", "hide": True}]
#OnlyExitButton = buttons_json["OnlyExitButton"] = [{"title": "Выход", "hide": True}]
OnlyMoreButton = buttons_json["OnlyMoreButton"] = [{"title": "Помощь", "hide": True}]
DefaultButtons = buttons_json["DefaultButtons"] = [
    {"title": "Помощь", "hide": True},
    #{"title": "Выход", "hide": True}
]

##Сохранение наборов
json.save()

##Первые команды пользователей
users_first_command = {}

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
    response_text = text ##Текст ответа на письме
    response_speak = response_text ##Голосовой текст ответа

    ##Объект для разных способов ответа
    response_to_alice = Responses(end=end, version=version)

    try:
        buttons = DefaultButtons if users_first_command[user_id] == True else UserFirstCommand
    except Exception as err: ##Ошибка будет ловиться если нет ключа с таким айди. Такого ключа может не быть при первом запуске пользователем навыка
        buttons = UserFirstCommand

    if text:     
        ##Если айди пользователя нет в словаре
        if user_id not in users_first_command:
            #first_start = True
            title_card = "Эгей, тебя давно не было в \"ИнфоЕде\"!"
            response_text = "Навык \"ИнфоЕд\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи про\" и скажи название продукта.\nНапример: расскажи про чай"
            response_speak = "Навык \"Инфо+Еда\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи пр+о\" и скажи название продукта.\nНапример: расскажи пр+о чай"

            users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду

        ##Делаем условие, что активационные слова есть в тексте
        if ("расскажи" in text and "про" in text) or ("что" in text or "как" in text and "насчёт" in text) or ("посчитай" in text) or ("рассчитай" in text): 
            product = CorrectString(text).remove_other_words(ActivationWords)

            ##Проверка на то, был ли введён продукт
            if len(product) != 0: ##Т.е., product != ""
                info = InfoProduct(product)
                response_text = info.beautiful_text()
                response_speak = response_text
            else:
                response_text = "Эй, надо же сказать и продукт!"
                response_speak = response_text
                
            ##Если пользователь вводит впервые
            if not users_first_command[user_id]:
                ##Сделаем response_text для пользователя, который ввёл предложенную сначала команду
                response_text = "Молодец, у тебя круто получается!\n\n" + response_text + "\n\nХочешь узнать больше о моих возможностях - вводи команду \"Помощь\"."
                response_speak = response_text

                users_first_command[user_id] = True ##Ставим использование первой команды пользователем в True, дабы не писать более "Молодец!"
                buttons = DefaultButtons
                print(f"Пользователь с айди: {user_id}\n{users_first_command[user_id]}")


        elif text.split(" ")[0] in ["помощь"] and users_first_command[user_id] == True: ##Если пользователь хочет узнать больше информации о командах
            response_text = "Я умею:\n• Считать пищевую ценность продукта при помощи команды \"Расскажи про\" (расскажи про чай)"
            response_speak = "Я умею:\n• Считать пищевую ценность продукта при помощи команды \"Расскажи пр+о\"\n•\n•\n•"
            buttons = [] ##Пользователь уже в помощи, поэтому кнопки оставляем пустыми

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

            users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду
            print(f"Пользователь с айди: {user_id}\n{users_first_command[user_id]}")


        ##Если пользователь уже был в навыке и вводил первую команду  
        elif user_id in users_first_command and users_first_command[user_id] == True:
            title_card = "Инфоеда успешно запущен!"
            response_text = f"И снова здравствуй!\nЧтобы узнать пищевую ценность - вводи команду \"Расскажи про\" и название продукта (например: расскажи про чай). \nХочешь узнать больше о моих возможностях - вводи команду \"Помощь\"."
            response_speak = f"И снова здравствуй!\nЧтобы узнать пищевую ценность - вводи команду \"Расскажи пр+о\" и название продукта (например: расскажи пр+о чай). \nХочешь узнать больше о моих возможностях - вводи команду \"Помощь\"."
            buttons = DefaultButtons
            meet_again = True
    
    if users_first_command[user_id] == False or meet_again:
        ##Ответ при первом запуске     
        return response_to_alice.card_response(LOGO_IMG_ID, title_card, response_text, response_speak, buttons)

    ##Ответ с помощью объекта response (для полноты смотреть classes -> responses.py -> Responses)
    return response_to_alice.simply_response(response_text, response_speak, buttons)

##Точка входа
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)