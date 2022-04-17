from dialogic.dialog_connector import DialogConnector
from dialogic.dialog_manager import TurnDialogManager
from dialogic.server.flask_server import FlaskServer
from dialogic.cascade import DialogTurn, Cascade

csc = Cascade()


@csc.add_handler(priority=10, regexp='(hello|hi|привет|здравствуй)')
def hello(turn: DialogTurn):
    turn.response_text = 'Привет! Это единственная условная ветка диалога.'


@csc.add_handler(priority=1)
def fallback(turn: DialogTurn):
    turn.response_text = 'Я вас не понял. Скажите мне "Привет"!'
    turn.suggests.append('привет')


dm = TurnDialogManager(cascade=csc)
connector = DialogConnector(dialog_manager=dm)
server = FlaskServer(connector=connector)

if __name__ == '__main__':
    server.parse_args_and_run()