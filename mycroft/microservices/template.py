from mycroft.microservices.base import *


@app.route("/intent/<utterance>", methods=['GET'])
@noindex
@btc
@requires_auth
def intent(utterance):
    result = {"error": "not implemented"}
    return nice_json(result)


@app.route("/ask/<utterance>", methods=['GET'])
@noindex
@btc
@requires_auth
def ask(utterance):
    result = {"error": "not implemented"}
    return nice_json(result)


@app.route("/stt/recognize", methods=['PUT'])
@noindex
@btc
@requires_auth
def stt():
    file_data = request.data
    result = {"error": "not implemented"}
    return nice_json(result)


@app.route("/tts/<voice>/<sentence>", methods=['GET'])
@noindex
@btc
@requires_auth
def tts(voice, sentence):
    result = {"error": "not implemented"}
    return nice_json(result)


if __name__ == "__main__":
    global app
    port = 6712
    start(app, port)
712