# Task Management REST API

This project is a **Task Management REST API** built using Flask. It allows users to register, log in, and manage their tasks with support for categories, task statuses, and filters.

---

## Installation

Install all required modules using pip:

```bash
pip install flask flask_sqlalchemy flask_login flask_bcrypt flask_wtf
pip install pytest
```

---

## Project Layout

```
project-root/
│
├── app.py                        # Main application entry point
├── extensions.py                 # Database and bcrypt setup
│
├── entity/                       # ORM model classes
│   ├── User.py                   # User model
│   ├── Task.py                   # Task model with status enum
│   ├── Category.py               # Category model
│
├── forms/                        # (Used in frontend version) FlaskForm classes
│   ├── LoginForm.py
│   ├── RegisterForm.py
│   ├── TaskForm.py
│   ├── CategoryForm.py
│
├── templates/                    # HTML templates (if using frontend)
│   ├── home.html
│   ├── dashboard.html
│   ├── createNewTask.html
│   ├── login.html
│   ├── register.html
│
├── tests/                        # Unit tests for API endpoints
│   ├── test_auth.py
│   ├── test_task.py
│
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration for deployment
└── README.md                     # Project documentation (this file)
```

---

## Technologies Used

| Technology | Purpose |
|-------------|----------|
| Flask | Web framework |
| Flask-SQLAlchemy | ORM for database interaction |
| Flask-Login | Session-based user authentication |
| Flask-Bcrypt | Password hashing |
| SQLite | Database |
| Pytest | Unit testing |
| Docker | Containerization |

---

## Authentication

This application uses **Session-based Authentication** implemented with Flask-Login.

- Users register with a username and password.
- Passwords are securely hashed using Flask-Bcrypt.
- Session cookies are used to maintain user login state.

---

## API Endpoints

### User Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| POST | `/api/register` | Register a new user |
| POST | `/api/login` | Log in and start a session |
| GET | `/api/logout` | Log out the current user |

### Task Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/api/tasks` | Get all tasks for current user (supports filters) |
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks/<id>` | Get a single task |
| PUT | `/api/tasks/<id>` | Update a task |
| PATCH | `/api/tasks/<id>/complete` | Mark a task as completed |
| DELETE | `/api/tasks/<id>` | Delete a task |

### Category Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/api/categories` | List all categories for user |
| POST | `/api/categories` | Create a new category |
| DELETE | `/api/categories/<id>` | Delete a category |

---

## Filters for Tasks

You can filter tasks by:
- `status` → PENDING or COMPLETED
- `category_id`
- `due_date`

Example:

```bash
GET /api/tasks?status=COMPLETED&category_id=1
```

---

## Docker Setup

A simple Dockerfile is provided.

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t task-api .
docker run -p 5000:5000 task-api
```

---

## Architecture Overview

### Request Lifecycle
1. Client sends HTTP request to Flask API.
2. Flask routes request to the correct function based on URL and method.
3. Controller (view function) processes request and interacts with SQLAlchemy models.
4. Database query executes and results are serialized to JSON.
5. Response is sent back to client.

### Memory Model and Concurrency
Flask runs on a **WSGI** model. Each request is handled by one worker process/thread.
To handle multiple concurrent users, use a WSGI server such as **Gunicorn** with multiple workers.

### Synchronous vs Asynchronous
Flask is synchronous by default. While async frameworks (like FastAPI) can handle high I/O workloads better, Flask’s synchronous design is simpler and sufficient for moderate traffic.

---

## Testing

Unit tests are written using **pytest**.

Example:

```python
def test_register(client):
    response = client.post("/api/register", json={"username": "test", "password": "1234"})
    assert response.status_code == 201
```

Run tests using:
```bash
pytest
```

---

## License

This project is open source and available for educational purposes.
