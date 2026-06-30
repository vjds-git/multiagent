from project_starter import (
    init_database, db_engine,
    tool_check_all_inventory, tool_check_item_stock, tool_reorder_item
)

init_database(db_engine)

# Test 1: check all inventory
all_inv = tool_check_all_inventory("2025-01-01")
print("Item count:", all_inv["item_count"])
print("Sample items:", list(all_inv["available_items"].items())[:3])

# Test 2: check stock for one item (use a name from the sample items above)
sample_item_name = list(all_inv["available_items"].keys())[0]
stock_check = tool_check_item_stock(sample_item_name, "2025-01-01", 50)
print("\nStock check:", stock_check)

# Test 3: place a reorder
reorder = tool_reorder_item(sample_item_name, 100, "2025-01-01")
print("\nReorder result:", reorder)