from sqlalchemy.orm import Session

from app.models import Employee

async def list_employees_logic(current_user: dict, db: Session):
    """
    Logic to list employees under the current manager.
    This function retrieves the employees associated with the manager's ID.
    """
    manager_id = current_user["user"].id
    employees = db.query(Employee).filter(Employee.manager_id == manager_id).all()

    if not employees:
        return {"message": "No employees found for this manager."}

    return [employee.to_dict() for employee in employees]
