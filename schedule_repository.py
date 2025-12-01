from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# list of days
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# define assignment class
@dataclass(frozen=True)
class Assignment:
    assignment_id: str
    week_ending: date
    employee_id: str
    day_of_week: str
    event_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    notes: Optional[str] = None


# parse week ending date
def _parse_week_ending(week_ending: str | date) -> date:
    if isinstance(week_ending, date):
        return week_ending

    s = str(week_ending).strip().lower()

    if s in {"", "today"}:
        return date.today()

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        f"Could not parse week_ending '{week_ending}'. "
        "Use 'YYYY-MM-DD' or 'MM/DD/YYYY', or type 'today'."
    )


# create parent dir if missing
def _ensure_parent_dir(path: Path) -> None:
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


# load employee data from csv
def load_employee_df(path: str | os.PathLike = "employee.csv") -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"employee.csv not found at: {path.resolve()}")

    df = pd.read_csv(path, dtype={"ID": str})
    if "ID" not in df.columns:
        raise ValueError("employee.csv must contain an 'ID' column.")

    df = df.set_index("ID")
    df.index = df.index.astype(str)
    return df


# list assignment columns
ASSIGNMENT_COLUMNS = [
    "AssignmentID",
    "WeekEndingSunday",
    "EmployeeID",
    "DayOfWeek",
    "EventName",
    "StartTime",
    "EndTime",
    "Notes",
]


# load assignments from csv
def load_assignments_df(
        path: str | os.PathLike = "weekly_assignments.csv",
        create_if_missing: bool = True,
) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        if not create_if_missing:
            raise FileNotFoundError(f"weekly_assignments.csv not found at: {path.resolve()}")
        df = pd.DataFrame(columns=ASSIGNMENT_COLUMNS)
        return df

    df = pd.read_csv(path, dtype={"EmployeeID": str, "AssignmentID": str})

    for col in ASSIGNMENT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["WeekEndingSunday"] = pd.to_datetime(df["WeekEndingSunday"]).dt.date
    df["EmployeeID"] = df["EmployeeID"].astype(str)
    df["AssignmentID"] = df["AssignmentID"].astype(str)

    return df[ASSIGNMENT_COLUMNS]


# write assignments to csv
def _write_assignments_df(df: pd.DataFrame, path: str | os.PathLike = "weekly_assignments.csv") -> None:
    path = Path(path)
    _ensure_parent_dir(path)

    temp_path = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(temp_path, index=False, lineterminator="\n")
    temp_path.replace(path)


# generate new assignment id
def _generate_new_assignment_id(existing_ids: Iterable[str]) -> str:
    max_num = 0
    for raw in existing_ids:
        if not raw:
            continue
        s = str(raw)
        if s.startswith("A"):
            try:
                n = int(s[1:])
                max_num = max(max_num, n)
            except ValueError:
                continue

    new_num = max_num + 1
    return f"A{new_num:04d}"


