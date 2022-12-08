import paho.mqtt.client as mqtt
from datetime import datetime
import json
import time

broker_url = "13.105.113.2" # IP address of broker running on edgezone
broker_port = 1883

client = mqtt.Client()
client.username_pw_set(username="client1", password="password")
client.connect(broker_url, broker_port)
client.loop_start()

json_data_bag_1 = {"bag_no" : 1, "items" : [{"French Fries" : 1, "Cheeseburger" : 1, "Soda" : 1, "Chicken Nuggets" : 1}]}
json_data_bag_2 = {"bag_no" : 2, "items" : [{"French Fries" : 1, "Soda" : 1, "Fish Sandwich" : 1, "Chicken Sandwich" : 1, "Spicy Chicken Sandwich" : 1}]}


client.publish(topic="new-order", payload=json.dumps(json_data_bag_1), qos=1, retain=False)
time.sleep(5)
client.publish(topic="new-order", payload=json.dumps(json_data_bag_2), qos=1, retain=False)

client.disconnect()
client.loop_stop()
