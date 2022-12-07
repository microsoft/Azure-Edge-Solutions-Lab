import json
import logging
import time
from datetime import datetime

import paho.mqtt.client as mqtt

broker_url = "13.105.113.2"
broker_port = 1883
orders = []

#define callback
def on_message(client, userdata, message):
    
    #decode the incoming message 
    # sample json data
        # {'bag_no': 1, 'item_name': 'soda', 'action': 'add'}
    json_in_order = json.loads(str(message.payload.decode("utf-8","ignore"))) #decode json data
    print("Action: ", json_in_order)
    # fetch order to check 
    # {"bag_no" : 1, "items" : [{"French Fries" : 1, "Cheeseburger" : 1, "Soda" : 1, "Chicken Nuggets" : 1}]}
    order = [""]
    for i in range(0, len(orders)):
        if orders[i]["bag_no"] == json_in_order["bag_no"]:
            order = orders[i]["items"]
    # order is a key-value hashmap
    if json_in_order["item_name"] in order[0].keys():
        if json_in_order["action"] == "add":
            json_out = json_in_order
            json_out["Status"] = True
            order[0][json_in_order["item_name"]] -= 1           
        elif json_in_order["action"] == "remove":
            json_out = json_in_order
            json_out["Status"] = False
    elif json_in_order["item_name"] not in order[0].keys():
        if json_in_order["action"] == "add":
            json_out = json_in_order
            json_out["Status"] = False
        elif json_in_order["action"] == "remove":
            json_out = json_in_order
            json_out["Status"] = True
            
            
    print("Messages to Publish: ", json_out)    
    #publish the result to broker
    client.publish(topic="result", payload=json.dumps(json_out), qos=1, retain=False)
    if isOrderComplete(order[0]):
        order_complete = {"bag_no": json_in_order["bag_no"], "Status": "order-completed"}
        print("Messages to Publish: ", order_complete)
        client.publish(topic="result", payload=json.dumps(order_complete), qos=1, retain=False)

def on_message_neworder(client, userdata, message):
    #decode the incoming message 
    order = json.loads(str(message.payload.decode("utf-8","ignore"))) #decode json data
    # {"bag_no" : 1, "items" : [{"French Fries" : 1, "Cheeseburger" : 1, "Soda" : 1, "Chicken Nuggets" : 1}]}
    print("Order received from PoS application", order)
    orders.append(order)

def isOrderComplete(order):
    for value in order.values():
       if value >= 1:
        return False
    return True

#configure the client and connect 
client = mqtt.Client()
#client.on_message = on_message
client.message_callback_add("orders", on_message)
client.message_callback_add("new-order", on_message_neworder)
client.username_pw_set(username="client2", password="password2")
client.connect(broker_url, broker_port, keepalive=800)

# start loop to process recieved messages
client.loop_start()
# subscribe to incoming order
client.subscribe("orders")
client.subscribe("new-order")
# keep loop running for 60 seconds
time.sleep(6000)

# disconnect and stop loop

client.disconnect()
client.loop_stop()
