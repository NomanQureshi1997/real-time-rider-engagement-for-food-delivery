from flask import jsonify
from datetime import datetime
import random
import subprocess

# Path to the queue job
script_path = './queues/dispatching_orders.py'

total_steps = random.randint(3, 20)
total_time = random.randint(10, 60)

def find_avaiable_driver(db): 
    driver = db.drivers.find_one({'available_status': True})
    if driver:
        return driver
    else:
        return 'not_found'
    
def save_order(order_bp, driver_id = None):
    order_id = order_bp.db.orders.insert_one({
        'name': 'A new Order',
        'status': 'pending',
        'total_steps': total_steps,
        'total_time': total_time,
        'driver': driver_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }).inserted_id

    return order_id, total_steps, total_time

def order_success_response(order_id, driver_id, queued):
    return jsonify({
        'message': 'Order placed successfully', 
        'order_id': str(order_id),
        'driver_id': str(driver_id),
        'queued': queued,
        'error': False}), 201

def execute_order_in_background(driver_id, order_id, total_steps, total_time, db):
    # Create a list of parameters to be passed to the subprocess command
    parameters = [str(driver_id), str(order_id), str(total_steps), str(total_time)]

    # Launch a subprocess with Python script and parameters
    process = subprocess.Popen(['python', script_path] + parameters)

    # Obtain the process ID (PID) of the subprocess
    pid = process.pid

    # Update the orders collection in the database with the subprocess ID
    db.orders.update_one(
        {'_id': order_id},
        {'$set': {'sub_process_id': pid}},
        upsert=True
    )

# This is a common function designed to update the status of any table.
# In our specific case, we require it to update the status of both drivers and orders.
def update_status(db , object_id, key, status):
    db.update_one(
        {'_id': object_id},
        {'$set': {key: status}}
    )

def send_unexpected_error():
    return jsonify({'message': 'Something went wrong! We are on to resolve the issue'}), 500


