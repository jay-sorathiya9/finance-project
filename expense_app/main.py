import csv
from database import (
    create_table,
    add_expense_db,
    get_all_expenses,
    filter_by_date_range,
    delete_expense_db,
    update_expense_db,
    set_budget_db,
    get_budgets_db,
    get_budget_for_category,
    add_category_db,
    get_categories_db,
    update_category_db
)

# ============================================================
# TABLE PRINT HELPER
# ============================================================
def print_table(data, headers):
    """
    Prints data in clean, aligned table form.
    """
    if not data:
        print("\nNo data.\n")
        return

    col_widths = {
        "id": 4,
        "date": 12,
        "category": 15,
        "amount": 10,
        "note": 25
    }

    header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
    print("\n" + header_line)
    print("-" * len(header_line))

    for row in data:
        line = " | ".join(str(row[h]).ljust(col_widths[h]) for h in headers)
        print(line)

    print()


# ============================================================
# ADD EXPENSE
# ============================================================
def add_expense():
    print("\n--- Add Expense ---")
    date = input("Enter date (YYYY-MM-DD): ")
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))
    note = input("Enter note: ")

    add_expense_db(date, category, amount, note)

    # Budget Check
    budget = get_budget_for_category(category)
    if budget:
        month = date[:7]
        total_spent = sum(
            e["amount"]
            for e in get_all_expenses()
            if e["category"] == category and e["date"][:7] == month
        )

        if total_spent > budget:
            print(f"\n⚠ WARNING: Budget exceeded for '{category}'!")
            print(f"Budget: {budget} | Spent: {total_spent}\n")

    print("Expense added successfully!\n")


# ============================================================
# VIEW EXPENSES
# ============================================================
def view_expenses():
    print("\n--- All Expenses ---")
    data = get_all_expenses()

    if not data:
        print("No expenses found.\n")
        return

    headers = ["id", "date", "category", "amount", "note"]
    print_table(data, headers)


# ============================================================
# SUMMARY
# ============================================================
def show_summary():
    print("\n--- Summary ---")
    data = get_all_expenses()

    if not data:
        print("No expenses found.\n")
        return

    total_spent = sum(item["amount"] for item in data)
    print(f"\nTotal Spent: {total_spent}")

    category_totals = {}
    for item in data:
        category = item["category"]
        category_totals[category] = category_totals.get(category, 0) + item["amount"]

    print("\nCategory-wise totals:")
    for category, amount in category_totals.items():
        print(f"  {category}: {amount}")
    print()


# ============================================================
# MONTHLY SUMMARY
# ============================================================
def monthly_summary():
    print("\n--- Monthly Summary ---")
    data = get_all_expenses()

    if not data:
        print("No expenses found.\n")
        return

    monthly_totals = {}
    category_monthly = {}

    for row in data:
        month = row["date"][:7]
        amount = row["amount"]
        category = row["category"]

        monthly_totals[month] = monthly_totals.get(month, 0) + amount

        if month not in category_monthly:
            category_monthly[month] = {}

        category_monthly[month][category] = category_monthly[month].get(category, 0) + amount

    for month in sorted(monthly_totals.keys()):
        print(f"\n{month}")
        print("-" * len(month))
        print(f"Total: {monthly_totals[month]}")
        print("Category breakdown:")

        for category, amount in category_monthly[month].items():
            print(f"  {category}: {amount}")

    print()


# ============================================================
# SEARCH EXPENSES
# ============================================================
def search_expenses():
    print("\n--- Search Expenses ---")
    query = input("Enter keyword: ").lower()

    results = [
        row for row in get_all_expenses()
        if query in row["date"].lower()
        or query in row["category"].lower()
        or query in str(row["amount"]).lower()
        or query in (row["note"] or "").lower()
    ]

    if not results:
        print("No matching expenses found.\n")
        return

    headers = ["id", "date", "category", "amount", "note"]
    print_table(results, headers)


# ============================================================
# FILTER EXPENSES
# ============================================================
def filter_expenses():
    print("\n--- Filter Expenses ---")
    print("1. Filter by Date")
    print("2. Filter by Category")
    print("3. Filter by Date Range")
    print("4. Export ALL Expenses to CSV")

    choice = input("Choose option: ")
    data = get_all_expenses()
    results = []

    if choice == "1":
        date = input("Enter date: ")
        results = [row for row in data if row["date"] == date]

    elif choice == "2":
        category = input("Enter category: ").lower()
        results = [row for row in data if row["category"].lower() == category]

    elif choice == "3":
        start = input("Start date: ")
        end = input("End date: ")
        results = filter_by_date_range(start, end)

    elif choice == "4":
        filename = input("CSV filename: ")
        export_to_csv(filename, data)
        print("Export complete.\n")
        return

    else:
        print("Invalid option.\n")
        return

    if not results:
        print("No results.\n")
        return

    headers = ["id", "date", "category", "amount", "note"]
    print_table(results, headers)


