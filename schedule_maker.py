import os
import pandas as pd
import matplotlib.pyplot as plt
import json
from schedule_repository import (load_employee_df, create_assignment,
                                 list_assignments_for_employee_week,
                                 build_and_save_weekly_schedule)

# create reports dir
os.makedirs('reports', exist_ok=True)


# get validated input
def get_validated_input(prompt, validation_func, error_message):
    while True:
        user_input = input(prompt).strip()
        if validation_func(user_input):
            return user_input
        print(error_message)


# manage workers
def worker_management():
    employees = load_employee_df()
    while True:
        print("\n=== WORKER MANAGEMENT ===")
        print("1. Add Worker | 2. Update Worker | 3. Delete Worker | 4. View All | 5. Back")
        choice = input("Choice: ").strip()
        if choice == '1':
            name = input("Name: ").strip()
            phone = input("Phone: ").strip()
            email = input("Email: ").strip()
            roles = input("Roles (comma sep: security,usher): ").strip()
            new_row = pd.DataFrame({'ID': [str(len(employees) + 1)], 'name': [name], 'phone': [phone],
                                    'email': [email], 'roles': [roles], 'total_shifts': [0],
                                    'availability': ['{}']})
            employees = pd.concat([employees.reset_index(drop=True), new_row], ignore_index=True)
            employees.to_csv('employee.csv')
            print("Added!")
        elif choice == '2':
            id_ = input("ID: ").strip()
            if id_ in employees.index:
                field = input("Field (name/phone/email/roles/total_shifts/availability): ").strip()
                new_val = input("New value: ").strip()
                if field == 'availability':
                    new_val = json.dumps(json.loads(new_val)) if new_val else '{}'
                employees.loc[id_, field] = new_val
                employees.to_csv('employee.csv')
                print("Updated!")
            else:
                print("ID not found.")
        elif choice == '3':
            id_ = input("ID: ").strip()
            confirm = input(f"Delete {id_}? (y/n): ").strip().lower()
            if confirm == 'y' and id_ in employees.index:
                employees = employees.drop(id_)
                employees.to_csv('employee.csv')
                print("Deleted!")
            else:
                print("Cancelled.")
        elif choice == '4':
            print(employees)
        elif choice == '5':
            break


# enter worker availability
def enter_availability():
    employees = load_employee_df()
    id_ = get_validated_input("Worker ID: ", lambda x: x in employees.index, "Invalid ID.")
    avail = json.loads(employees.loc[id_, 'availability'])
    date_ = input("Date (YYYY-MM-DD): ").strip()
    time_ = input("Time (e.g., 18:00): ").strip()
    available = input("Available? (y/n): ").strip().lower() == 'y'
    if date_ not in avail:
        avail[date_] = {}
    avail[date_][time_] = available
    employees.loc[id_, 'availability'] = json.dumps(avail)
    employees.to_csv('employee.csv')
    print("Availability updated!")


# create event schedule
def create_event_schedule():
    event_name = input("Event Name: ").strip()
    week_ending = input("Week Ending (YYYY-MM-DD): ").strip()
    day = input("Day (Monday-Sunday): ").strip()
    requirements = {}
    roles_needed = input("Roles needed (e.g., security:8,ushers:12): ").strip()
    for pair in roles_needed.split(','):
        role, num = pair.split(':')
        requirements[role.strip()] = int(num.strip())

    employees = load_employee_df()
    for role, needed in requirements.items():
        role_mask = employees['roles'].str.contains(role, na=False)
        avail_mask = employees.apply(
            lambda row: json.loads(row['availability']).get(week_ending, {}).get('18:00', False), axis=1)
        available = employees[role_mask & avail_mask].sort_values('total_shifts')
        for _, worker in available.head(needed).iterrows():
            create_assignment(week_ending, worker.name, day, f"{event_name} - {role}", "18:00", "20:00")
            employees.loc[worker.name, 'total_shifts'] += 1
    employees.to_csv('employee.csv')
    print("Schedule created!")


# view worker schedule
def view_my_schedule():
    id_ = input("Worker ID: ").strip()
    week_ending = input("Week Ending (YYYY-MM-DD): ").strip()
    assignments = list_assignments_for_employee_week(week_ending, id_)
    if not assignments.empty:
        for _, row in assignments.iterrows():
            print(f"{row['DayOfWeek']}: {row['EventName']} ({row['StartTime']}-{row['EndTime']})")
    else:
        print("No assignments.")


# generate reports
def generate_reports():
    employees = load_employee_df()
    week_ending = input("Week Ending (YYYY-MM-DD): ").strip()

    plt.figure(figsize=(12, 6))
    plt.bar(employees.index, employees['total_shifts'])
    plt.title('Shift Distribution')
    plt.xlabel('Worker ID')
    plt.ylabel('Total Shifts')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('reports/shift_distribution.png')
    plt.show()

    total_shifts = employees['total_shifts'].sum()
    avg_shifts = employees['total_shifts'].mean()
    labor_cost = total_shifts * 23
    print(f"Total Shifts: {total_shifts} | Avg: {avg_shifts:.1f} | Labor Cost: ${labor_cost:,.0f}")

    path = build_and_save_weekly_schedule(week_ending)
    print(f"Schedule exported: {path}")


# main menu loop
def main():
    while True:
        print("\n=== STAFF SCHEDULING MANAGER ===")
        print("1. Worker Management | 2. Enter Availability | 3. Create Event Schedule")
        print("4. View My Schedule | 5. Generate Reports | 6. Exit")
        choice = input("Choice: ").strip()
        if choice == '1':
            worker_management()
        elif choice == '2':
            enter_availability()
        elif choice == '3':
            create_event_schedule()
        elif choice == '4':
            view_my_schedule()
        elif choice == '5':
            generate_reports()
        elif choice == '6':
            break
        else:
            print("Invalid choice.")


# run main
if __name__ == "__main__":
    main()