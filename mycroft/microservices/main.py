from mycroft.microservices.base import *
from mycroft.skills.intent_service import IntentService
from mycroft.util import LOG
from mycroft.util.parse import normalize
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from threading import Thread
from time import sleep
from Queue import Queue

ws = None
queue = Queue()
waiting = False
reply = ""
user_id = ""
answer_utt = ""
answer = None
intents = None
timeout = 10


def connect():
    global ws
    ws.run_forever()


@app.route("/intent/<lang>/<utterance>", methods=['GET'])
@noindex
@btc
@requires_auth
def intent(utterance, lang="en-us"):
    result = {}
    try:
        # normalize() changes "it's a boy" to "it is boy", etc.
        best_intent = next(intents.engine.determine_intent(
            normalize(utterance, lang), 100,
            include_tags=True,
            context_manager=intents.context_manager))
        # TODO - Should Adapt handle this?
        best_intent['utterance'] = utterance
        result = best_intent
    except StopIteration:
        # don't show error in log
        pass
    except Exception as e:
        LOG.exception(e)
    return nice_json(result)


@app.route("/ask/<utterance>", methods=['GET'])
@noindex
@btc
@requires_auth
def ask(utterance):
    global user_id
    ip = request.remote_addr
    user = request.headers["Authorization"]
    data = {"utterances": [utterance]}
    user_id = str(ip) + ":" + str(user)
    context = {"source": ip, "target": user, "user_id": user_id}
    message = Message("recognizer_loop:utterance", data, context)
    result = get_answer(message, "speak", context)
    return nice_json(result)


def get_answer(message=None, reply="speak", context=None):
    global ws, queue, answer, waiting
    answer = None
    queue.put((message, reply))
    start = time.time()
    while answer is None and time.time() - start < timeout:
        sleep(0.1)
    waiting = False
    # TODO use dialog file for time out
    return answer or Message(reply, {"utterance": "server timed out"},
                             context).serialize()


@app.route("/stt/recognize", methods=['PUT'])
@noindex
@btc
@requires_auth
def stt():
    file_data = request.data
    path = "{}/stt.wav".format(root_dir())
    with open(path, "wb") as f:
        f.write(file_data)
    result = {"error": "not implemented"}
    return nice_json(result)


@app.route("/tts/<voice>/<sentence>", methods=['GET'])
@noindex
@btc
@requires_auth
def tts(voice, sentence):
    result = {"error": "not implemented"}
    return nice_json(result)


def asker():
    global queue, ws, waiting, reply
    while True:
        if queue.empty() or waiting:
            sleep(0.1)
            continue
        message, reply = queue.get()
        waiting = True
        ws.on(reply, listener)
        ws.emit(message)


def listener(message):
    global answer, user_id, ws, answer_utt
    message.context = message.context or {}
    if message.context.get("user_id", "") == user_id:
        message.context["source"] = "https_server"
        if "utterance" in message.data.keys():
            answer_utt += message.data["utterance"] + " "
        # use last message, update utterance only
        answer = message


def end_wait(message):
    global answer, answer_utt, waiting
    if not waiting:
        return
    if "utterance" in answer.data.keys():
        answer.data["utterance"] = answer_utt
    answer_utt = ""
    answer = answer.serialize()
    waiting = False

if __name__ == "__main__":
    global app, ws
    # connect to internal mycroft
    ws = WebsocketClient()
    ws.on("mycroft.skill.handler.complete", end_wait)
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()
    asker_thread = Thread(target=asker)
    asker_thread.setDaemon(True)
    asker_thread.start()
    #intents = IntentService(ws)
    port = 6712
    start(app, port)