# ============================================================
# DELETE EXPENSE
# ============================================================
def delete_expense():
    print("\n--- Delete Expense ---")
    data = get_all_expenses()

    if not data:
        print("No expenses.\n")
        return

    print_table(data, ["id", "date", "category", "amount", "note"])

    delete_id = int(input("Enter ID to delete: "))
    delete_expense_db(delete_id)

    print("Deleted.\n")


# ============================================================
# EDIT EXPENSE
# ============================================================
def edit_expense():
    print("\n--- Edit Expense ---")
    data = get_all_expenses()

    if not data:
        print("No expenses.\n")
        return

    print_table(data, ["id", "date", "category", "amount", "note"])

    edit_id = int(input("Enter ID: "))
    target = next((r for r in data if r["id"] == edit_id), None)

    if not target:
        print("Invalid ID.\n")
        return

    print("Leave blank to keep old value.")

    new_date = input(f"Date ({target['date']}): ") or target["date"]
    new_category = input(f"Category ({target['category']}): ") or target["category"]
    amount_input = input(f"Amount ({target['amount']}): ")
    new_amount = float(amount_input) if amount_input.strip() else target["amount"]
    new_note = input(f"Note ({target['note']}): ") or target["note"]

    update_expense_db(edit_id, new_date, new_category, new_amount, new_note)
    print("Updated.\n")


# ============================================================
# EXPORT CSV
# ============================================================
def export_to_csv(filename, data):
    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "date", "category", "amount", "note"])
        for r in data:
            w.writerow([r["id"], r["date"], r["category"], r["amount"], r["note"]])


def export_csv():
    filename = input("Enter filename (backup.csv): ")
    export_to_csv(filename, get_all_expenses())
    print("Export complete.\n")


# ============================================================
# CATEGORY MANAGER
# ============================================================
def category_manager():
    while True:
        print("\n--- Category Manager ---")
        print("1. View Categories")
        print("2. Add Category")
        print("3. Edit Category")
        print("4. Delete Category")
        print("5. Back")

        choice = input("Choose: ")

        if choice == "1":
            categories = get_categories_db()
            if not categories:
                print("No categories.\n")
                continue
            for c in categories:
                print(f"{c['id']}. {c['name']}")
            print()

        elif choice == "2":
            name = input("Category name: ").strip()
            if name:
                add_category_db(name)
                print("Added.\n")

        elif choice == "3":
            categories = get_categories_db()
            for c in categories:
                print(f"{c['id']}. {c['name']}")

            cid = int(input("Enter ID: "))
            new_name = input("New name: ").strip()
            update_category_db(cid, new_name)
            print("Updated.\n")

        elif choice == "4":
            categories = get_categories_db()
            for c in categories:
                print(f"{c['id']}. {c['name']}")

            cid = int(input("Enter ID: "))
            conn = __import__("sqlite3").connect("expenses.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM categories WHERE id = ?", (cid,))
            conn.commit()
            conn.close()

            print("Deleted.\n")

        elif choice == "5":
            break


# ============================================================
# BUDGET MANAGER
# ============================================================
def budget_manager():
    while True:
        print("\n--- Budget Manager ---")
        print("1. View Budgets")
        print("2. Set/Update Budget")
        print("3. Back")

        choice = input("Choose: ")

        if choice == "1":
            budgets = get_budgets_db()
            if not budgets:
                print("No budgets.\n")
            else:
                for b in budgets:
                    print(f"{b['category']}: {b['amount']}")
            print()

        elif choice == "2":
            category = input("Category: ")
            amount = float(input("Amount: "))
            set_budget_db(category, amount)
            print("Budget updated.\n")

        elif choice == "3":
            break


# ============================================================
# MENU & MAIN LOOP
# ============================================================
def show_menu():
    print("===== ADVANCED EXPENSE TRACKER =====")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Summary")
    print("4. Filter Expenses")
    print("5. Monthly Summary")
    print("6. Search Expenses")
    print("7. Edit Expense")
    print("8. Delete Expense")
    print("9. Export to CSV")
    print("10. Category Manager")
    print("11. Budget Manager")
    print("12. Exit")


def main():
    create_table()

    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == "1": add_expense()
        elif choice == "2": view_expenses()
        elif choice == "3": show_summary()
        elif choice == "4": filter_expenses()
        elif choice == "5": monthly_summary()
        elif choice == "6": search_expenses()
        elif choice == "7": edit_expense()
        elif choice == "8": delete_expense()
        elif choice == "9": export_csv()
        elif choice == "10": category_manager()
        elif choice == "11": budget_manager()
        elif choice == "12":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
