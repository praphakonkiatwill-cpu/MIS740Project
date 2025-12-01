# IMPORT MODULES
import json
from datetime import datetime
import os

# GLOBAL DATA
workers = []
schedule = {}
DATA_FILE = "workers.json"
SCHEDULE_FILE = "schedule.json"


# LOAD WORKERS
def load_workers():
    global workers
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            workers = json.load(f)


# SAVE WORKERS
def save_workers():
    with open(DATA_FILE, "w") as f:
        json.dump(workers, f, indent=4)


# LOAD SCHEDULE
def load_schedule():
    global schedule
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r") as f:
            schedule = json.load(f)


# SAVE SCHEDULE
def save_schedule():
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=4)


# ADD WORKER
def add_worker():
    name = input("Enter name: ").strip()
    contact = input("Enter contact (phone/email): ").strip()
    roles = input("Enter roles (comma-separated): ").strip().split(",")
    roles = [r.strip() for r in roles if r.strip()]

    availability = {}
    while True:
        date = input("Enter available date (YYYY-MM-DD) or blank to finish: ").strip()
        if not date:
            break
        times = input("Enter available times (e.g. 08:00-16:00, 18:00-22:00): ").strip()
        availability[date] = [t.strip() for t in times.split(",") if t.strip()]

    worker = {
        "name": name,
        "contact": contact,
        "roles": roles,
        "availability": availability
    }
    workers.append(worker)
    save_workers()
    print("Worker added successfully.")


# UPDATE WORKER
def update_worker():
    view_workers()
    idx = int(input("Enter worker number to update: ")) - 1
    if 0 <= idx < len(workers):
        worker = workers[idx]
        print("Leave blank to keep current value.")
        name = input(f"Name [{worker['name']}]: ").strip()
        contact = input(f"Contact [{worker['contact']}]: ").strip()
        roles_input = input(f"Roles [{', '.join(worker['roles'])}]: ").strip()

        if name:
            worker["name"] = name
        if contact:
            worker["contact"] = contact
        if roles_input:
            worker["roles"] = [r.strip() for r in roles_input.split(",") if r.strip()]

        save_workers()
        print("Worker updated.")
    else:
        print("Invalid number.")


# DELETE WORKER
def delete_worker():
    view_workers()
    idx = int(input("Enter worker number to delete: ")) - 1
    if 0 <= idx < len(workers):
        removed = workers.pop(idx)
        save_workers()
        print(f"Deleted: {removed['name']}")
    else:
        print("Invalid number.")


# VIEW WORKERS
def view_workers():
    if not workers:
        print("No workers found.")
        return
    for i, w in enumerate(workers, 1):
        print(f"{i}. {w['name']} | {w['contact']} | Roles: {', '.join(w['roles'])}")


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
    global schedule
    schedule.clear()

    event_date = input("Event date (YYYY-MM-DD): ").strip()
    roles_needed = {}
    while True:
        role = input("Role needed (or blank to finish): ").strip()
        if not role:
            break
        count = int(input(f"How many {role}s needed? "))
        roles_needed[role] = count

    assigned = {}
    for role, needed in roles_needed.items():
        qualified = [w for w in workers if role in w["roles"] and event_date in w["availability"]]
        assigned[role] = []

        for _ in range(needed):
            if not qualified:
                print(f"Not enough {role}s available!")
                break
            print(f"\nAvailable for {role}:")
            for i, w in enumerate(qualified):
                times = ", ".join(w["availability"][event_date])
                print(f"{i + 1}. {w['name']} → {times}")

            choice = int(input("Select worker number: ")) - 1
            if 0 <= choice < len(qualified):
                selected = qualified.pop(choice)
                assigned[role].append({"name": selected["name"], "contact": selected["contact"]})
            else:
                print("Invalid choice.")

    schedule[event_date] = assigned
    save_schedule()
    print("Schedule created and saved.")


# VIEW SCHEDULE
def view_schedule():
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
                print(f"   • {person['name']} ({person['contact']})")
            if len(staff) < roles_needed.get(role, 0):
                print("   ⚠️  UNDERSTAFFED")


# Data Visualization Module
# This module provides reporting and analytics capabilities to support strategic decision-making by generating visual insights into staffing metrics. Key performance indicators (KPIs) include staff distribution by role, availability trends over time, and shift fairness across workers. These visualizations help managers identify coverage gaps, forecast staffing needs, and ensure equitable workloads, ultimately improving operational efficiency and employee satisfaction.

# Visual reports are generated using dedicated functions that leverage pandas for data aggregation and matplotlib for creating intuitive charts such as bar graphs and heatmaps. Data is loaded from centralized JSON or CSV files, processed with counters and accumulators to calculate totals and distributions, and presented in clear, graphical formats that highlight key insights. This addresses the lack of reporting in manual systems by enabling data-driven adjustments for future events.
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import os


# Load Data for Charts
# The system must load worker data from persistent storage to enable analysis without redundant data entry. This centralized approach eliminates disorganized information by reading from JSON or CSV files, ensuring all visualizations are based on up-to-date records.

# This can be implemented using pandas to convert file data into DataFrames or lists of dictionaries for efficient querying. Conditional logic determines the file format, and the function returns structured data ready for aggregation, reducing the risk of errors in downstream visualizations.
def load_workers_for_analysis():
    filename = "workers.json" if os.path.exists("workers.json") else "workers.csv"
    if filename.endswith(".json"):
        import json
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return pd.read_csv(filename).to_dict(orient="records")


# Chart 1 – Roles Distribution
# To monitor role coverage and identify potential shortages, the system should visualize the distribution of qualified workers across roles. This KPI helps managers forecast staffing needs and address recurring challenges in critical positions like security or concessions.

# This can be implemented by flattening role lists from worker profiles using loops, then applying counters to tally frequencies. The results are aggregated into a pandas-compatible structure and visualized as a bar chart with matplotlib, providing a clear format for quick insights into workforce composition.
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


# Chart 2 – Availability Heatmap (Next 7 Days)
# The system needs to track and visualize worker availability trends over upcoming days to prevent coverage gaps and operational breakdowns. This allows managers to proactively address shortages in advance, improving event reliability.

# Availability data is stored as nested dictionaries within worker profiles. Using loops and conditional checks, the system aggregates daily counts into a structure suitable for visualization. Matplotlib generates a bar-based heatmap, with accumulators tallying available workers per day for a data-driven view of short-term staffing forecasts.
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
# To promote shift fairness and monitor employee morale, the system should analyze and visualize assigned shifts per worker. This identifies imbalances, such as over-assignment, which can lead to lower satisfaction and higher turnover.

# Schedule data is loaded from a JSON file and processed using counters to tally shifts per worker. Aggregations calculate averages, and conditional logic highlights outliers. Matplotlib renders a bar chart for easy comparison, empowering managers to make equitable adjustments based on reliable data.
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
# Users should access analytics through a centralized menu for generating reports and visualizations on demand. This streamlines the process, eliminating manual calculations and ensuring timely insights.

# Implemented with a while loop for input handling and conditional statements to route to specific chart functions. This encapsulates the logic, reducing miscommunication and allowing managers to focus on data-driven decisions.
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


# MAIN MENU
def main_menu():
    load_workers()
    load_schedule()

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
        print("8. Analytics & Charts")
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
            view_schedule()
        elif choice == "8":
            analytics_menu()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


# RUN PROGRAM
if __name__ == "__main__":
    main_menu()
