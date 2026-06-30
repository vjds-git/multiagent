from project_starter import init_database, db_engine, inventory_agent, quoting_agent, sales_agent

init_database(db_engine)

task = "Customer wants 200 sheets of A4 paper and 50 units of cardstock, needed by 2025-01-10."
date = "2025-01-01"

inv_result = inventory_agent(task, date)
print("Inventory result:", inv_result)

quote_result = quoting_agent(task, inv_result, order_size="small", date=date)
print("\nQuote result:", quote_result)

line_items = [{"item_name": li["item_name"], "quantity": li["quantity"]} for li in quote_result.get("line_items", [])]
total_price = quote_result.get("total", 0)

sale_result = sales_agent(line_items, total_price, date=date, customer_deadline="2025-01-10")
print("\nSale result:", sale_result)