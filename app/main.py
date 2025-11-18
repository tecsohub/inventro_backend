from fastapi import Depends, FastAPI

from app.database import create_tables
from app.utils import roles_required
from app.routes.auth import router as auth_router
from app.routes.companies import router as company_router
from app.routes.manager import router as manager_router
from app.routes.products import router as product_router
from app.routes.new_products import router as new_product_router
from app.routes.users import router as user_router


app = FastAPI()

create_tables()

# Admin-only endpoint
@app.get("/admin/dashboard")
async def admin_dashboard(current_user: dict = Depends(roles_required(["admin"]))):
    return {"message": f"Welcome Admin {current_user['user'].name}"}


app.include_router(auth_router)
app.include_router(company_router)
app.include_router(manager_router)
app.include_router(product_router)
app.include_router(new_product_router)
app.include_router(user_router)
