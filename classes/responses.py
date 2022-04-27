##Класс содержащий различные виды ответов для Алисы
class Responses:

    ##Инициализатор для всовывания конца сессии и версии в атрибуты класса
    def __init__(self, end: bool, version: str):
        self.end = end
        self.version = version

    ##Обыкновенный ответ в виде текста
    def simply_response(self, response_text: str, response_speak: str, buttons: dict):
        ##Тело ответа
        response = {
            "response": {
                "text": response_text,
                "tts": response_speak,
                "end_session": self.end,
                "buttons": buttons
            },
            "version": self.version
        }
    
        return response
    
    ##Прощальный ответ
    def bye_response(self, response_text: str, response_speak: str):
        ##Тело ответа
        response = {
            "response": {
                "text": response_text,
                "tts": response_speak,
                "end_session": True
            },
            "version": self.version
        }
    
        return response

    ##Ответ в виде карточки
    def card_response(self, image_id:str, title_card: str, response_text: str, response_speak: str, buttons: dict):
        ##Тело ответа
        response = {
                "response": {
                    "text": response_text,
                    "tts": response_speak, ##Алиса будет это говорить
                    "end_session": self.end,
                    "buttons": buttons, ##Кнопка которая и станет первой командой пользователя с подсчётом ценности продукта (например, чая) при первом запуске навыка и команда "Помощь" если пользователь уже пользовался навыком

                    ##Карточка - блок с картинкой, далее заголовком и текстом
                    "card": {
                        "type":"BigImage",
                        "image_id": image_id, ##Алиса будет это отображать сверху карточки (Картинка)
                        "title": title_card, ##Это текст заголовка (под картинкой)
                        "description": response_text, ##Это текст карточки (под заголовком)
                    }
                },
                "version": self.version
            }

        return response
