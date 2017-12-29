import requests
from requests.exceptions import ConnectionError


class MycroftAPI(object):
    URL = "https://0.0.0.0:6712/"

    def __init__(self, api):
        self.api = api
        self.headers = {"Authorization": str(self.api)}

    def hello_world(self):
       try:
           response = requests.get(
               MycroftAPI.URL,
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
                MycroftAPI.URL+"new_user/"+key+"/"+id+"/"+name,
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
                MycroftAPI.URL+"get_api",
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

    def get_intent(self, utterance, lang="en-us"):
        try:
            response = requests.get(
                MycroftAPI.URL+"/intent/"+lang+"/"+utterance,
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

    def ask_mycroft(self, utterance):
        try:
            response = requests.get(
                MycroftAPI.URL+"ask/"+utterance,
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
#print ap.get_intent("hello world")
