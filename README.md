# Inventro Backend

This is the backend for the Inventro application, a FastAPI-based inventory management system.

## Project Structure

```
inventory.db         # SQLite database file
Procfile             # Defines commands for Heroku/hosting
requirements.txt     # Python dependencies
app/                 # Main application directory
├── __init__.py
├── auth.py          # Authentication logic
├── config.py        # Configuration settings
├── database.py      # Database setup and session management
├── main.py          # FastAPI application entry point
├── models.py        # SQLAlchemy ORM models
├── utils.py         # Utility functions
├── validators.py    # Pydantic models for request/response validation
├── controllers/     # Business logic for different resources
│   └── products.py
└── routes/          # API endpoint definitions
    └── products.py
env/                 # Python virtual environment (should be in .gitignore)
```

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd inventro_backend
    ```

2.  **Create and activate a virtual environment:**
    *   On Windows (PowerShell):
        ```powershell
        python -m venv env
        .\env\Scripts\Activate.ps1
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv env
        source env/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database:**
    The application uses an SQLite database named `inventory.db`. It will be created automatically if it doesn't exist when the application starts.

5.  **Environment Variables:**
    The application might require certain environment variables. Create a `.env` file in the root directory and add any necessary variables. For example:
    ```env
    SECRET_KEY=your_super_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    # Add other environment variables as needed
    ```
    Refer to `app/config.py` for details on required environment variables.

## Running the Application

To run the application locally, use Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This will start the development server, typically accessible at `http://localhost:8000`. The `--reload` flag enables auto-reloading when code changes are detected.

The `Procfile` also defines how to run the application, which is useful for deployment platforms:
```
web: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

The application exposes various API endpoints. The main FastAPI application is defined in `app/main.py`, and specific routes are included from the `app/routes/` directory.

*   **Product Routes:** Defined in `app/routes/products.py`.

Refer to the FastAPI documentation at `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc) when the application is running to see detailed API documentation and try out the endpoints.
