# IMPORT MODULES
import json
from datetime import datetime, timedelta
import os
import random
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

# GLOBAL DATA
workers = []
schedule = {}
DATA_FILE = "workers.json"
SCHEDULE_FILE = "schedule.json"
MANAGER_PASSWORD = "UNLV"

# LOAD WORKERS
def load_workers():
    global workers
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                workers = json.load(f)
        except json.JSONDecodeError:
            # Handle the case where the file is empty or invalid
            workers = []
    else:
        # Handle the case where the file doesn't exist
        workers = []

# SAVE WORKERS
def save_workers():
    with open(DATA_FILE, "w") as f:
        json.dump(workers, f, indent=4)

# LOAD SCHEDULE
def load_schedule():
    global schedule
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r") as f:
                schedule = json.load(f)
        except json.JSONDecodeError:
            # Handle the case where the file is empty or invalid
            schedule = {}
    else:
        # Handle the case where the file doesn't exist
        schedule = {}

# SAVE SCHEDULE
def save_schedule():
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=4)

# ADD WORKER
def add_worker():
    worker = {
        "name": input("Enter name: ").strip(),
        "contact": f"{random.choice(['***', '***', '***', '***', '***'])}-{random.randint(1000, 9999)}",
        "roles": [r.strip() for r in input("Enter roles (comma-separated): ").strip().split(",") if r.strip()],
        "availability": generate_availability()
    }
    workers.append(worker)
    save_workers()
    print("Worker added successfully.")

