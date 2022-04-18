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
    
    ##Ответ в виде карточки
    def card_response(self, image_id:str, title_card: str, response_text: str, response_speak: str, buttons: dict):
        response = {
                "response": {
                    "text": response_text,
                    "tts": response_speak, ##Алиса будет это говорить
                    "end_session": self.end,
                    "buttons": buttons, ##Кнопка которая и станет первой командой пользователя с подсчётом ценности продукта (например, чая) при первом запуске навыка и команда "Больше" если пользователь уже пользовался навыком

                    ##Карточка - блок с картинкой, далее заголовком и текстом
                    "card": {
                        "type":"BigImage",
                        "image_id": "937455/e1833075f705a4649b2c",
                        "title": title_card,
                        "description": response_text, ##Алиса будет это отображать в карточке
                    }
                },
                "version": self.version
            }

        return response