# create new assignment
def create_assignment(
        week_ending: str | date,
        employee_id: str,
        day_of_week: str,
        event_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        notes: Optional[str] = None,
        assignments_csv: str | os.PathLike = "weekly_assignments.csv",
) -> Assignment:
    week_date = _parse_week_ending(week_ending)
    day_of_week = str(day_of_week).strip()

    if day_of_week not in DAYS_OF_WEEK:
        raise ValueError(f"Invalid DayOfWeek '{day_of_week}'. Must be one of {DAYS_OF_WEEK}.")

    df = load_assignments_df(assignments_csv, create_if_missing=True)
    new_id = _generate_new_assignment_id(df["AssignmentID"].tolist())

    new_row = {
        "AssignmentID": new_id,
        "WeekEndingSunday": week_date,
        "EmployeeID": str(employee_id),
        "DayOfWeek": day_of_week,
        "EventName": event_name.strip(),
        "StartTime": (start_time or "").strip(),
        "EndTime": (end_time or "").strip(),
        "Notes": (notes or "").strip(),
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    _write_assignments_df(df, assignments_csv)

    return Assignment(
        assignment_id=new_id,
        week_ending=week_date,
        employee_id=str(employee_id),
        day_of_week=day_of_week,
        event_name=event_name.strip(),
        start_time=(start_time or "").strip() or None,
        end_time=(end_time or "").strip() or None,
        notes=(notes or "").strip() or None,
    )


# list assignments for week
def list_assignments_for_week(
        week_ending: str | date,
        assignments_csv: str | os.PathLike = "weekly_assignments.csv",
) -> pd.DataFrame:
    week_date = _parse_week_ending(week_ending)
    df = load_assignments_df(assignments_csv, create_if_missing=True)
    return df[df["WeekEndingSunday"] == week_date].copy()


# list assignments for employee in week
def list_assignments_for_employee_week(
        week_ending: str | date,
        employee_id: str,
        assignments_csv: str | os.PathLike = "weekly_assignments.csv",
) -> pd.DataFrame:
    week_date = _parse_week_ending(week_ending)
    df = load_assignments_df(assignments_csv, create_if_missing=True)
    mask = (df["WeekEndingSunday"] == week_date) & (df["EmployeeID"] == str(employee_id))
    return df[mask].copy()


# update existing assignment
def update_assignment(
        assignment_id: str,
        *,
        event_name: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        notes: Optional[str] = None,
        day_of_week: Optional[str] = None,
        assignments_csv: str | os.PathLike = "weekly_assignments.csv",
) -> None:
    df = load_assignments_df(assignments_csv, create_if_missing=True)

    mask = df["AssignmentID"] == str(assignment_id)
    if not mask.any():
        raise ValueError(f"No assignment found with AssignmentID={assignment_id}")

    if day_of_week is not None:
        day_of_week = day_of_week.strip()
        if day_of_week not in DAYS_OF_WEEK:
            raise ValueError(f"Invalid DayOfWeek '{day_of_week}'. Must be one of {DAYS_OF_WEEK}.")
        df.loc[mask, "DayOfWeek"] = day_of_week

    if event_name is not None:
        df.loc[mask, "EventName"] = event_name.strip()

    if start_time is not None:
        df.loc[mask, "StartTime"] = start_time.strip()

    if end_time is not None:
        df.loc[mask, "EndTime"] = end_time.strip()

    if notes is not None:
        df.loc[mask, "Notes"] = notes.strip()

    _write_assignments_df(df, assignments_csv)


# delete assignment by id
def delete_assignment(
        assignment_id: str,
        assignments_csv: str | os.PathLike = "weekly_assignments.csv",
) -> None:
    df = load_assignments_df(assignments_csv, create_if_missing=True)

    mask = df["AssignmentID"] != str(assignment_id)
    if mask.all():
        raise ValueError(f"No assignment found with AssignmentID={assignment_id}")

    df = df[mask]
    _write_assignments_df(df, assignments_csv)


# build weekly schedule df
def build_weekly_schedule_from_assignments(
        week_ending: str | date,
        employee_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
) -> pd.DataFrame:
    week_date = _parse_week_ending(week_ending)

    week_assignments = assignments_df[assignments_df["WeekEndingSunday"] == week_date]

    schedule_df = employee_df.copy()

    schedule_map: dict[str, dict[str, str]] = {day: {} for day in DAYS_OF_WEEK}

    for _, row in week_assignments.iterrows():
        day = str(row["DayOfWeek"])
        if day not in DAYS_OF_WEEK:
            continue

        emp_id = str(row["EmployeeID"])

        event_name = row.get("EventName") or ""
        start_time = row.get("StartTime") or ""

        label_parts = []
        if event_name.strip():
            label_parts.append(event_name.strip())
        if start_time.strip():
            label_parts.append(start_time.strip())

        label = ": ".join(label_parts) if label_parts else ""

        if label:
            schedule_map[day][emp_id] = label

    for day in DAYS_OF_WEEK:
        day_series = pd.Series(schedule_map[day], name=day)
        day_series = day_series.reindex(schedule_df.index, fill_value="Off")
        schedule_df[day] = day_series

    day_columns = [col for col in DAYS_OF_WEEK if col in schedule_df.columns]
    other_columns = [col for col in schedule_df.columns if col not in DAYS_OF_WEEK]
    schedule_df = schedule_df[day_columns + other_columns]

    return schedule_df


# save schedule to csv
def save_weekly_schedule_csv(
        schedule_df: pd.DataFrame,
        week_ending: str | date,
        output_dir: str | os.PathLike = ".",
) -> Path:
    week_date = _parse_week_ending(week_ending)

    month = week_date.month
    day = week_date.day
    year = week_date.year

    filename = f"{month}_{day}_{year}_Week_Ending_Schedule.csv"
    output_path = Path(output_dir) / filename

    _ensure_parent_dir(output_path)
    schedule_df.to_csv(output_path, lineterminator="\n")

    return output_path


# build and save schedule
def build_and_save_weekly_schedule(
        week_ending: str | date,
        employee_csv: str | os.PathLike = "employee.csv",
        assignments_csv: str | os.PathLike = "weekly_assignments.csv",
        output_dir: str | os.PathLike = ".",
) -> Path:
    employees = load_employee_df(employee_csv)
    assignments = load_assignments_df(assignments_csv, create_if_missing=True)
    schedule_df = build_weekly_schedule_from_assignments(week_ending, employees, assignments)
    return save_weekly_schedule_csv(schedule_df, week_ending, output_dir=output_dir)


# main for testing
if __name__ == "__main__":
    print("=" * 60)
    print("CSV SCHEDULE REPOSITORY (CRUD + EXPORT)")
    print("=" * 60)
    week_str = input("Enter week-ending Sunday (YYYY-MM-DD): ").strip()

    try:
        path = build_and_save_weekly_schedule(week_str)
        print(f"\n{GREEN}✓ Schedule exported to: {path.resolve()}{RESET}")
    except Exception as exc:
        print(f"\n{RED}✗ Error: {exc}{RESET}")
