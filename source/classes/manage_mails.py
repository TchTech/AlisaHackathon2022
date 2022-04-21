import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mail():

    sender_mail = {} #Словарь с данными о письме отправителя

    def __init__(self, address: str, password: str): #Создаем объект адреса, с которого будут отправляться письма

        self.sender_mail["address"] = address
        self.sender_mail["password"] = password


    def send(self, receiver_email: str, theme: str, body: str, filename:str = None):

        message = MIMEMultipart() #Заполнение информации о письме: Тема, Отправитель, Получатель
        message["Subject"] = theme
        message["From"] = self.sender_mail["address"]
        message["To"] = receiver_email

        msgtext = MIMEText(body, "plain") #Создание текста в письме
        message.attach(msgtext) #Добавление его в письмо

        if filename != None: #Если есть прикрепленный файл

            with open(filename, "rb") as attachment: #Открывается файл и с него считывается информация
                msgfile = MIMEBase("application", "octet-stream")
                msgfile.set_payload(attachment.read())

            encoders.encode_base64(msgfile) #Декодировка в base64
            msgfile.add_header("Content-Disposition", f"attachment; filename= {filename}",) #Добавление файла в шапку
            message.attach(msgfile) #Добавление его в письмо

        text = message.as_string() #Превращение экземпляра класса MIMEMultipart() в строку

        context = ssl.create_default_context() #Создание контекста с безопасными настройками по умолчанию

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server: #Подключение к гугл письмам
            server.login(self.sender_mail["address"], self.sender_mail["password"]) #Логин почты отправителя
            server.sendmail(self.sender_mail["address"], receiver_email, text) #Отправка письма
