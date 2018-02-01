from mycroft.server.microservices.api import MycroftAPI

if __name__ == "__main__":
    # test if admin privileges are properly blocked
    ap = MycroftAPI("test_key", url="https://127.0.1.1:6712/")
    while True:
        line = raw_input("Input: ")
        res = ap.ask_mycroft(line.lower())
        print "Jarbas: ", res.get("data", {}).get("utterance", "")