from project_template import init_database, db_engine, handle_customer_request

init_database(db_engine)

response = handle_customer_request(
    request="I need 200 sheets of A4 paper and 50 units of cardstock, needed by April 15, 2025.",
    request_date="2025-01-01",
    order_size="small"
)

print("\n=== FINAL CUSTOMER RESPONSE ===")
print(response)