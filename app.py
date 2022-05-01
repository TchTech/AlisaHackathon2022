# -*- coding: utf-8 -*-
import os, sys
from flask import Flask, request
import random
from config import LOGO_IMG_ID, ERROR_IMG_ID
from classes.manage_words import JsonManager
from classes.manage_product import InfoProduct
from classes.manage_product import ProductSearch
from classes.responses import Responses
from classes.manage_words import CorrectString
from classes.manage_mails import EmailSend
from config import EMAIL, PASSWORD
from classes.manage_quest import Quest
from classes.manage_states import States
import re
from classes.manage_person import Person
import torch
from classes.manage_intellect import Recommender

##WSGI - приложение
app = Flask(__name__)

##Создание jsona
json = JsonManager("words.json")
phrases_json = json.json_object["Phrases"]
buttons_json = json.json_object["Buttons"]

##Наборы приветствий, прощаний и т.д.
HelloWords = phrases_json["HelloWords"] = ["привет", "приветствую", "приветик", "здравствуйте", "здравствуй", "зравия желаю"]
ExitWords = phrases_json["ExitWords"] = ["выход", "выключись", "пока", "прощай", "как меня зовут", "переведи на английский"] ##Фразы при которых Алиса выйдет из сессии
LeaveWords = phrases_json["LeaveWords"] = ["Прощайте", "До свидания", "Увидимся!", "До встречи"] ##Фразы которые Алиса скажет когда выключит навык

##Активирующие слова
ActivationWords = phrases_json["ActivationWords"] = ["расскажи про", "расскажи о", "расскажи об", "посчитай", "рассчитай", "скажи про", "скажи о", "пожалуйста про", "что насчет", "что насчёт", "как насчет", "как насчёт", "покажи", "покажи ка", "посчитай", "посчитай ка"]
ActivationCalculate = phrases_json["ActivationCalculate"] = {
    "before": ["посчитай", "рассчитай"],
    "after": ["на", "про"]
}

##Слова для отправки сообщения об ошибке
ActivationEmailWords = phrases_json["ActivationEmailWords"] = ["ошибка"]

##Разные наборы кнопок
EmptyButtons = buttons_json["EmptyButtons"] = []
UserFirstCommands = buttons_json["UserFirstCommands"] = [
    {"title": "Расскажи про чай", "hide": True},
    {"title": "Квест", "hide": True}
    ]
OnlyMoreButton = buttons_json["OnlyMoreButton"] = [{"title": "Помощь", "hide": True}]
OnlyErrorButton = buttons_json["OnlyExitButton"] = [{"title": "Ошибка", "hide": True}]
MoreAndErrorButtons = buttons_json["MoreAndErrorButtons"] = [
    {"title": "Ошибка", "hide": True},
    {"title": "Помощь", "hide": True}
    ]
DefaultButtons = buttons_json["DefaultButtons"] = [
    {"title": "Квест", "hide": True},
    {"title": "Помощь", "hide": True},
    {"title": "Расскажи про случайный продукт", "hide": False}
]
MoreAndQuestButtons = buttons_json["MoreAndQuestButtons"] = [
    {"title": "Квест", "hide": True},
    {"title": "Помощь", "hide": True}
]
CalculateQuestMoreButtons = [
    {"title": "Расскажи про чай", "hide": True},
    {"title": "Квест", "hide": True},
    {"title": "Помощь", "hide": True}
]
SayCalculateQuestMoreButtons = [
    {"title": "Расскажи про чай", "hide": True},
    {"title": "Квест", "hide": True},
    {"title": "Помощь", "hide": True},
    {"title": "Расскажи про случайный продукт", "hide": False}
]
QuestButton = buttons_json["QuestButton"] = [{"title": "Квест", "hide": True}]
ExitFromQuest = buttons_json["ExitFromQuest"] = [{"title": "Покинуть квест", "hide": True}]

##Кнопки для диалогов
MaleAndFemaleAndQuit = buttons_json["MaleAndFemale"] = [
    {"title": "Мужской", "hide": False},
    {"title": "Женский", "hide": False},
    {"title": "Покинуть", "hide": True}
]
QuitAdviceButton = buttons_json["QuitAdviceButton"] = [
    {"title": "Покинуть", "hide": True}
]
QuitDishHint = [{"title": "Покинуть", "hide": True}]
AgainDishHint = [
    {"title": "Расскажи про чай", "hide": True},
    {"title": "Квест", "hide": True},
    {"title": "Помощь", "hide": True},
    {"title": "Подбери блюдо", "hide": False}
]

