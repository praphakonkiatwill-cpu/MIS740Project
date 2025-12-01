import csv
import random
from datetime import datetime, timedelta

# Define lists of sample data
names = ["John Doe", "Jane Smith", "Michael Johnson", "Emily Brown", "David Lee", "Sarah Thompson", "Christopher Davis",
         "Olivia Wilson", "Daniel Taylor", "Sophia Anderson"]
roles = ["Security", "Usher", "Concessions", "Ticket Sales", "Event Coordinator"]
phone_prefixes = ["702", "206", "808", "312", "626",]
email_domains = ["unlv.com", "company.org", "service.net", "enterprise.co"]

# Generate 50 employees
num_employees = 50
employees = []

for i in range(num_employees):
    name = random.choice(names)
    role_count = random.randint(1, 3)
    worker_roles = random.sample(roles, role_count)
    phone = f"{random.choice(phone_prefixes)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    email = f"{name.lower().replace(' ', '.')}@{random.choice(email_domains)}"

    # Generate availability
    availability = {}
    start_date = datetime.now().date() - timedelta(days=random.randint(0, 30))
    end_date = start_date + timedelta(days=random.randint(30, 90))
    current_date = start_date
    while current_date <= end_date:
        if random.random() < 0.7:  # 70% chance of being available on a given day
            start_time = f"{random.randint(8, 20)}:{random.choice(['00', '15', '30', '45'])}"
            end_time = f"{random.randint(12, 22)}:{random.choice(['00', '15', '30', '45'])}"
            availability[current_date.strftime("%Y-%m-%d")] = [f"{start_time}-{end_time}"]
        current_date += timedelta(days=1)

    employee = {
        "ID": f"E{i + 1}",
        "name": name,
        "phone": phone,
        "email": email,
        "roles": ",".join(worker_roles),
        "total_shifts": random.randint(0, 50),
        "availability": str(availability)
    }
    employees.append(employee)

# Write the data to a CSV file
with open("employee.csv", "w", newline="") as csvfile:
    fieldnames = ["ID", "name", "phone", "email", "roles", "total_shifts", "availability"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for employee in employees:
        writer.writerow(employee)

print("CSV file 'employee_data.csv' generated successfully.")
