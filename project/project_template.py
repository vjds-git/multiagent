import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union
from sqlalchemy import create_engine, Engine

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################


# Set up and load your env parameters and instantiate your model.


"""Set up tools for your agents to use, these should be methods that combine the database functions above
 and apply criteria to them to ensure that the flow of the system is correct."""


# Tools for inventory agent


# Tools for quoting agent


# Tools for ordering agent


# Set up your agents and create an orchestration agent that will manage them.


# Run your test scenarios by writing them here. Make sure to keep track of them.

import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from smolagents import ToolCallingAgent, OpenAIServerModel, tool

load_dotenv()

# OpenAI-compatible client pointing to Vocareum proxy
client = OpenAI(
    base_url="https://openai.vocareum.com/v1",
    api_key=os.environ.get("UDACITY_OPENAI_API_KEY", ""),
)

MODEL = "gpt-3.5-turbo"

# smolagents model wrapper pointing to Vocareum proxy
smolagents_model = OpenAIServerModel(
    model_id=MODEL,
    api_base="https://openai.vocareum.com/v1",
    api_key=os.environ.get("UDACITY_OPENAI_API_KEY", ""),
)

# ── Tools ────────────────────────────────────────────────

def normalize_date(date_str: str) -> str:
    """
    Ensure a date string includes a time component so SQLite string
    comparisons against stored timestamps behave correctly.
    Converts 'YYYY-MM-DD' -> 'YYYY-MM-DDT23:59:59'.
    If already has a time component, returns as-is.
    """
    if "T" in date_str:
        return date_str
    return f"{date_str}T23:59:59"

@tool
def tool_check_all_inventory(as_of_date: str) -> dict:
    """
    Return the full inventory snapshot as of a given date.

    Args:
        as_of_date: ISO date string in YYYY-MM-DD format
    """
    as_of_date = normalize_date(as_of_date)
    inventory = get_all_inventory(as_of_date)
    return {
        "available_items": inventory,
        "item_count": len(inventory),
        "as_of_date": as_of_date,
    }


@tool
def tool_check_item_stock(item_name: str, as_of_date: str, requested_qty: int) -> dict:
    """
    Check whether sufficient stock exists for a specific item and quantity.

    Args:
        item_name: Name of the inventory item to check (case-insensitive)
        as_of_date: ISO date string in YYYY-MM-DD format
        requested_qty: Number of units the customer wants
    """
    as_of_date = normalize_date(as_of_date)

    # Case-insensitive match against actual inventory catalog
    all_inv = get_all_inventory(as_of_date)
    matched_name = item_name
    for catalog_name in all_inv.keys():
        if catalog_name.lower() == item_name.lower():
            matched_name = catalog_name
            break

    result_df = get_stock_level(matched_name, as_of_date)
    stock = int(result_df["current_stock"].iloc[0]) if not result_df.empty else 0
    can_fulfill = stock >= requested_qty
    return {
        "item_name": matched_name,
        "current_stock": stock,
        "requested_qty": requested_qty,
        "can_fulfill": can_fulfill,
        "shortfall": max(0, requested_qty - stock),
    }


@tool
def tool_reorder_item(item_name: str, quantity: int, as_of_date: str) -> dict:
    """
    Place a stock replenishment order for a low-stock item.

    Args:
        item_name: Name of the item to reorder
        quantity: Number of units to reorder
        as_of_date: ISO date string in YYYY-MM-DD format
    """
    as_of_date = normalize_date(as_of_date)
    unit_price = next(
        (p["unit_price"] for p in paper_supplies if p["item_name"] == item_name), 0.10
    )
    total_cost = round(unit_price * quantity, 2)
    delivery_date = get_supplier_delivery_date(as_of_date, quantity)
    txn_id = create_transaction(
        item_name=item_name,
        transaction_type="stock_orders",
        quantity=quantity,
        price=total_cost,
        date=as_of_date,
    )
    return {
        "transaction_id": txn_id,
        "item_name": item_name,
        "quantity": quantity,
        "total_cost": total_cost,
        "delivery_date": delivery_date,
        "message": f"Reorder placed: {quantity} units of '{item_name}' arriving by {delivery_date}.",
    }


@tool
def tool_search_quote_history(search_terms: list, limit: int = 5) -> dict:
    """
    Retrieve historical quotes relevant to the current request for pricing context.

    Args:
        search_terms: List of keywords to search in quote history
        limit: Maximum number of past quotes to return
    """
    quotes = search_quote_history(search_terms, limit=limit)
    return {"quotes": quotes, "count": len(quotes)}


