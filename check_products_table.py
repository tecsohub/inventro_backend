from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
cols = inspector.get_columns('products')
print('Products table columns:')
for col in cols:
    print(f'  {col["name"]}: {col["type"]} (nullable: {col["nullable"]})')
