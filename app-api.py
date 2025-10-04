from flask import Flask, jsonify, request
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from sqlalchemy.orm import Session
from extensions import db, bcrypt
from entity.User import User
from entity.Task import StatusEnum, Task
from entity.Category import Category

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "thisisasecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db.init_app(app)
bcrypt.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    with Session(db.engine) as session:
        return session.get(User, int(user_id))


with app.app_context():
    try:
        db.create_all()
        print("Database tables created")
    except Exception as e:
        print("Could not create tables:", e)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Task Manager API"})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf8")
    new_user = User(username=data["username"], password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        print("DB error:", e)
        return jsonify({"error": "Failed to register user"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()

    if user and bcrypt.check_password_hash(user.password, data.get("password")):
        login_user(user)
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})


@app.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing task data"}), 400

    new_task = Task(
        title=data.get("title"),
        description=data.get("description"),
        due_date=data.get("due_date"),
        completed=False,
        category_id=data.get("category_id"),
        user_id=current_user.id,
        status=StatusEnum.PENDING
    )

    try:
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"message": "Task created successfully"}), 201
    except Exception as e:
        print("Error creating task:", e)
        return jsonify({"error": "Could not create task"}), 500


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.due_date = data.get("due_date", task.due_date)
    task.category_id = data.get("category_id", task.category_id)
    task.status = StatusEnum[data.get("status", task.status.name)]

    try:
        db.session.commit()
        return jsonify({"message": "Task updated successfully"})
    except Exception as e:
        print("Error updating task:", e)
        return jsonify({"error": "Could not update task"}), 500


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": f"Task {task_id} deleted successfully"})
    except Exception as e:
        print("Error deleting task:", e)
        return jsonify({"error": "Could not delete task"}), 500

@app.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    query = Task.query.filter_by(user_id=current_user.id)
    status = request.args.get("status")
    category_id = request.args.get("category_id")
    due_date = request.args.get("due_date")

    if status:
        query = query.filter_by(status=status)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if due_date:
        query = query.filter(Task.due_date == due_date)

    tasks = query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "status": t.status,
        "category": t.category.category_name if t.category else None
    } for t in tasks])


@app.route("/api/tasks/<int:task_id>/complete", methods=["PATCH"])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    task.status = StatusEnum.COMPLETED
    db.session.commit()
    return jsonify({"message": "Task marked as completed"})



@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {"id": c.id, "name": c.category_name}
        for c in categories
    ])


@app.route("/api/categories", methods=["POST"])
@login_required
def create_category():
    data = request.get_json()
    if not data or "category_name" not in data:
        return jsonify({"error": "Missing category_name"}), 400

    new_category = Category(
        category_name=data["category_name"],
        user_id=current_user.id
    )

    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify({"message": "Category created successfully"}), 201
    except Exception as e:
        print("Error creating category:", e)
        return jsonify({"error": "Could not create category"}), 500


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    if (category is None):
        return jsonify({"error": "Category not found"}), 404
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": f"Category {category_id} deleted successfully"})
    except Exception as e:
        print("Error deleting category:", e)
        return jsonify({"error": "Could not delete category"}), 500


if __name__ == "__main__":
    app.run(debug=True)
