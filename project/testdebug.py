
from project_template import init_database, db_engine, inventory_agent

init_database(db_engine)

result = inventory_agent(
    task="I need 500 sheets of A4 paper and 200 units of cardstock for an office meeting by April 15, 2025. (Date of request: 2025-04-01)",
    date="2025-04-01"
)

print("\nfulfilled_items:", result.get("fulfilled_items"))
print("unfulfillable_items:", result.get("unfulfillable_items"))