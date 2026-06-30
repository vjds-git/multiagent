from project_starter import init_database, db_engine, inventory_agent

init_database(db_engine)

result = inventory_agent(
    task="Customer wants 200 sheets of A4 paper and 50 units of cardstock.",
    date="2025-01-01"
)

print("Inventory Agent result:")
print(result)