from project_starter import (
    init_database, db_engine,
    tool_get_delivery_date, tool_finalize_sale, tool_get_cash_balance
)

init_database(db_engine)

# Test 1: delivery date estimate
delivery = tool_get_delivery_date("2025-01-01", 50)
print("Delivery estimate:", delivery)

# Test 2: check cash balance before sale
cash_before = tool_get_cash_balance("2025-01-01")
print("\nCash before:", cash_before)

# Test 3: finalize a sale
sale = tool_finalize_sale(
    line_items=[{"item_name": "A4 paper", "quantity": 200}],
    total_price=10.0,
    as_of_date="2025-01-01"
)
print("\nSale result:", sale)

# Test 4: check cash balance after sale (should be higher)
cash_after = tool_get_cash_balance("2025-01-01")
print("\nCash after:", cash_after)