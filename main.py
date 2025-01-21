import sqlite3
from datetime import datetime

# Database setup and initialization
def initialize_database():
    """Initialize the database tables and add default categories."""
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        
        # Create categories table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """)
        
        # Create expenses table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category_id INTEGER,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
        """)
        
        # Insert default categories if they don't exist
        categories = ["Food", "Transport", "Entertainment", "Utilities"]
        for category in categories:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        
        conn.commit()

# Connect to the SQLite database
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

def display_menu():
    """Display the main menu options."""
    print("\n=== Expense Management System ===")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. View Expenses by Category")
    print("4. Monthly Expense Summary")
    print("5. Add New Category")
    print("6. Exit")

def add_expense():
    """Add a new expense record to the database."""
    try:
        amount = float(input("Enter the expense amount: "))
        
        # List available categories
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        print("Available Categories:")
        for category in categories:
            print(f"{category[0]}. {category[1]}")

        category_id = int(input("Enter the category ID: "))
        
        # Validate category_id
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if cursor.fetchone() is None:
            print("Invalid category ID. Please try again.")
            return

        date = input("Enter the date (YYYY-MM-DD) [default: today]: ")
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        description = input("Enter a description (optional): ")

        # Insert the expense into the database
        cursor.execute("""
        INSERT INTO expenses (amount, category_id, date, description)
        VALUES (?, ?, ?, ?)
        """, (amount, category_id, date, description))
        conn.commit()

        print("Expense added successfully!")
    except Exception as e:
        print(f"Error: {e}")

def view_all_expenses():
    """Display all recorded expenses."""
    cursor.execute("""
    SELECT e.id, e.amount, c.name, e.date, e.description 
    FROM expenses e
    JOIN categories c ON e.category_id = c.id
    ORDER BY e.date DESC
    """)
    expenses = cursor.fetchall()
    if not expenses:
        print("No expenses recorded yet.")
        return

    print("\nAll Expenses:")
    print("ID | Amount | Category       | Date       | Description")
    print("-" * 50)
    for expense in expenses:
        print(f"{expense[0]:<2} | {expense[1]:<6.2f} | {expense[2]:<12} | {expense[3]} | {expense[4]}")

def view_expenses_by_category():
    """Display expenses filtered by category."""
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    print("Available Categories:")
    for category in categories:
        print(f"{category[0]}. {category[1]}")

    category_id = int(input("Enter the category ID: "))
    cursor.execute("""
    SELECT e.amount, e.date, e.description 
    FROM expenses e
    WHERE e.category_id = ?
    ORDER BY e.date DESC
    """, (category_id,))
    expenses = cursor.fetchall()

    if not expenses:
        print("No expenses found in this category.")
        return

    print("\nExpenses in Selected Category:")
    print("Amount | Date       | Description")
    print("-" * 40)
    for expense in expenses:
        print(f"{expense[0]:<6.2f} | {expense[1]} | {expense[2]}")

def monthly_summary():
    """Show a summary of expenses grouped by category for a specific month."""
    month = input("Enter the month (YYYY-MM): ")
    cursor.execute("""
    SELECT c.name, SUM(e.amount)
    FROM expenses e
    JOIN categories c ON e.category_id = c.id
    WHERE e.date LIKE ?
    GROUP BY c.name
    """, (f"{month}%",))
    summary = cursor.fetchall()

    if not summary:
        print("No expenses recorded for this month.")
        return

    print("\nMonthly Expense Summary:")
    print("Category       | Total Amount")
    print("-" * 30)
    for item in summary:
        print(f"{item[0]:<12} | {item[1]:<10.2f}")

def add_category():
    """Add a new category to the database."""
    name = input("Enter the new category name: ")
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Category '{name}' added successfully!")
    except sqlite3.IntegrityError:
        print("Category already exists.")

def main():
    """Run the main program loop for expense management."""
    initialize_database()

    while True:
        display_menu()
        choice = input("Choose an option: ")
        if choice == "1":
            add_expense()
        elif choice == "2":
            view_all_expenses()
        elif choice == "3":
            view_expenses_by_category()
        elif choice == "4":
            monthly_summary()
        elif choice == "5":
            add_category()
        elif choice == "6":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