# UPDATE WORKER
def update_worker():
    password = input("Enter manager password: ")
    if password != MANAGER_PASSWORD:
        print("Incorrect password. Access denied.")
        return

    view_workers()
    idx = input("Enter worker number to update: ").strip()
    if idx:
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(workers):
                worker = workers[idx]
                print("Leave blank to keep current value.")
                worker["name"] = input(f"Name [{worker['name']}]: ").strip() or worker["name"]
                worker["contact"] = f"{random.choice(['***', '***', '***', '***', '***'])}-{random.randint(1000, 9999)}"
                roles_input = input(f"Roles [{', '.join(worker['roles'])}]: ").strip()
                if roles_input:
                    worker["roles"] = [r.strip() for r in roles_input.split(",") if r.strip()]

                save_workers()
                print("Worker updated.")
            else:
                print("Invalid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    else:
        print("No worker selected.")

# DELETE WORKER
def delete_worker():
    password = input("Enter manager password: ")
    if password != MANAGER_PASSWORD:
        print("Incorrect password. Access denied.")
        return

    view_workers()
    idx = input("Enter worker number to delete: ").strip()
    if idx:
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(workers):
                removed = workers.pop(idx)
                save_workers()
                print(f"Deleted: {removed['name']}")
            else:
                print("Invalid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    else:
        print("No worker selected.")

# VIEW WORKERS
def view_workers():
    if not workers:
        print("No workers found.")
        return
    for i, worker in enumerate(workers, 1):
        print(f"{i}. {worker['name']} | {worker['contact']} | Roles: {', '.join(worker['roles'])}")

# VIEW AVAILABILITY
def view_availability():
    date = input("Enter date (YYYY-MM-DD): ").strip()
    available = [w for w in workers if date in w["availability"] and w["availability"][date]]
    if not available:
        print("No one available on this date.")
        return
    print(f"Available on {date}:")
    for w in available:
        times = ", ".join(w["availability"][date])
        print(f"  - {w['name']} ({', '.join(w['roles'])}) → {times}")

# CREATE SCHEDULE
def create_schedule():
    global schedule, roles_needed
    schedule.clear()
    roles_needed = {}

    event_date = input("Event date (YYYY-MM-DD): ").strip()
    while True:
        role = input("Role needed (or blank to finish): ").strip()
        if not role:
            break
        count = int(input(f"How many {role}s needed? "))
        roles_needed[role] = count

    assigned = {}
    for role, needed in roles_needed.items():
        qualified = []
        for worker in workers:
            if role in worker["roles"] and event_date in worker["availability"]:
                qualified.append({"name": worker["name"], "contact": worker["contact"], "availability": worker["availability"][event_date]})

        for _ in range(needed):
            if not qualified:
                print(f"Not enough {role}s available!")
                break
            print(f"\nAvailable for {role}:")
            for i, w in enumerate(qualified, 1):
                print(f"{i}. {w['name']} → {', '.join(w['availability'])}")

            choice = input("Select worker number: ").strip()
            if choice:
                try:
                    choice = int(choice) - 1
                    if 0 <= choice < len(qualified):
                        selected = qualified.pop(choice)
                        assigned[role] = assigned.get(role, []) + [{"name": selected["name"], "contact": selected["contact"]}]
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

    schedule[event_date] = assigned
    save_schedule()
    print("Schedule created and saved.")

# VIEW SCHEDULE
def view_schedule(roles_needed):
    load_schedule()
    if not schedule:
        print("No schedule found.")
        return

    for date, roles in schedule.items():
        print(f"\nSCHEDULE FOR {date}")
        print("-" * 50)
        for role, staff in roles.items():
            print(f"{role.upper()}:")
            for person in staff:
                # Find the worker's availability for the scheduled date
                worker = next((w for w in workers if w['name'] == person['name']), None)
                if worker and date in worker['availability']:
                    availability_times = ', '.join(worker['availability'][date])
                    print(f"   • {person['name']} ({person['contact']}) → {availability_times}")
                else:
                    print(f"   • {person['name']} ({person['contact']})")
            if len(staff) < roles_needed.get(role, 0):
                print("   ⚠️  UNDERSTAFFED")

# Generate availability data
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

# MAIN MENU
def main_menu():
    load_workers()
    load_schedule()
    roles_needed = {}

    while True:
        print("\n" + "=" * 40)
        print("   STAFF SCHEDULING MANAGER")
        print("=" * 40)
        print("1. Add Worker")
        print("2. Update Worker")
        print("3. Delete Worker")
        print("4. View All Workers")
        print("5. Check Availability")
        print("6. Create Schedule")
        print("7. View Schedule")
        print("8. Data Analysis")
        print("0. Exit")
        choice = input("\nSelect option: ").strip()

        if choice == "1":
            add_worker()
        elif choice == "2":
            update_worker()
        elif choice == "3":
            delete_worker()
        elif choice == "4":
            view_workers()
        elif choice == "5":
            view_availability()
        elif choice == "6":
            create_schedule()
        elif choice == "7":
            view_schedule(roles_needed)
        elif choice == "8":
            analytics_menu()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

# Data Visualization Modules

# Load Data for Charts
def load_workers_for_analysis():
    filename = "workers.json" if os.path.exists("workers.json") else "workers.csv"
    if filename.endswith(".json"):
        import json
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return pd.read_csv(filename).to_dict(orient="records")

# Chart 1 – Roles Distribution
def plot_role_distribution():
    workers = load_workers_for_analysis()
    all_roles = []
    for w in workers:
        roles = w.get("roles", [])
        if isinstance(roles, str):
            roles = [r.strip() for r in roles.split(",")]
        all_roles.extend(roles)

    role_counts = Counter(all_roles)
    roles, counts = zip(*role_counts.most_common())

    plt.figure(figsize=(10, 6))
    plt.bar(roles, counts, color="#4e79a7")
    plt.title("Staff Distribution by Role", fontsize=16, fontweight="bold")
    plt.xlabel("Role")
    plt.ylabel("Number of Qualified Workers")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

# Chart 2 – Availability Heatmap next 7 dys
def plot_availability_heatmap():
    workers = load_workers_for_analysis()
    from datetime import datetime, timedelta
    today = datetime.today().date()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    heatmap = {date: 0 for date in dates}
    for worker in workers:
        avail = worker.get("availability", {})
        for date in dates:
            if date in avail and avail[date]:
                heatmap[date] += 1

    days = [d[5:] for d in dates]
    counts = list(heatmap.values())

    plt.figure(figsize=(9, 5))
    plt.bar(days, counts, color="#f28e2b")
    plt.title("Total Workers Available (Next 7 Days)", fontsize=16, fontweight="bold")
    plt.xlabel("Date (MM-DD)")
    plt.ylabel("Available Workers")
    plt.ylim(0, max(counts) * 1.2 if counts else 10)
    for i, v in enumerate(counts):
        plt.text(i, v + max(counts) * 0.02, str(v), ha="center", fontweight="bold")
    plt.tight_layout()
    plt.show()

# Chart 3 – Shifts per Worker (Fairness Check)
def plot_shifts_per_worker():
    schedule_file = "schedule.json"
    if not os.path.exists(schedule_file):
        print("No schedule file found – generate a schedule first.")
        return

    import json
    with open(schedule_file, "r") as f:
        schedule = json.load(f)

    worker_shift_count = Counter()
    for role, assignments in schedule.items():
        for assignment in assignments:
            worker_shift_count[assignment["name"]] += 1

    if not worker_shift_count:
        print("Schedule is empty.")
        return

    names, shifts = zip(*worker_shift_count.most_common())

    plt.figure(figsize=(11, 6))
    bars = plt.bar(names, shifts, color="#76b7b2")
    plt.title("Number of Assigned Shifts per Worker", fontsize=16, fontweight="bold")
    plt.xlabel("Worker")
    plt.ylabel("Shifts Assigned")
    plt.xticks(rotation=60, ha="right")

    avg = sum(shifts) / len(shifts)
    for bar, s in zip(bars, shifts):
        if s > avg + 2:
            bar.set_color("#e15759")

    plt.tight_layout()
    plt.show()

# Master Analytics Menu
def analytics_menu():
    while True:
        print("\n" + "=" * 40)
        print("       ANALYTICS & VISUALIZATION")
        print("=" * 40)
        print("1. Role Distribution Bar Chart")
        print("2. 7-Day Availability Heatmap")
        print("3. Shifts per Worker (Fairness)")
        print("0. Back to Main Menu")
        choice = input("Choose report » ").strip()

        if choice == "1":
            plot_role_distribution()
        elif choice == "2":
            plot_availability_heatmap()
        elif choice == "3":
            plot_shifts_per_worker()
        elif choice == "0":
            break
        else:
            print("Invalid option – try again.")

# run
if __name__ == "__main__":
    main_menu()
