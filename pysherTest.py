import json
from time import sleep
import pysher


pusher = pysher.Pusher(u"anykey", cluster='mt1', secure=False, secret=u'anysecret', port=6001,
                       custom_host='localhost', http_proxy_auth='localhost:8000/sanctum/csrf-cookie')


def handleGSExtendEvent(*args, **kwargs):
    print("####################### Extend Handle #######################")
    print("processing Args:", args)
    temp = json.loads(args[0])
    print("prof", temp)
    print("processing Kwargs:", kwargs)


def connect_handler(data):
    channel = pusher.subscribe('pythonChannel')
    print('connected to channel [pythonChannel]')
    channel.bind('App\Events\GsExtendEvent', handleGSExtendEvent)
    print('bounded the Event to the function')


# subscribe to the channel and add an event listener
pusher.connection.bind('pusher:connection_established', connect_handler)
pusher.connect()

while True:
    sleep(1)