@tool
def tool_calculate_quote(line_items: list, order_size: str) -> dict:
    """
    Calculate a price quote with bulk discounts for a list of line items.

    Args:
        line_items: List of dicts each with item_name, quantity, and unit_price
        order_size: Size of the order, one of small, medium, or large
    """
    subtotal = 0.0
    total_qty = 0
    breakdown = []
    for item in line_items:
        name = item["item_name"]
        qty = item["quantity"]
        price = item["unit_price"]
        line_cost = round(qty * price, 2)
        subtotal += line_cost
        total_qty += qty
        breakdown.append({
            "item_name": name,
            "quantity": qty,
            "unit_price": price,
            "line_total": line_cost,
        })
    if order_size == "large" or total_qty > 2000:
        discount_pct = 0.10
    elif order_size == "medium" or total_qty > 500:
        discount_pct = 0.05
    else:
        discount_pct = 0.0
    discount_amount = round(subtotal * discount_pct, 2)
    total = round(subtotal - discount_amount, 2)
    return {
        "line_items": breakdown,
        "subtotal": round(subtotal, 2),
        "discount_pct": int(discount_pct * 100),
        "discount_amount": discount_amount,
        "total": total,
        "order_size_label": order_size,
    }


@tool
def tool_get_delivery_date(as_of_date: str, total_quantity: int) -> dict:
    """
    Estimate supplier delivery date based on order date and total quantity.

    Args:
        as_of_date: ISO date string in YYYY-MM-DD format
        total_quantity: Total number of units across all items in the order
    """
    as_of_date = normalize_date(as_of_date)
    delivery = get_supplier_delivery_date(as_of_date, total_quantity)
    order_dt = datetime.fromisoformat(as_of_date)
    delivery_dt = datetime.fromisoformat(delivery)
    lead_days = (delivery_dt - order_dt).days
    return {
        "order_date": as_of_date,
        "delivery_date": delivery,
        "lead_days": lead_days,
    }


@tool
def tool_finalize_sale(line_items: list, total_price: float, as_of_date: str) -> dict:
    """
    Record completed sale transactions for each line item in the database.

    Args:
        line_items: List of dicts each with item_name and quantity
        total_price: Total amount to charge the customer after discounts
        as_of_date: ISO date string in YYYY-MM-DD format
    """
    as_of_date = normalize_date(as_of_date)
    txn_ids = []
    total_qty = sum(item["quantity"] for item in line_items)
    for item in line_items:
        share = item["quantity"] / total_qty if total_qty else 0
        item_price = round(total_price * share, 2)
        txn_id = create_transaction(
            item_name=item["item_name"],
            transaction_type="sales",
            quantity=item["quantity"],
            price=item_price,
            date=as_of_date,
        )
        txn_ids.append(txn_id)
    return {
        "transaction_ids": txn_ids,
        "total_charged": total_price,
        "sale_date": as_of_date,
        "items_sold": len(line_items),
        "status": "completed",
    }


@tool
def tool_get_cash_balance(as_of_date: str) -> dict:
    """
    Return the current cash balance as of a given date.

    Args:
        as_of_date: ISO date string in YYYY-MM-DD format
    """
    as_of_date = normalize_date(as_of_date)
    balance = get_cash_balance(as_of_date)
    return {"cash_balance": round(balance, 2), "as_of_date": as_of_date}

# ── Tool schemas (OpenAI function-calling format) ────────────────────

INVENTORY_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "tool_check_all_inventory",
            "description": "Get full inventory snapshot as of a date.",
            "parameters": {
                "type": "object",
                "properties": {"as_of_date": {"type": "string"}},
                "required": ["as_of_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_check_item_stock",
            "description": "Check stock for a specific item and whether the requested quantity can be fulfilled.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {"type": "string"},
                    "as_of_date": {"type": "string"},
                    "requested_qty": {"type": "integer"},
                },
                "required": ["item_name", "as_of_date", "requested_qty"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_reorder_item",
            "description": "Place a replenishment stock order for a low-stock item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "as_of_date": {"type": "string"},
                },
                "required": ["item_name", "quantity", "as_of_date"],
            },
        },
    },
]

# ── Tool dispatcher ────────────────────────────────────────────────

