from project_starter import init_database, generate_financial_report, db_engine 

init_database(db_engine)
report = generate_financial_report('2025-01-01')
print('Cash Bal:', report['cash_balance'])
print('Inv items:', len(report['inventory_summary']))
print('DB ON')