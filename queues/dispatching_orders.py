import sys
from pathlib import Path
import time
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
import os
parent_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(parent_dir))
from services.orders_service import find_avaiable_driver, update_status


# Load environment variables from .env file
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)
db = client.get_default_database()

def main():
    # Extract command-line arguments
    args = sys.argv[1:]

    total_time = int(args[3])
    total_steps = int(args[2])
    driver_id = str(args[0])
    order_id = ObjectId(args[1])
    
    # If a driver is unavailable, the queue will wait for one to become available every five seconds.
    waiting_for_driver = 0
    while driver_id == '':
        id = find_avaiable_driver(db)
        if id != 'not_found':
            driver_id = str(id.get('_id'))
            update_status(db.orders, order_id, 'driver', id.get('_id'))
            # Update the driver's status to unavailable
            update_status(db.drivers, id.get('_id'), 'available_status', False)
            print(f"Driver found: {driver_id}, Dispatching Order")
        time.sleep(5)
        print('No Driver Found Yet')
        waiting_for_driver += 5
        if(waiting_for_driver > 120):
            update_status(db.orders, order_id, 'status', 'canceled')
            print(f"Order canceled {str(order_id)}")
            sys.exit()

    # Order completion time will start at this point
    while total_time > 0:
        print(f"Time remaining: {total_time} seconds | Order Id {str(order_id)}")
        # Here we can put are login to calculate steps on basis of time
        time.sleep(1)
        total_time -= 1

    # Updating status on completion of order & mark driver as avaiable for next job
    update_status(db.drivers, ObjectId(driver_id), 'available_status', True)
    update_status(db.orders, order_id, 'status', 'completed')

    print(f"Order completed {str(order_id)}")

if __name__ == "__main__":
    main()
