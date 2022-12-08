import json
from flask import Flask, request, jsonify, render_template, make_response
from flask_mqtt import Mqtt

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = '13.105.113.2' # IP address of broker running on edgezone
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'client1'  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = 'password'  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True

# MQTT Topics
result = 'result'
orders = 'orders'
new_order = 'new-order'

mqtt_client = Mqtt(app)

results = []
newOrder = []

@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('index.html')

@app.route('/post_items_placement', methods=["POST"])
def item_placement():
    # process JSON
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json_data = request.json
        # sample json data
        # {'bag_no': 1, 'item_name': 'soda', 'action': 'add'}
        mqtt_client.publish(topic=orders, payload=json.dumps(json_data), qos=1, retain=False)
        print (json.dumps(json_data))
        return json_data
    return 'Content-Type not supported'

@app.route('/data', methods=["GET", "POST"])
def data():
    response = make_response(json.dumps(results))
    response.content_type = 'application/json'
    print(response)
    results.clear()
    return response

@app.route('/newOrder', methods=["GET", "POST"])
def getNewOrder():
    response = make_response(json.dumps(newOrder))
    response.content_type = 'application/json'
    print(response)
    newOrder.clear()
    return response

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        # subscribe to topics
        mqtt_client.subscribe(result)
        mqtt_client.subscribe(new_order)
    else:
        print('Bad connection. Code:', rc)

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
  )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    if message.topic == result:
        results.append(data['payload'])
    if message.topic == new_order:
        newOrder.append(data['payload'])

if __name__ == '__main__':
    app.run(debug=True)
