from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
cols = inspector.get_columns('managers')
print('Managers table columns:')
for col in cols:
    print(f'  {col["name"]}: {col["type"]}')