TOOL_MAP = {
    "tool_check_all_inventory": tool_check_all_inventory,
    "tool_check_item_stock": tool_check_item_stock,
    "tool_reorder_item": tool_reorder_item,
}


def dispatch_tool(tool_name: str, tool_args: dict) -> str:
    """Execute the named tool with the given arguments and return a JSON string."""
    fn = TOOL_MAP.get(tool_name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = fn(**tool_args)
        return json.dumps(result, default=str)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def run_agent(system_prompt: str, user_message: str, agent_tools: list, max_steps: int = 6) -> str:
    """
    Run a smolagents ToolCallingAgent with the given tools and return its final response.
    The system_prompt is prepended to the user message since smolagents manages
    its own internal message history.
    """
    agent = ToolCallingAgent(
        tools=agent_tools,
        model=smolagents_model,
        max_steps=max_steps,
    )
    full_prompt = f"{system_prompt}\n\n{user_message}"
    result = agent.run(full_prompt)
        # smolagents returns the final_answer value directly — could be dict, str, or other
    if isinstance(result, dict):
        return result
    return str(result)


# ── Inventory Agent ────────────────────────────────────────────────

INVENTORY_AGENT_PROMPT = """You are the Inventory Agent for Munder Difflin Paper Company.
Your responsibilities:
- Use tool_check_all_inventory or tool_check_item_stock to verify stock availability.
- Map customer item descriptions to the closest matching inventory item names.
- For each item requested, report: item name, current stock, quantity requested, can_fulfill (yes/no).
- If an item is not in our inventory, say so clearly.
- If stock would fall below ~100 units after the sale, use tool_reorder_item to reorder 500 units.
- Return ONLY a JSON object (no markdown, no commentary) with keys:
    fulfilled_items: list of {item_name, catalog_name, quantity, stock_available, fulfillable}
    unfulfillable_items: list of {item_name, reason}
    reorders_placed: list of reorder confirmations
"""

def _extract_json(text: str) -> dict:
    """
    Robustly extract the first valid JSON object from a model response.
    Handles markdown code fences and duplicated/repeated JSON blocks.
    """
    if not text:
        return {"raw": text}

    # Strip markdown fences if present
    cleaned = text
    if "```" in cleaned:
        parts = cleaned.split("```")
        cleaned = parts[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]

    cleaned = cleaned.strip()

    # Find the first balanced {...} block using a brace counter
    start = cleaned.find("{")
    if start == -1:
        return {"raw": text}

    depth = 0
    for i in range(start, len(cleaned)):
        if cleaned[i] == "{":
            depth += 1
        elif cleaned[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = cleaned[start:i + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    return {"raw": text}

    return {"raw": text}

def inventory_agent(task: str, date: str) -> dict:
    """Run the Inventory Agent for a given task and date."""
    result = run_agent(
        system_prompt=INVENTORY_AGENT_PROMPT,
        user_message=f"Date: {date}\nTask: {task}",
        agent_tools=[tool_check_all_inventory, tool_check_item_stock, tool_reorder_item],
    )
    if isinstance(result, dict):
        return result
    return _extract_json(str(result))


# ── Quoting Agent ────────────────────────────────────────────────

QUOTING_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "tool_search_quote_history",
            "description": "Search historical quotes for pricing context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_terms": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer", "default": 5},
                },
                "required": ["search_terms"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_calculate_quote",
            "description": "Calculate a quoted price with bulk discounts for line items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "line_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_name": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "unit_price": {"type": "number"},
                            },
                        },
                    },
                    "order_size": {"type": "string", "enum": ["small", "medium", "large"]},
                },
                "required": ["line_items", "order_size"],
            },
        },
    },
]

TOOL_MAP["tool_search_quote_history"] = tool_search_quote_history
TOOL_MAP["tool_calculate_quote"] = tool_calculate_quote

