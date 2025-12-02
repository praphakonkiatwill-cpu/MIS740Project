import random
from datetime import datetime, timedelta
import json

# Define lists of names, roles, and phone number prefixes
first_names = ["John", "Jane", "Bob", "Alice", "Tom", "Sarah", "Michael", "Emily", "David", "Ashley"]
last_names = ["Doe", "Smith", "Johnson", "Williams", "Brown", "Davis", "Wilson", "Anderson", "Taylor", "Martinez"]
roles = ["Security", "Usher", "Concessions", "Ticket Sales", "Event Coordinator"]
phone_prefixes = ["702", "206", "808", "312", "626"]

# Define function to generate worker data
def generate_worker_data(num_workers):
    workers = []
    for _ in range(num_workers):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        phone_prefix = random.choice(phone_prefixes)
        phone_number = f"{phone_prefix}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        contact = f"{phone_number}"
        worker_roles = random.sample(roles, random.randint(1, 3))
        availability = generate_availability()
        worker = {
            "name": name,
            "contact": contact,
            "roles": worker_roles,
            "availability": availability
        }
        workers.append(worker)
    return workers

# Define function to generate availability data
def generate_availability():
    availability = {}
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=7)
    current_date = start_date
    while current_date <= end_date:
        available_times = []
        if random.random() < 0.8:  # 80% chance of being available
            start_hour = random.randint(8, 17)
            end_hour = random.randint(start_hour + 2, 20)
            available_times.append(f"{start_hour:02d}:00-{end_hour:02d}:00")
        availability[str(current_date)] = available_times
        current_date += timedelta(days=1)
    return availability

# Generate and save mock data
num_workers = 50
workers = generate_worker_data(num_workers)

with open("workers.json", "w") as f:
    json.dump(workers, f, indent=4)

print(f"Generated {num_workers} workers and saved to workers.json.")
