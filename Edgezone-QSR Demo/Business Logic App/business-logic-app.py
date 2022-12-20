import json
import logging
import time
from datetime import datetime

import paho.mqtt.client as mqtt

broker_url = "<mqtt broker IP address>" # IP address of broker running on edgezone
broker_port = 1883
pos_orders = []

#method is called once a inbounded message is recieved on topic "orders"
def on_message(client, userdata, message):
    
    #decode the incoming message 
    # sample json data: {'bag_no': 1, 'item_name': 'soda', 'action': 'add'}
    json_in_order = json.loads(str(message.payload.decode("utf-8","ignore"))) #decode json data
    print("Message Recieved: ", json_in_order)
    
    # initate a tempory list to compare the incoming item to POS order
    # loads the POS order for bag number to compare
    order_compare = [""]
    for i in range(0, len(pos_orders)):
        if pos_orders[i]["bag_no"] == json_in_order["bag_no"]:
            order_compare = pos_orders[i]["items"]

    # order is a key-value hashmap which is an associative array
    # if item addded to bag is part of the order, make status true
    # if item added to bag is not part of the order, status is false
    if json_in_order["item_name"] in order_compare[0].keys():
        if json_in_order["action"] == "add":
            json_out = json_in_order
            json_out["Status"] = True
            order_compare[0][json_in_order["item_name"]] -= 1
            if isOrderComplete(order_compare[0]):
                order_complete = {"bag_no": json_in_order["bag_no"], "Status": "order-completed"}
                print("Messages to Publish: ", order_complete)
                client.publish(topic="result", payload=json.dumps(order_complete), qos=1, retain=False)           
        elif json_in_order["action"] == "remove":
            json_out = json_in_order
            json_out["Status"] = False
    # if item added to bag is not in the order check if being added or removed from bag
    # if being added and it's not part of order, status is false
    # if being removed and is not part of the order, status is false
    elif json_in_order["item_name"] not in order_compare[0].keys():
        if json_in_order["action"] == "add":
            json_out = json_in_order
            json_out["Status"] = False
        elif json_in_order["action"] == "remove":
            json_out = json_in_order
            json_out["Status"] = True
            if isOrderComplete(order_compare[0]):
                order_complete = {"bag_no": json_in_order["bag_no"], "Status": "order-completed"}
                print("Messages to Publish: ", order_complete)
                client.publish(topic="result", payload=json.dumps(order_complete), qos=1, retain=False)
                    
    print("Messages to Publish: ", json_out)    
    #publish the result to broker
    client.publish(topic="result", payload=json.dumps(json_out), qos=1, retain=False)
    
# method is called once a inbounded message is recieved on topic "new-order"
def on_message_neworder(client, userdata, message):   
    #decode the incoming message 
    order = json.loads(str(message.payload.decode("utf-8","ignore"))) #decode json data
    # sample json data: {"bag_no" : 1, "items" : [{"French Fries" : 1, "Cheeseburger" : 1, "Soda" : 1, "Chicken Nuggets" : 1}]}
    print("Order received from PoS application", order)
    pos_orders.append(order)

# method evaluate if order is complete
def isOrderComplete(order):
    for value in order.values():
       if value >= 1:
        return False
    return True


#configure the client and connect 
client = mqtt.Client()

#client subscribes to two topics "orders" the incoming items being placed in the bag
# the second topic is "new-order" the actual order from the POS system
client.message_callback_add("orders", on_message)
client.message_callback_add("new-order", on_message_neworder)
client.username_pw_set(username="client2", password="password2")
client.connect(broker_url, broker_port, keepalive=800)

# start loop to process recieved messages
client.loop_start()
# subscribe to incoming order items as it is being filled
client.subscribe("orders")
# subscribe to the POS order 
client.subscribe("new-order")
# keep loop running for n seconds
time.sleep(6000)

# disconnect and stop loop
client.disconnect()
client.loop_stop()