QUOTING_AGENT_PROMPT = """You are the Quoting Agent for Munder Difflin Paper Company.
Your responsibilities:
- Use tool_search_quote_history to find relevant past quotes for pricing context.
- Use tool_calculate_quote to compute a price with appropriate bulk discounts.
- IMPORTANT: Only quote and charge for items in "fulfilled_items" from the inventory check,
  using the EXACT quantity the customer requested — never the reorder quantity.
- IGNORE "reorders_placed" entirely when building the quote. Reorders are internal restocking
  actions for our own warehouse and are NOT sold to the customer, and must NEVER appear as a
  line item in the quote.
- Do not invent extra line items beyond what the customer actually asked for.
- For each fulfillable item, use these standard unit prices:
    A4 paper/Letter paper: $0.05-0.06/sheet, Cardstock: $0.15/sheet,
    Colored paper: $0.10/sheet, Glossy paper: $0.20/sheet, Matte paper: $0.18/sheet,
    Construction paper: $0.07/sheet, Poster paper: $0.25/sheet, Envelopes: $0.05/each,
    Standard copy paper: $0.04/sheet. Use $0.10/unit as a default if item is not listed.
- Bulk discounts: 10% for large orders or >2000 units; 5% for medium or >500 units.
- Return ONLY a JSON object (no markdown, no commentary) with keys:
    line_items: list of {item_name, quantity, unit_price, line_total}
    subtotal, discount_pct, discount_amount, total
    pricing_rationale: brief plain-English explanation of the pricing
"""


def quoting_agent(task: str, inventory_result: dict, order_size: str, date: str) -> dict:
    """Run the Quoting Agent given inventory availability and order size."""
    prompt = (
        f"Date: {date}\n"
        f"Order size: {order_size}\n"
        f"Available items from inventory check:\n{json.dumps(inventory_result, indent=2)}\n"
        f"Customer request: {task}"
    )
    result = run_agent(
        system_prompt=QUOTING_AGENT_PROMPT,
        user_message=prompt,
        agent_tools=[tool_search_quote_history, tool_calculate_quote],
    )
    if isinstance(result, dict):
        return result
    return _extract_json(str(result))





# ── Sales Agent ────────────────────────────────────────────────

SALES_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "tool_get_delivery_date",
            "description": "Estimate delivery date based on order date and total quantity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "as_of_date": {"type": "string"},
                    "total_quantity": {"type": "integer"},
                },
                "required": ["as_of_date", "total_quantity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_finalize_sale",
            "description": "Record a completed sale in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "line_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_name": {"type": "string"},
                                "quantity": {"type": "integer"},
                            },
                        },
                    },
                    "total_price": {"type": "number"},
                    "as_of_date": {"type": "string"},
                },
                "required": ["line_items", "total_price", "as_of_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_cash_balance",
            "description": "Get current cash balance as of a date.",
            "parameters": {
                "type": "object",
                "properties": {"as_of_date": {"type": "string"}},
                "required": ["as_of_date"],
            },
        },
    },
]

TOOL_MAP["tool_get_delivery_date"] = tool_get_delivery_date
TOOL_MAP["tool_finalize_sale"] = tool_finalize_sale
TOOL_MAP["tool_get_cash_balance"] = tool_get_cash_balance

SALES_AGENT_PROMPT = """You are the Sales Agent for Munder Difflin Paper Company.
Your responsibilities:
- Use tool_get_delivery_date to determine when the order will arrive.
- Check if the delivery date is before the customer's requested delivery deadline.
- Use tool_finalize_sale to record the transaction in the database.
- Use tool_get_cash_balance for internal awareness only (never share it with customers).
- Return ONLY a JSON object (no markdown, no commentary) with keys:
    status: 'completed' or 'rejected'
    reason: (if rejected, why)
    transaction_ids: list of DB transaction IDs
    delivery_date: confirmed delivery date
    total_charged: final amount
    customer_message: a polite, professional confirmation for the customer
      (include delivery date, items, total — never reveal transaction IDs or cash balance)
"""


def sales_agent(line_items: list, total_price: float, date: str, customer_deadline: str) -> dict:
    """Run the Sales Agent to finalize a transaction."""
    prompt = (
        f"Order date: {date}\n"
        f"Customer requested delivery by: {customer_deadline}\n"
        f"Line items to sell:\n{json.dumps(line_items, indent=2)}\n"
        f"Total price to charge: ${total_price:.2f}\n"
        "Please check delivery feasibility and finalize the sale if possible."
    )
    result = run_agent(
        system_prompt=SALES_AGENT_PROMPT,
        user_message=prompt,
        agent_tools=[tool_get_delivery_date, tool_finalize_sale, tool_get_cash_balance],
    )
    if isinstance(result, dict):
        return result
    return _extract_json(str(result))

# ── Orchestrator ────────────────────────────────────────────────

ORCHESTRATOR_SYSTEM_NOTE = """
(Orchestrator logic is implemented in Python below, not as a separate LLM call,
since it deterministically sequences Inventory -> Quoting -> Sales and composes
the final customer-facing message.)
"""


