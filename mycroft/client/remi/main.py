from remi import start, App, gui
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft import Message
import random
from threading import Thread


class RemiClient(App):
    def __init__(self, *args):
        super(RemiClient, self).__init__(*args)

    def connect(self):
        self.emitter.run_forever()

    def initalize_messages(self):
        self.emitter.on("speak", self.on_speak)

    def speak(self, utterance):
        self.emitter.emit(Message("speak", {"utterance": utterance},
                                  {"source": self.name}))

    def on_speak(self, message):
        destinatary = message.context.get("destinatary", "")
        if destinatary == self.name and message.type == "speak":
            utterance = message.data.get("utterance", "")
            self.history_widget.append(
                "Jarbas: " + utterance.replace("chat:", "").lower())

    def main(self):
        self.suggestions = ["hello world",
                            "do you like pizza",
                            "tell me about nicola tesla",
                            "tell me a joke"]
        self.utterance = ""
        self.emitter = WebsocketClient()
        self.name = "remi_gui"
        self.event_thread = Thread(target=self.connect)
        self.event_thread.setDaemon(True)
        self.event_thread.start()
        self.initalize_messages()
        # returning the root widget
        return self.get_chat_widget()

    def get_chat_widget(self):
        verticalContainer = gui.Widget(width=400, margin='0px auto',
                                       style={'display': 'block',
                                              'overflow': 'hidden'})
        chatButtonContainer = gui.Widget(width=400,
                                         layout_orientation=gui.Widget.LAYOUT_HORIZONTAL,
                                         margin='0px',
                                         style={'display': 'block',
                                                'overflow': 'auto'})

        self.history_widget = gui.ListView.new_from_list((), width=500,
                                                         height=300,
                                                         margin='10px')

        self.txt_input = gui.TextInput(width=400, height=30, margin='10px')
        self.txt_input.set_text('chat: ')
        self.txt_input.set_on_change_listener(self.on_chat_type)
        self.txt_input.set_on_enter_listener(self.on_chat_enter)

        send_button = gui.Button('Send', width=150, height=30, margin='10px')
        send_button.set_on_click_listener(self.on_chat_click)

        sug_button = gui.Button('Suggestion', width=150, height=30,
                                margin='10px')
        sug_button.set_on_click_listener(self.on_sug_click)

        chatButtonContainer.append(send_button)
        chatButtonContainer.append(sug_button)

        verticalContainer.append(self.txt_input)
        verticalContainer.append(chatButtonContainer)
        verticalContainer.append(self.history_widget)
        return verticalContainer

    def on_sug_click(self, widget):
        sug = random.choice(self.suggestions)
        self.txt_input.set_text('chat: ' + sug)
        self.utterance = sug

    def on_chat_type(self, widget, newValue):
        self.utterance = str(newValue)

    def on_chat_click(self, widget):
        payload = {
            "utterances": [self.utterance.replace("chat:", "").lower()]}
        context = {"source": self.name}
        self.emitter.emit(Message("recognizer_loop:utterance", payload,
                                  context))
        self.history_widget.append("you: " + self.utterance.replace("chat:",
                                                                    "").lower())
        self.txt_input.set_text('chat: ')
        self.utterance = ""

    def on_chat_enter(self, widget, userData):
        self.utterance = userData
        payload = {
            "utterances": [self.utterance.replace("chat:", "").lower()]}
        context = {"source": "gui"}
        self.emitter.emit(Message("recognizer_loop:utterance", payload,
                                  context))
        self.history_widget.append("you: " + self.utterance.replace("chat:",
                                                                    "").lower())
        self.txt_input.set_text('chat: ')
        self.utterance = ""


def start_server(host='127.0.0.1', port=8171):
    start(RemiClient, address=host, port=port, multiple_instance=True,
          enable_file_cache=True, update_interval=0.1, start_browser=False)


def start_standalone():
    start(RemiClient, standalone=True)


if __name__ == "__main__":
    start_standalone()
