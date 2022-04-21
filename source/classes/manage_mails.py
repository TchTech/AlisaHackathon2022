import smtplib
from email.message import EmailMessage

##Класс для отправки писем
class EmailSend:
    ##Инициализатор для авторизации
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    ##Отправка сообщения: Ошибка ненахода продукта в бд
    def send_error_product(self, user_id: str,  product: str) -> bool:
        msg = EmailMessage()  ##Сообщение
        msg["Subject"] = "---Ошибка навыка Яндекс---"  ##Тема сообщения
        msg["From"] = "Навык Яндекс (ИнфоЕда)"  ##От кого это сообщение
        msg["To"] = "main.alice.email@gmail.com"  ##На какую почту это сообщение будет отправлено
        msg.set_content(f"ID пользователя: {user_id}.\nОшибка: в навыке \"ИнфоЕда\" не был найден продукт: {product}")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  ##Делаем сервер
        server.login(self.email, self.password)  ##Авторизуемся
        server.send_message(msg)  ##Отправляем сообщение 
