from flask import Blueprint, jsonify
from services.orders_service import find_avaiable_driver, save_order, order_success_response, execute_order_in_background, update_status, send_unexpected_error
from bson import ObjectId
import os
from bson import json_util
order_bp = Blueprint('order', __name__)

@order_bp.route('/place_order', methods=['POST'])
def place_order():
    try: 
        # Find an available driver from the database
        driver = find_avaiable_driver(order_bp.db)

        # If no available driver is found
        if driver == 'not_found':
            # Save the order and execute it in the background
            order_id, total_steps, total_time = save_order(order_bp)
            execute_order_in_background('', order_id, total_steps, total_time, order_bp.db)
            return order_success_response(order_id, '', True)
        
        # If an available driver is found
        order_id, total_steps, total_time = save_order(order_bp, driver.get('_id'))

        # Update the driver's status to unavailable
        update_status(order_bp.db.drivers, driver.get('_id'), 'available_status', False)

        # Execute the order in the background with the assigned driver
        execute_order_in_background(driver.get('_id'), order_id, total_steps, total_time, order_bp.db)

        return order_success_response(order_id, driver.get('_id') ,False)
    
    except Exception as e:
        print("An error occurred while placing the order:", e)
        return send_unexpected_error()

    

@order_bp.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = order_bp.db.orders.find_one({'_id': ObjectId(order_id)})

        if order:
            order['_id'] = str(order['_id'])
            order['driver'] = str(order['driver'])
            del(order['sub_process_id'])
            return jsonify(order), 200
        else:
            return jsonify({'message': 'Order not found'}), 404
    except Exception as e:
        print("An error occurred while placing the order:", e)
        return send_unexpected_error()
    
@order_bp.route('/order/<order_id>', methods=['Delete'])
def cancel_order(order_id):
    try:
        order = order_bp.db.orders.find_one({
            '_id': ObjectId(order_id),
            'status': 'pending'},
        )

        if order:
            os.kill(order['sub_process_id'], 9)
        
            update_status(order_bp.db.orders, ObjectId(order_id), 'status', 'canceled')
            update_status(order_bp.db.drivers, order['driver'], 'available_status', True)
            
            return jsonify({'message': f'Order {order_id} has been canceled'}), 404
        else:
            return jsonify({'message': 'Order not found, or Already completed'}), 404
    except Exception as e:
        print("An error occurred while placing the order:", e)
        return send_unexpected_error()
    
@order_bp.route('/drivers', methods=['GET'])
def get_all_drivers():
    try:
        # Query the database to fetch all drivers
        drivers = order_bp.db.drivers.find()

        # Convert the cursor to a list of dictionaries
        drivers_list = list(drivers)

        # Convert the list of dictionaries to JSON format
        drivers_json = json_util.dumps(drivers_list)

        # Return the JSON response
        return drivers_json, 200
    except Exception as e:
        print("An error occurred while placing the order:", e)
        return send_unexpected_error()