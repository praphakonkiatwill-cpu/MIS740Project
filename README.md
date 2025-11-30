test
**built on original code:**
- kept path validation in main()
- adapted events_to_days() for availability entry
- reused employee_to_event() logic in create_schedule()
- your validation loops are solid, used them for inputs

**added CRUD stuff:**
- worker_management(): add/update/delete workers via pandas on employee.csv
- enter_availability(): additional column for avail times
- create_event_schedule(): auto-assigns by role + fairness (total_shifts)
- view_my_schedule(): reads assignments by ID
- generate_reports(): matplotlib charts + KPIs + export

**quick tweaks:**
- consolidated day copy/paste into for loop over DAYS_OF_WEEK
- fixed file write: df.to_csv() instead of open().write()
- added weekly_assignments.csv for schedule CRUD (via repository)

**Need to do**
- add fuzzy/lenient date input. right now it's too rigid in what date you put in
- add format hints inline to reduce errors
- add confirmation for delete or update actions
- add loading status for longer operations
- colors for errors?
- automatic default values
