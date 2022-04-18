from flask import Flask, request
import random
import csv
from classes.manage_words import JsonManager
from classes.manage_product import InfoProduct

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

##Разные наборы кнопок
EmptyButtons = buttons_json["EmptyButtons"] = []
UserFirstCommand = buttons_json["UserFirstCommand"] = [{"title": "Посчитай чай", "hide": True}]
OnlyExitButton = buttons_json["OnlyExitButton"] = [{"title": "Выход", "hide": True}]
OnlyMoreButton = buttons_json["OnlyMoreButton"] = [{"title": "Больше", "hide": True}]
DefaultButtons = buttons_json["DefaultButtons"] = [
    {"title": "Больше", "hide": True},
    {"title": "Выход", "hide": True}
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
    #first_start = False
    meet_again = False

    response_text = text
    end = False ##Выходим из навыка (True/False)

    try:
        buttons = DefaultButtons if users_first_command[user_id] == True else UserFirstCommand
    except Exception as err: ##Ошибка будет ловиться если нет ключа с таким айди. Такого ключа может не быть при первом запуске пользователем навыка
        print(err)
        buttons = UserFirstCommand

    if text:     
        #if text.split(" ")[0] in ["посчитай"]:
        if "расскажи про" in text or "что насчёт" in text or "посчитай" in text:
            #product = text.split("посчитай")[1].lower().strip()
            #product = text.replace("расскажи про", "").replace("посчитай", "").replace("что насчёт", "").strip()
            
            product = ""
            if "расскажи про" in text:
                product = " ".join(text.replace("пожалуйста", "").replace("алиса", "").replace("инфоед", "").replace("инфоеда", "").split("расскажи про")[text.index("")+1].split())
            elif "что насчёт" in text:
                product = " ".join(text.replace("пожалуйста", "").replace("алиса", "").replace("инфоед", "").replace("инфоеда", "").split("что насчёт")[text.index("")+1].split())
            elif "как насчёт" in text:
                product = " ".join(text.replace("пожалуйста", "").replace("алиса", "").replace("инфоед", "").replace("инфоеда", "").split("как насчёт")[text.index("")+1].split())
            elif "посчитай" in text:
                product = " ".join(text.replace("пожалуйста", "").replace("алиса", "").replace("инфоед", "").replace("инфоеда", "").split("посчитай")[text.index("")+1].split())
            
            ##Проверка на то, был ли введён продукт
            if len(product) != 0: ##Т.е., product != ""
                info = InfoProduct(product)
                response_text = info.beautiful_text()
            else:
                response_text = "Эй, надо же сказать и продукт!"
                
            ##Если айди пользователя нет в словаре
            if user_id not in users_first_command:
                #first_start = True
                title_card = "Эгей, тебя давно не было в \"ИнфоЕде\"!"
                response_text = "Навык \"ИнфоЕд\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Посчитай\" и скажи название продукта.\nНапример: посчитай чай"
            
                users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду

            ##Если пользователь вводит впервые
            elif not users_first_command[user_id]: 
                ##Сделаем response_text для пользователя, который ввёл предложенную сначала команду
                response_text = "Молодец, у тебя круто получается!\n\n" + response_text + "\n\nЧтобы получить доступ к моим другим командам - используй команду \"Больше\""
                users_first_command[user_id] = True ##Ставим использование первой команды пользователем в True, дабы не писать более "Молодец!"
                buttons = DefaultButtons
                print(f"Пользователь с айди: {user_id}\n{users_first_command[user_id]}")

        elif text.split(" ")[0] in ["больше"]: ##Если пользователь хочет узнать больше информации о командах
            response_text = "Команда в разработке..."
            buttons = OnlyExitButton

        elif text in HelloWords: ##Если пользователь приветствует
            response_text = random.choice(HelloWords).title()

        elif text in ExitWords: ##Если пользователь прощается
            response_text = random.choice(LeaveWords).title()
            end = True
    else:
        title_card = "Инфоеда успешно запущен!"
        ##По сути, можно запихнуть в elif, но не очень уверен что тогда всё будет корректно работать
        if user_id not in users_first_command or users_first_command[user_id] == False:
            title_card = "Приветствуем тебя в \"ИнфоЕде\"!"
            response_text = "Навык \"ИнфоЕд\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Посчитай\" и скажи название продукта.\nНапример: посчитай чай"
            
            users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду
            print(f"Пользователь с айди: {user_id}\n{users_first_command[user_id]}")


        ##Если пользователь уже был в навыке и вводил первую команду  
        elif user_id in users_first_command and users_first_command[user_id] == True:
            #title = "Инфоеда успешно запущен!"
            response_text = f"И снова здравствуй!\nЧтобы узнать пищевую ценность - вводи команду \"Посчитай\" и название продукта (например: посчитай чай).Хочешь узнать больше о навыке - вводи команду \"Больше\"."
            buttons = DefaultButtons
            meet_again = True
    
    if not users_first_command[user_id] or meet_again:
        ##Ответ при первом запуске
        response = {
                "response": {
                    "text": response_text,
                    "end_session": end,
                    "buttons": buttons, ##Кнопка которая и станет первой командой пользователя с подсчётом ценности продукта (например, чая) при первом запуске навыка и команда "Больше" если пользователь уже пользовался навыком

                    ##Карточка - блок с картинкой, далее заголовком и текстом
                    "card": {
                        "type":"BigImage",
                        "image_id": "937455/e1833075f705a4649b2c",
                        "title": title_card,
                        "description": response_text,
                    }
                },
                "version": version
            }
            
        return response

    ##Тело ответа
    response = {
        "response": {
            "text": response_text,
            "end_session": end,
            "buttons": buttons
        },
        "version": version
    }

    return response

##Точка входа
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
