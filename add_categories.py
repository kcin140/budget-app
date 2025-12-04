import sys
sys.path.insert(0, '/Users/nickkyburz/Desktop/budget-app')

from sheets_client import add_category

# Categories to add
categories = [
    ("HOA", 285),
    ("Mortgage", 2700),
    ("Utilities (Electric)", 150),
    ("Car Insurance", 100),
    ("Cell Phone", 45),
    ("Debt", 700),
    ("Gym Membership (Pelaton, YMCA)", 80),
    ("Internet", 70),
    ("Subscription (Costso, Netflix)", 12),
    ("Car Maintenance", 50),
    ("Eating Out", 100),
    ("Gas", 250),
    ("Gifts", 50),
    ("Grocery", 300),
    ("Grocery (Costco)", 300),
    ("Medical (Doctor, Dental, Vision, etc.)", 100),
    ("Misc.", 100),
    ("Nala", 100),
    ("Personal", 200),
    ("Supplemental (Collagen, Fishoil, Prenatal, etc.)", 50),
    ("Cleaning Supplies, Toiletries", 50),
]

print("Adding categories to Google Sheets...")
for name, amount in categories:
    try:
        add_category(name, amount)
        print(f"✓ Added: {name} - ${amount}")
    except Exception as e:
        print(f"✗ Error adding {name}: {e}")

print(f"\nDone! Added {len(categories)} categories.")
print("Total planned: $5,912")