def handle_customer_request(request: str, request_date: str, order_size: str = "small") -> str:
    """
    Main orchestration entry point. Runs Inventory -> Quoting -> Sales in sequence
    and composes a professional, customer-facing response.
    """
    print(f"\n[Orchestrator] Processing request ({order_size}, {request_date})")

    # Step 1: Inventory check
    print("[InventoryAgent] Checking stock...")
    inv_result = inventory_agent(request, request_date)
    fulfilled_items = [
    item for item in inv_result.get("fulfilled_items", [])
    if str(item.get("fulfillable", "")).lower() == "yes"]
    unfulfillable_items = inv_result.get("unfulfillable_items", [])

    if not fulfilled_items:
        unful_summary = ", ".join(
            f"{u.get('item_name', 'item')} ({u.get('reason', 'not available')})"
            for u in unfulfillable_items
        ) or "the requested items are not currently in stock"
        return (
            "Thank you for your inquiry. Unfortunately, we are unable to fulfill your request "
            f"at this time: {unful_summary}. We apologize for any inconvenience."
        )

    # Step 2: Quote
    print("[QuotingAgent] Generating quote...")
    quote_result = quoting_agent(request, inv_result, order_size, request_date)

    line_items_for_sale = [
        {"item_name": li["item_name"], "quantity": li["quantity"]}
        for li in quote_result.get("line_items", [])
    ]
    total_price = float(quote_result.get("total", 0.0))

    if not line_items_for_sale:
        return (
            "Thank you for your inquiry. We were unable to prepare a quote for the requested items. "
            "Please contact us directly for assistance."
        )

    # Step 3: Extract customer deadline (simple heuristic) or default to +14 days
    deadline_match = re.search(
        r"by\s+(\w+)\s+(\d{1,2}),?\s*(202\d)?", request, re.IGNORECASE
    )
    month_map = {"january": "01", "february": "02", "march": "03", "april": "04",
                 "may": "05", "june": "06", "july": "07", "august": "08",
                 "september": "09", "october": "10", "november": "11", "december": "12"}
    if deadline_match and deadline_match.group(1).lower() in month_map:
        month = month_map[deadline_match.group(1).lower()]
        day = deadline_match.group(2).zfill(2)
        year = deadline_match.group(3) or "2025"
        customer_deadline = f"{year}-{month}-{day}"
    else:
        from datetime import timedelta
        customer_deadline = (
            datetime.fromisoformat(normalize_date(request_date)) + timedelta(days=14)
        ).strftime("%Y-%m-%d")

    # Step 4: Finalize sale
    print("[SalesAgent] Finalizing transaction...")
    sale_result = sales_agent(line_items_for_sale, total_price, request_date, customer_deadline)

    # Step 5: Compose final customer-facing response
    if sale_result.get("customer_message"):
        customer_facing = sale_result["customer_message"]
    else:
        status = sale_result.get("status", "completed")
        if status == "rejected":
            reason = sale_result.get("reason", "we could not meet your delivery deadline")
            customer_facing = f"Thank you for your order. Unfortunately, {reason}."
        else:
            customer_facing = (
                f"Thank you for your order! Total charged: ${total_price:.2f}. "
                f"Delivery estimated: {sale_result.get('delivery_date', customer_deadline)}."
            )

    # Add a note about unfulfillable items if any
    # Filter out any item that was already fulfilled (LLM inconsistency guard)
    fulfilled_names = {
        fi.get("item_name", "").lower() for fi in fulfilled_items
    }
    true_unfulfillable = [
        u for u in unfulfillable_items
        if u.get("item_name", "").lower() not in fulfilled_names
    ]

    if true_unfulfillable:
        unful_names = ", ".join(u.get("item_name", "item") for u in true_unfulfillable)
        customer_facing += (
            f"\n\nPlease note: the following items could not be included in this order: "
            f"{unful_names}. We apologize for any inconvenience."
        )

    return customer_facing


def run_test_scenarios():
    """Process all sample requests through the multi-agent system and save results."""
    print("Initializing Database...")
    init_database(db_engine)

    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    results = []

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############

    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_with_date = f"{row['request']} (Date of request: {request_date})"

        ############
        ############
        ############
        # USE YOUR MULTI AGENT SYSTEM TO HANDLE THE REQUEST
        ############
        ############
        ############

        response = handle_customer_request(
            request=request_with_date,
            request_date=request_date,
            order_size=str(row.get("need_size", "small")).lower()
        )

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()