##Сохранение наборов
json.save()

##Первые команды пользователей
users_first_command = {}  ##Ключ - айди пользователя; Значение - True/False (была использована пользователем команда или нет)

##Стоп-лист
users_stop_list_products = {} ##Ключ - айди пользователя; Значение - список с названиями продуктов
##Словарь в котором значением будет слово, которое не смог найти пользователь
users_error_products = {} ##Ключ - айди пользователя; Значение - строка (название продукта)
##Словарь с ключом - айди и значением - списком продуктов, которые говорил пользователь
users_products = {}

##Стоп-лист с предложенными продуктами при команде "посоветуй"
users_advice_stop_list = {}

##Объект для отправки сообщения
email_send = EmailSend(EMAIL, PASSWORD)

##Словарь для успешной игры пользователя в квест. Ключ - айди пользователя; Значение - True/False
users_playing_quest = {}

##Объект квеста для пользователей. Ключ - айди пользователя; Значение - объект класса Quest
users_quest = {}

##Объект машины состояний для каждого пользователя
users_states = {}

##Объект (мини машина состояний) для сказа пользователем ингридиента продукта
users_saying_ingridient = {}

##Обработчик куда алиса пришлёт ответ, а мы станем отвечать на него
@app.route("/", methods=["POST"])
def main():
    global users_first_command, users_stop_list_products, users_error_products, users_products, users_advice_stop_list
    global users_playing_quest, users_quest, users_states, users_saying_ingridient
    global email_send

    req = request.json ##Ответ от алисы
    text = req["request"]["command"].lower().strip().replace(",", "").replace(".", "").replace("!", "").replace("?", "") ##Текст пользователя
    version = req["version"] ##Версия (алисы)
    user_id = req["session"]["user_id"] ##id пользователя
    end = False ##Выходим из навыка (True/False)
    meet_again = False

    ##Переменные для пользователя
    title_card = "ИнфоЕда"
    response_text = "" ##Текст ответа на письме
    response_speak = "" ##Голосовой текст ответа
    response_img = None ##Картинка для вставки потом в карточку

    ##В стоп-лист по умолчанию ставим пустой список (если айди пользователя нет в списке ключей - по умолчанию значением ставим пустой список)
    if user_id not in users_stop_list_products:
        users_stop_list_products[user_id] = []
    
    ##В словарь с ошибочным продуктом кладём пустой список по умолчанию
    if user_id not in users_error_products:
        users_error_products[user_id] = []

    ##В словарь с продуктами пользователя кладём пустой список по умолчанию
    if user_id not in users_products:
        users_products[user_id] = []

    ##С словарь с игрой пользователя в квест - по умолчанию кладём False
    if user_id not in users_playing_quest:
        users_playing_quest[user_id] = False

    ##В словарь со стоп-листом предложенных продуктов кладём по умолчанию пустой список
    if user_id not in users_advice_stop_list:
        users_advice_stop_list[user_id] = []

    ##В users_quest по умолчанию кладём None
    if user_id not in users_quest:
        users_quest[user_id] = None

    ##В users_states по умолчанию кладём объект класса States
    if user_id not in users_states:
        users_states[user_id] = States()

    ##В users_saying_ingridient по умолчанию кладём False, т.к., пользователь не говорит ингридиенты с самого начала
    if user_id not in users_saying_ingridient:
        users_saying_ingridient[user_id] = False

    ##Служебные объекты
    response_to_alice = Responses(end=end, version=version)##Объект для разных способов ответа

    try:
        buttons = DefaultButtons if users_first_command[user_id] == True else UserFirstCommands
    except Exception as err: ##Ошибка будет ловиться если нет ключа с таким айди. Такого ключа может не быть при первом запуске пользователем навыка
        buttons = UserFirstCommands

    ##Всё помещаем в try-except для того, чтобы не было шаблонного "Извините, диалог не отвечает"
    try:
        if text:
            product = None ##Для дальнейшей записи сюда продукта
            random_check = CorrectString().go_to_nominative(text) ##Далее будем использовать для проверки на ввод "Случайный продукт"
            quest_check = CorrectString().go_to_nominative(text) ##Будем проверять, есть ли упоминание о квесте в тексте

            ##Если айди пользователя нет в словаре, но он всё равно ввел какой-либо текст (т.е., у него УЖЕ было открыто диалоговое окно навыка)
            if user_id not in users_first_command:
                title_card = "Эгей, тебя давно не было в \"ИнфоЕде\"!"
                response_text = "Навык \"ИнфоЕд\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи про\" и скажи название продукта.\nНапример: расскажи про чай"
                response_speak = "Навык \"Инфо+Еда\" успешно запущен, теперь ты можешь узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используй команду \"Расскажи пр+о\" и скажи название продукта.\nНапример: расскажи пр+о чай"

                users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду

            ##Если игра в квест уже идёт (Ветка квеста)
            if users_playing_quest[user_id] == True:
                
                ##Выход из квеста (Если пользователь ввёл команду "покинуть квест" или похожую)
                if len(re.findall(r"п[оа][кг][и\w]ну[тд][ьъ]", text)) > 0:
                    users_playing_quest[user_id] = False
                    response_text = "Успешно покинули квест."
                    response_speak = response_text
                    buttons = CalculateQuestMoreButtons
                ##Если пользователь просто играет в квест
                else:
                    response_text = users_quest[user_id].IsRightAnswer(text)[1]
                    response_speak = users_quest[user_id].IsRightAnswer(text)[2]
                    users_playing_quest[user_id] = False
                    buttons = users_quest[user_id].IsRightAnswer(text)[3]

                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если есть упоминание о квесте в тексте
            elif "квест" in quest_check or "квест" in text:
                if users_playing_quest[user_id] == False:
                    users_playing_quest[user_id] = True
                    users_quest[user_id] = Quest()
                    response_text = users_quest[user_id].PrintRules()[0]
                    response_speak = users_quest[user_id].PrintRules()[1]
                    buttons = users_quest[user_id].get_buttons_answers()

                    ##Отправляем ответ алисе
                    return response_to_alice.simply_response(response_text, response_speak, buttons)
            
            ##Ветка с подсчётом нормы БЖУ
            if len(re.findall(r"скол[ь]к\w", text)) > 0 and (users_states[user_id].say_growth == False or users_states[user_id].states_list[3] == False):
                response_text = "Для того, чтобы определить вашу норму в день, мне нужно собрать данные о вас.\nДля начала назовите ваш пол (мужской/женский):"
                response_speak = "Для того, чтобы определить вашу норму в день, мне нужно собрать данные о вас.\nДля начала назовите ваш пол:"
                #buttons = MoreAndQuestButtons
                buttons = MaleAndFemaleAndQuit

                users_states[user_id].process_recommends = True
                ##В True ставим самый первый атрибут (пол - say_sex), чтобы потом его корректно считать
                users_states[user_id].say_sex = True

                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь хочет покинуть процесс подсчета нормы БЖУ и калорий в сутки
            if "покинуть" in text and users_states[user_id].process_recommends == True and (users_states[user_id].say_sex == True or users_states[user_id].say_age == True or users_states[user_id].say_weight == True or users_states[user_id].say_growth == True):
                response_text = "Успешно покинули процесс подсчета нормы БЖУ и калорий в день."
                response_speak = response_text
                buttons = CalculateQuestMoreButtons

                ##Зануляем советы
                users_states[user_id] = States()

                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Запоминаем пол пользователя
            if len(re.findall("муж.{0,}|жен.{0,}", text)) > 0 and (users_states[user_id].say_sex == True or users_states[user_id].states_list[0] == True):
                if re.findall("муж.{0,}|жен.{0,}", text)[0][0:3] == "муж":
                    sex = "мужской"
                else:
                    sex = "женский"
                response_text = f"Хорошо, ваш пол: {sex}.\nТеперь укажите ваш возраст:"
                response_speak = response_text
                #buttons = MoreAndQuestButtons
                buttons = QuitAdviceButton

                ##Продвигаем состояния вперёд
                users_states[user_id].correctly_sex = sex
                users_states[user_id].next()
                users_states[user_id].say_sex = False
                users_states[user_id].say_age = True

                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь не ввёл свой пол
            elif len(re.findall("муж.{0,}|жен.{0,}", text)) <= 0 and (users_states[user_id].say_sex == True):
                print(users_states[user_id].states_list)
                print(users_states[user_id].say_sex, " - скажи пол")
                response_text = "Не удалось распознать пол, попробуйте снова."
                response_speak = response_text
                #buttons = MoreAndQuestButtons
                buttons = MaleAndFemaleAndQuit

                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Запоминаем возраст пользователя
            if text.replace("-", "").isdigit() and (users_states[user_id].say_age == True):
                ##Если возраст пользователя нереальный 
                if int(text) > 110 or int(text) < 0:
                    response_text = "Вводите действительный возраст!"
                    response_speak = response_text
                    #buttons = MoreAndQuestButtons
                    buttons = QuitAdviceButton

                    ##Отправляем ответ алисе
                    return response_to_alice.simply_response(response_text, response_speak, buttons)
                else:
                    age = int(text)
                    response_text = f"Отлично, ваш возраст: {age}.\nТеперь укажите ваш вес (в килограммах):"
                    response_speak = response_text
                    #buttons = MoreAndQuestButtons
                    buttons = QuitAdviceButton

                    ##Продвигаем состояния вперёд
                    users_states[user_id].correctly_age = age
                    users_states[user_id].next()
                    users_states[user_id].say_age = False
                    users_states[user_id].say_weight = True
                    print(users_states[user_id].states_list, "---------------------------")

                    ##Отправляем ответ алисе
                    return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если текст был не числом
            elif isinstance(text, str) and (users_states[user_id].say_age == True):
                response_text = "Возраст должен быть целым числом!"
                response_speak = response_text
                #buttons = MoreAndQuestButtons
                buttons = QuitAdviceButton

                ##Отправляем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Запоминаем вес пользователя
            if len("".join(re.findall(r"\d\d\d|\d\d|\d", text))) > 0 and (users_states[user_id].say_weight == True):
                weight = float("".join(re.findall(r"\d\d\d|\d\d|\d", text))) ##Вес указанный пользователем
                response_text = f"Супер, ваш вес: {weight} килограмм.\nТеперь укажите ваш рост (в сантиметрах)"
                response_speak = response_text
                #buttons = MoreAndQuestButtons
                buttons = QuitAdviceButton

                ##Продвигаем состояние вперёд
                users_states[user_id].correctly_weight = weight
                users_states[user_id].next()
                users_states[user_id].say_weight = False
                users_states[user_id].say_growth = True

                ##Возвращаем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь не ввёл число (свой вес)
            elif len("".join(re.findall(r"\d\d\d|\d\d|\d", text))) <= 0 and (users_states[user_id].say_weight == True):
                response_text = "Вам необходимо указать ваш вес в следующем формате: 80 кг"
                response_speak = response_text
                #buttons = MoreAndQuestButtons
                buttons = QuitAdviceButton

                ##Возвращаем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Запоминаем рост пользователя
            if len("".join(re.findall(r"\d\d\d|\d\d", text))) > 0 and (users_states[user_id].say_growth == True):
                growth = float("".join(re.findall(r"\d\d\d|\d\d", text))) ##Рост введённый пользователем
                users_states[user_id].correctly_growth = growth

                ##Данная переменная содержит индивидуальные рекомендации БЖУ и калорий
                individual_recommendations = Person(users_states[user_id].correctly_sex, users_states[user_id].correctly_age, users_states[user_id].correctly_weight, users_states[user_id].correctly_growth).get_PFC()

                if individual_recommendations[0] < 0 or individual_recommendations[1] < 0 or individual_recommendations[2] < 0 or individual_recommendations[3] < 0:
                    response_text = f"Данные чересчур малы, можете попробовать ввести их снова."
                    response_speak = response_text
                    buttons = SayCalculateQuestMoreButtons
                else:
                    response_text = f"Замечательно, вы ввели все нужные для подсчета данные!\nНа основе введенных вами данных, могу сказать, что в день вам следует съедать:\n• Белков: {individual_recommendations[0]} грамм.\n• Жиров: {individual_recommendations[1]} грамм.\n• Углеводов: {individual_recommendations[2]} грамм.\n• Калорий: {individual_recommendations[3]} ккал."
                    response_speak = f"На основе введенных вами данных, могу сказать, что в день вам следует съедать:\n• Белков: {individual_recommendations[0]} грамм.\n• Жиров: {individual_recommendations[1]} грамм.\n• Углеводов: {individual_recommendations[2]} грамм.\n• Калорий: {individual_recommendations[3]} ккал."
                    buttons = SayCalculateQuestMoreButtons

                ##Мы на последнем этапе, поэтому всё обнуляем (переприсваем класс States)
                users_states[user_id] = States()

                ##Возвращаем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь не ввёл число (минимум двузначное - свой рост)
            elif len("".join(re.findall(r"\d\d|\d\d\d", text))) <= 0 and (users_states[user_id].say_growth == True):
                response_text = "Вам необходимо указать ваш рост в следующем формате: 180 см"
                response_speak = response_text
                buttons = MoreAndQuestButtons

                ##Возвращаем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)


            ##Ветка с советом продукта от ии по ингредиенту
            if len(re.findall("п[оа][дт][сз][кг][ао][жш][иы]|п[оа][дт][бп][еи]ри", text)) > 0:
                response_text = "Готова подобрать блюдо! Пожалуйста, введите название ингредиента блюда (к примеру: яблоко):"
                response_speak = response_text
                #buttons = CalculateQuestMoreButtons
                buttons = QuitDishHint

                ##В словарь с: пользователь в ветке подсказки или нет - ставим True - поскольку он попал в неё
                users_saying_ingridient[user_id] = True

                ##Возвращаем ответ Алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь хочет выйти из подсказки блюда по ингредиенту
            if len(re.findall(r"п[оа]{0,}[кг]{0,}[и\w]{0,}.{0,}", text)) > 0 and users_saying_ingridient[user_id] == True:
                response_text = f"Успешно вышли из процесса совета блюда."
                response_speak = response_text
                buttons = CalculateQuestMoreButtons

                ##В словарь с: пользователь в ветке подсказки или нет - ставим False - поскольку он ввёл 'покинуть'
                users_saying_ingridient[user_id] = False

                ##Возвращаем ответ Алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь вводит ингредиент
            elif users_saying_ingridient[user_id] == True:
                ingridient = CorrectString().go_to_nominative(text)
                recommends = Recommender(ingridient)
                dishes = recommends.get_dishes()
                
                ##Проверка на полученные блюда
                if len(dishes) > 0:
                    response_text = f"Хорошо, ингредиент \"{ingridient}\" принят.\nМогу посоветовать Вам следующие блюда:\n\n{dishes}"
                    response_speak = recommends.get_speech()
                    buttons = AgainDishHint
                else:
                    response_text = f"Блюд с  ингредиентом: \"{ingridient}\" не найдено, попробуйте повторить."
                    response_speak = response_text
                    buttons = AgainDishHint

                ##В словарь с: пользователь в ветке подсказки или нет - ставим False - поскольку он ввёл уже ингредиент и получил ответ
                users_saying_ingridient[user_id] = False

                ##Возвращаем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Ветка с советом какого-либо продукта
            if "посоветуй" in text:
                specification = ProductSearch(users_stop_list_products[user_id]).remove_all_in_specification(text)
        
                product = ProductSearch(users_stop_list_products[user_id]).search_by_value(float(specification.split()[0]), str(specification.split()[1]).lower(), users_advice_stop_list[user_id])
                
                title_card = product[0][0] + f" ({product[0][1]})"
                response_text = f"Могу посоветовать следующий продукт: {product[0][0].lower()}.\nВ нём содержится {product[1]} {product[2]} на 100 грамм."
                response_speak = response_text
                response_img = product[3]
                users_advice_stop_list[user_id] = product[4]
                #buttons = MoreAndQuestButtons
                buttons = SayCalculateQuestMoreButtons

                #return response_to_alice.simply_response(response_text, response_speak, buttons)
                return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)

            ##Если пользователь хочет случайный продукт
            elif random_check == "случайный продукт" or random_check == "рандомный продукт" or random_check == "случайный" or random_check == "рандомный"\
                or text == "случайный продукт" or text == "рандомный продукт" or text == "случайный" or text == "рандомный":
                search = ProductSearch(users_stop_list_products[user_id]) ##Делаем объект на основе класса ProductSearch
                response_text, response_img = search.random_product()
                title_card = search.name.split()[0].title() + " " + " ".join(search.name.split()[1::]) + f" ({search.category})" ##Первое слово в продукте делаем с заглавной буквой, далее пишем пробел, далее всё остальное. Потом прибавляем категорию продукта
                response_speak = response_text
                buttons = DefaultButtons

                ##Отправляем ответ алисе
                return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)

            ##Делаем условие, что активационные слова есть в тексте
            if ("расскажи" in text and "про" in text) or ("расскажи" in text and "о" in text) or ("расскажи" in text and "об" in text) or ("скажи" in text and "про" in text) or ("скажи" in text and "о" in text) or ("пожалуйста" in text and "про" in text) or ("что" in text or "как" in text and "насчёт" in text or "насчет" in text) or ("покажи" in text) or ("посчитай" in text and len(re.findall(r"\w*амм", text)) <= 0): 
                product = CorrectString(text).remove_other_words(ActivationWords, go_nominative=False) ##Продукт в именительном падеже и без мусорных слов
                
                ##Если сообщение было: расскажи про случайный продукт
                if product == "случайный продукт" or product == "рандомный продукт"\
                or "случайный" in product or "рандомный" in product:
                    search = ProductSearch(users_stop_list_products[user_id]) ##Делаем объект на основе класса ProductSearch
                    response_text, response_img = search.random_product()
                    title_card = search.name.split()[0].title() + " " + " ".join(search.name.split()[1::]) + f" ({search.category})" ##Первое слово в продукте делаем с заглавной буквой, далее пишем пробел, далее всё остальное. Потом прибавляем категорию продукта
                    response_speak = response_text
                    buttons = DefaultButtons

                    ##Отправляем ответ алисе
                    return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)

                ##Проверка на то, был ли введён продукт
                if len(product) != 0: ##Т.е., product != ""
                    info = InfoProduct(product, users_stop_list_products[user_id], users_products[user_id]) ##Инициализируем объект класса, в котором будет храниться вся информация о продукте

                    title_card = info.get_title_card() ##Получаем заголовок для карточки

                    response_text = info.beautiful_text()[0] ##.beautiful_text возвращает кортеж, нулевой элемент - письменный текст
                    response_speak = info.beautiful_text()[1] ##Первый элемент - голосовой текст
                    response_img = info.get_product_img()  ##Получаем картинку продукта
                    users_products[user_id] = info.get_users_products()

                    ##Получаем стоп-лист
                    users_stop_list_products[user_id] = info.get_stop_list()

                    ##Если пользователь вводит команду впервые и продукт был найден
                    if users_first_command[user_id] == False and info.name != None:
                        
                        ##Сделаем response_speak для пользователя, который ввёл свою первую команду
                        response_speak = "Вы молодец! У вас круто получается!" + response_speak + "Хотите узнать больше о моих возможностях - вводите команду \"Помощь\"."

                        users_first_command[user_id] = True ##Ставим использование первой команды пользователем в True, дабы не писать более "Молодец!"
                        buttons = DefaultButtons

                    ##Если продукт не был найден
                    if info.name == None:
                        users_error_products[user_id] = product  ##Произошла ошибка, поэтому в словарь с ошибочными продуктами ставим продукт введённый пользователем
                        buttons = MoreAndErrorButtons ##В кнопки ставим "Больше" и "Ошибка"

                        ##Отправляем ответ алисе
                        return response_to_alice.simply_response(response_text, response_speak, buttons) ##Отсылаем ответ об ошибке в виде текста

                else: ##Если пользователь ввёл только активационное слово
                    response_text = "Необходимо указать название продукта!"
                    response_speak = response_text
                    buttons = OnlyMoreButton

                ##Отправляем ответ алисе
                return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)
            
            elif len(re.findall(r"\w*амм", text)) <= 0:
                print(users_states[user_id].states_list)
                product = text ##Продукт в именительном падеже и без мусорных слов

                info = InfoProduct(product, users_stop_list_products[user_id], users_products[user_id]) ##Инициализируем объект класса, в котором будет храниться вся информация о продукте

                title_card = info.get_title_card() ##Получаем заголовок для карточки

                response_text = info.beautiful_text()[0] ##.beautiful_text возвращает кортеж, нулевой элемент - письменный текст
                response_speak = info.beautiful_text()[1] ##Первый элемент - голосовой текст
                response_img = info.get_product_img()  ##Получаем картинку продукта
                users_products[user_id] = info.get_users_products()

                #print(f"Стоп-лист: {users_stop_list_products[user_id]}")

                ##Получаем стоп-лист
                users_stop_list_products[user_id] = info.get_stop_list()

                ##Если пользователь вводит команду впервые и продукт был найден
                if users_first_command[user_id] == False and info.name != None:
                    
                    ##Сделаем response_speak для пользователя, который ввёл свою первую команду
                    response_speak = "Вы молодец! У вас круто получается!\n\n" + response_speak + "\n\nХотите узнать больше о моих возможностях - вводите команду \"Помощь\"."

                    users_first_command[user_id] = True ##Ставим использование первой команды пользователем в True, дабы не писать более "Молодец!"
                    buttons = DefaultButtons

                ##Если продукт не был найден
                if info.name == None:
                    users_error_products[user_id] = product  ##Произошла ошибка, поэтому в словарь с ошибочными продуктами ставим продукт введённый пользователем
                    buttons = MoreAndErrorButtons ##В кнопки ставим "Больше" и "Ошибка"

                    ##Отправляем ответ алисе
                    return response_to_alice.simply_response(response_text, response_speak, buttons) ##Отсылаем ответ об ошибке в виде текста
                
            ##Ветка на "посчитай" или "рассчитай": посчитай гречку на 300 грамм
            if len(re.findall(r"п[оа][сз][чщ].?[ие][тд]а[йи]|р[оа][сз][сз]?ч[ие][тд]ай", text)) > 0:
                product = CorrectString().remove_other_words_to_calculate(text, ActivationCalculate["before"], ActivationCalculate["after"])
                info = InfoProduct(product[0], users_stop_list_products[user_id], users_products[user_id])
                users_stop_list_products[user_id] = info.get_stop_list()

                ##Если продукт был найден - считаем бжу на массу
                if info.name != None:         
                    if product[0] != product[1]:
                        info = info.calculate(product[1])
                        response_text = info[0]
                        response_speak = info[1]
                        buttons = DefaultButtons
                    elif product[0] == product[1]:
                        response_text = f"Необходимо указать корректный вес!\nНапример: посчитай {info.user_product_not_nominative} на 100 грамм"
                        response_speak = response_text
                        buttons = DefaultButtons

                        return response_to_alice.simply_response(response_text, response_speak, buttons)
                else: ##Если продукт не был найден
                    response_text = info.beautiful_text()[0]
                    response_speak = info.beautiful_text()[1]
                    buttons = MoreAndErrorButtons

                ##Отправляем ответ Алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь хочет узнать больше информации о командах
            if text.split(" ")[0] in ["помощь"]:
                response_text = "Я умею:\n• Считать пищевую ценность продукта на 100 грамм при помощи команды \"Расскажи про\" (расскажи про чай).\n• Рассказывать о случайном продукте с помощью команды \"Расскажи про случайный продукт\".\n• Советовать продукты с похожим количеством указанной характеристики (белков, жиров, углеводов, калорий). К примеру: \"посоветуй продукт с 10 граммами белка\".\n• Считать пищевую ценность в определенном весе продукта. Например: \"посчитай пельмени на 150 грамм\".\n• Подсказывать, сколько белков, жиров, углеводов и калорий съесть в день, исходя из личных характеристик человека (пола, возраста, веса, роста). Например: \"Сколько мне съесть в день?\".\n• Могу помочь подобрать блюдо по ингредиенту с помощью команды \"подбери блюдо\".\n• Играть в мини-игру с помощью команды \"Квест\"."
                response_speak = "Я умею sil <[200]> первое. Считать пищевую ценность продукта на сто грамм при помощи команды \"Расскажи пр+о\". второе. Рассказывать о случайном продукте с помощью команды \"Расскажи про случайный продукт\". третье. Советовать продукты с похожим количеством указанной характеристики. четвёртое. Считать пищевую ценность в определённом весе продукта. пятое. Подсказывать, сколько белков, жиров, углеводов и калорий съесть в день, исходя из личных характеристик человека. шестое. Могу помочь подобрать блюдо по ингредиенту с помощью команды \"подбери блюдо\" .седьмое. Играть в мини-игру с помощью команды \"Квэст\"."
                buttons = UserFirstCommands ##Пользователь уже в помощи, поэтому кнопки оставляем пустыми
                response_img = None

                ##Отправляем алисе сразу ответ
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            ##Если пользователь хочет отправить сообщение об ошибке
            elif text.split(" ")[0] in ActivationEmailWords:
                if len(users_error_products[user_id]) > 0: ##Если длина ошибочных продуктов больше 0
                    email_send.send_error_product(user_id, users_error_products[user_id])  ##Отсылаем на почту сообщение о ошибке с данным продуктом

                response_text = "Сообщение об ошибке успешно доставлено и будет рассмотрено модераторами."
                response_speak = "Ваша заявка будет рассмотрена модераторами. Можете вернуться к работе с навыком."
                buttons = MoreAndQuestButtons
                users_error_products[user_id] = []

                ##Отправляем алисе ответ
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            elif text in HelloWords: ##Если пользователь приветствует
                response_text = random.choice(HelloWords)
                response_text = response_text.split()[0].title() + " " + " ".join(response_text.split()[1::]) ##Делаем словосочетания с заглавной буквы
                response_speak = response_text
                buttons = MoreAndQuestButtons

                ##Отправляем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)

            elif text in ExitWords: ##Если пользователь прощается
                response_text = random.choice(LeaveWords)
                response_text = response_text.split()[0].title() + " " + " ".join(response_text.split()[1::]) ##Делаем словосочетания с заглавной буквы
                response_speak = response_text
                buttons = MoreAndQuestButtons

                ##Отправляем ответ алисе
                return response_to_alice.bye_response(response_text, response_speak)

            elif product == None:
                response_text = "Я вас не поняла..."
                response_speak = response_text
                buttons = OnlyMoreButton

                ##Возвращаем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)
        else:
            ##По сути, можно запихнуть в elif, но не очень уверен что тогда всё будет корректно работать
            if user_id not in users_first_command or users_first_command[user_id] == False:
                title_card = "Приветствуем вас в \"ИнфоЕде\"!"
                response_text = "Навык \"ИнфоЕда\" успешно запущен, теперь вы можете узнать пищевую ценность (содержание белков, жиров, углеводов, калорий) большинства продуктов!\nДля этого используйте команду \"Расскажи про\" и скажите название продукта.\nНапример: расскажи про чай. Также, в навык встроена и мини-игра! Для её активации просто используйте команду: \"квест\"."
                response_speak = "Навык \"Инфо+Еда\" успешно запущен, теперь вы можете узнать пищевую ценность большинства продуктов!\nДля этого используйте команду \"Расскажи пр+о\" и скажите название продукта.\nНапример: расскажи пр+о чай. Также, в навык встроена и мини-игра! Для её активации просто используйте команду: \"квэст\"."
                response_img = LOGO_IMG_ID ##Это первый ввод команды пользователем и поэтому отслылаем карточку с логотипом
                buttons = CalculateQuestMoreButtons

                users_first_command[user_id] = False ##Ставим в словаре с ключом айди то, что пользователь не написал первую команду
                users_stop_list_products[user_id] = [] ##В значение стоп листа ставим пустой список, дабы потом в него осуществлять добавку при вводе пользователем продуктов
                users_playing_quest[user_id] = False ##В значение игры в квест ставим False, поскольку навык был перезапущен
                users_quest[user_id] = None

            ##Если пользователь уже был в навыке и вводил первую команду (грубо говоря, если пользователь очистил диалоговое окно с навыком)
            elif user_id in users_first_command and users_first_command[user_id] == True:
                title_card = "\"ИнфоЕда\" успешно запущен!"
                response_text = f"И снова здравствуйте!\nЧтобы узнать пищевую ценность продукта на 100 грамм - вводите команду \"Расскажи про\" и название продукта (например: расскажи про чай). Хотите поиграть в игру - используйте команду \"квест\". Узнать больше о моих возможностях вы можете с помощью команды: \"Помощь\"."
                response_speak = f"И снова здравствуйте!\nЧтобы узнать пищевую ценность продукта на 100 грамм - вводите команду \"Расскажи пр+о\" и название продукта (например: расскажи пр+о чай). Хотите поиграть в игру - используйте команду \"квест\". Узнать больше о моих возможностях вы можете с помощью команды: \"Помощь\"."
                buttons = CalculateQuestMoreButtons
                response_img = LOGO_IMG_ID

                users_stop_list_products[user_id] = []
                users_playing_quest[user_id] = False ##В значение игры в квест ставим False,  поскольку навык был перезапущен
                users_quest[user_id] = None

                meet_again = True
            
            ##Если ничего из перечисленного в условиях выше не подходит
            else:
                response_text = "Я не смогла распознать вашу команду..."
                response_speak = response_text
                buttons = OnlyMoreButton

                ##Возвращаем ответ алисе
                return response_to_alice.simply_response(response_text, response_speak, buttons)
        
        ##Если пользователь впервые в навыке или если очистил окно с диалогом внутри навыка (за это и отвечает meet_again)
        if users_first_command[user_id] == False or meet_again:
            ##Ответ при первом запуске     
            if response_img != None:
                return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)
            else:
                return response_to_alice.simply_response(response_text, response_speak, buttons)

        ##Если картинка не None (если в ответе будет картинка, т.е., ответ подразумевается в виде карточки)
        if response_img != None:
            return response_to_alice.card_response(response_img, title_card, response_text, response_speak, buttons)
        else:
            ##Ответ с помощью объекта response (для полноты смотреть classes -> responses.py -> Responses)
            return response_to_alice.simply_response(response_text, response_speak, buttons)
    except: ##Ловим ошибки
        response_text = "Я вас не поняла..."
        response_speak = response_text
        buttons = CalculateQuestMoreButtons

        #Ответ алисе
        return response_to_alice.simply_response(response_text, response_speak, buttons)

##Точка входа
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)