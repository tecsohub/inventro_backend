from typing import Optional
from app.config import pwd_context
from app.models import Admin, Manager, Employee

async def authenticate_user(email: str, password: str, db) -> Optional[dict]:
    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin and pwd_context.verify(password, admin.password):
        return {"user": admin, "role": "admin"}

    manager = db.query(Manager).filter(Manager.email == email).first()
    if manager and pwd_context.verify(password, manager.password):
        return {"user": manager, "role": "manager"}

    employee = db.query(Employee).filter(Employee.email == email).first()
    if employee and pwd_context.verify(password, employee.password):
        return {"user": employee, "role": "employee"}

    return None
