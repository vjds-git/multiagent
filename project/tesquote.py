from project_starter import (
    init_database, db_engine,
    tool_search_quote_history, tool_calculate_quote
)

init_database(db_engine)

# Test 1: search quote history
history = tool_search_quote_history(["cardstock", "paper"], limit=3)
print("History count:", history["count"])
print("Sample quote:", history["quotes"][0] if history["quotes"] else "none found")

# Test 2: calculate a small quote (no discount expected)
small_quote = tool_calculate_quote(
    line_items=[{"item_name": "A4 paper", "quantity": 200, "unit_price": 0.05}],
    order_size="small"
)
print("\nSmall quote:", small_quote)

# Test 3: calculate a large quote (10% discount expected)
large_quote = tool_calculate_quote(
    line_items=[
        {"item_name": "A4 paper", "quantity": 1500, "unit_price": 0.05},
        {"item_name": "Cardstock", "quantity": 600, "unit_price": 0.15},
    ],
    order_size="large"
)
print("\nLarge quote:", large_quote)