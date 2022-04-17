from flask import Flask, request
import random
import csv
from classes.manage_product import InfoProduct

##WSGI - приложение
app = Flask(__name__)

##Наборы приветствий, прощаний и т.д.
HelloWords = ["привет", "приветствую", "прив", "приветик", "привит", "здравствуйте", "здравствуй", "зравия желаю", "здарова"]
ExitWords = ["выход", "выключись", "пока", "прощай", "как меня зовут", "переведи на английский"] ##Фразы при которых Алиса выйдет из сессии
LeaveWords = ["Выключаюсь...", "Выключаю навык \"ИнфоЕд\"", "Выходим из \"Инфоеда\""] ##Фразы которые Алиса скажет когда выключит навык

##Разные наборы кнопок
EmptyButtons = []
OnlyExitButton = [{"title":"Выход", "hide": True}]
DefaultButtons = [
    {"title": "Посчитай", "hide": True},
    {"title": "Выход", "hide": True}
]

@app.route("/", methods=["POST"])
def main():
    text = request.json["request"]["command"].lower().strip() ##Текст пользователя
    response_text = text
    end = False ##Выходим из навыка (True/False)
    buttons = OnlyExitButton 

    if text:     
        if text.split(" ")[0] in ["посчитай"]:
            product = text.lower().split("посчитай")[1].strip()
            info = InfoProduct(product)
            response_text = info.beautiful_text()

        elif text in ExitWords:
            response_text = random.choice(LeaveWords)
            end = True
    else:
        response_text = "Навык \"ИнфоЕд\" успешно запущен, теперь ты можешь узнать пищевую ценность (белки, жиры, углеводы, калории) большинства продуктов!\nДля этого используй команду \"Посчитай\"."

    ##Тело ответа
    response = {
        "response": {
            "text": response_text,
            "end_session": end,
            "buttons": buttons
        },
        "version": "1.0"
    }

    return response

##Точка входа
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)