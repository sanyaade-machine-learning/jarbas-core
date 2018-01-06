# JarbasAPI

the microservices should be started before the skills process

# Processing an utterance

    from mycroft.microservices.api import MycroftAPI

    ap = MycroftAPI("api_key")
    json_response = ap.ask_mycroft("hello world")

# Admin functions

some functions require an admin api key

    ap = MycroftAPI("admin_key")

    # get an api key string
    api = ap.get_api()

    # add a new user with api=generated_key, id=0, name=test
    print ap.new_user("new_key", "0", "test")

# Determining Intents

    from mycroft.microservices.api import MycroftAPI

    ap = MycroftAPI("api_key")

    # what intent will this utterance trigger
    intent = ap.get_intent("hello world")

    # what intents are registered {"skill_id": ["intent", "list"] }
    intent_dict = ap.get_intent_map()

# Determining Vocab

    from mycroft.microservices.api import MycroftAPI

    ap = MycroftAPI("api_key")

    # what vocab is registered {"word": "MatchingKeyword" }
    intent_dict = ap.get_vocab_map()
