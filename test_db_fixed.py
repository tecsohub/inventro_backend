from app.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)

print("=== Managers table columns ===")
cols = inspector.get_columns('managers')
for col in cols:
    print(f'  {col["name"]}: {col["type"]} (nullable: {col["nullable"]})')

print("\n=== Companies table columns ===")
try:
    cols = inspector.get_columns('companies')
    for col in cols:
        print(f'  {col["name"]}: {col["type"]} (nullable: {col["nullable"]})')
except Exception as e:
    print(f"Error accessing companies table: {e}")

print("\n=== Sample data ===")
with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT id, name FROM companies LIMIT 3"))
        print("Companies:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
    except Exception as e:
        print(f"Error querying companies: {e}")

    try:
        result = conn.execute(text("SELECT id, email, company_id FROM managers LIMIT 3"))
        print("Managers:")
        for row in result:
            print(f"  {row[0]}: {row[1]} (company: {row[2]})")
    except Exception as e:
        print(f"Error querying managers: {e}")
