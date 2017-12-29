import requests
from requests.exceptions import ConnectionError


class MycroftAPI(object):
    def __init__(self, api, lang="en-us", url="https://0.0.0.0:6712/"):
        self.api = api
        self.headers = {"Authorization": str(self.api)}
        self.lang = lang
        self.url = url

    def hello_world(self):
       try:
           response = requests.get(
               self.url,
               headers=self.headers, verify=False
           )
           return response.text
       except ConnectionError as e:
           print e
           raise ConnectionError("Could not connect")

    def new_user(self, key, id, name):
        #
        try:
            response = requests.put(
                self.url+"new_user/"+key+"/"+id+"/"+name,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid admin api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")

    def get_api(self):
        #
        try:
            response = requests.get(
                self.url+"get_api",
                headers=self.headers, verify=False
            )
            try:
                return response.json()["api"]
            except:
                print response.text
                raise ValueError("Invalid admin api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")

    def get_intent(self, utterance, lang=None):
        lang = lang or self.lang
        try:
            response = requests.get(
                self.url+"/intent/"+lang+"/"+utterance,
                headers=self.headers, verify=False
            )
            try:
                return response.json()["echo"]
            except:
                print response.text
                raise ValueError("Invalid api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")

    def ask_mycroft(self, utterance, lang=None):
        lang = lang or self.lang
        try:
            response = requests.get(
                self.url+"ask/"+lang+"/"+utterance,
                headers=self.headers, verify=False
            )
            try:
                return response.json()
            except:
                print response.text
                raise ValueError("Invalid api key")
        except ConnectionError as e:
            print e
            raise ConnectionError("Could not connect")



# test connection
#print ap.hello_world()

# test if admin privileges are properly blocked
#ap = MycroftAPI("test_key")
#try:
#    print ap.new_user("new_key", "0", "test")
#    print "whoa, anyone can make himself an user_id"
#except:
#    pass
#try:
#    print ap.get_api()
#    print "whoa, anyone can generate an api key"
#except:
#    pass

# test if admin privileges are properly allowed

#ap = MycroftAPI("admin_key")
#print ap.new_user("new_key", "0", "test")
#print ap.get_api()

# test functionality
ap = MycroftAPI("test_key")
print ap.ask_mycroft("hello world")
print ap.ask_mycroft("do you like pizza")
print ap.ask_mycroft("tell me a joke")
