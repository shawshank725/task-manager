from flask import Flask, render_template, url_for, redirect
from flask_login import login_user, LoginManager, login_required, logout_user
from extensions import db, bcrypt
from flask_login import current_user
from sqlalchemy.orm import Session

from entity.User import User
from entity.Task import StatusEnum, Task
from entity.Category import Category

from forms.LoginForm import LoginForm
from forms.RegisterForm import RegisterForm
from forms.TaskForm import TaskForm
from forms.CategoryForm import CategoryForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///database.db"
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


# making the tables in the database
with app.app_context():
    try: 
        db.create_all()
        print("made the tables")
    except Exception as e: 
        print("Couldnt make the tables")
        print(e)

@app.route("/")
def home():
    if (current_user):
        return redirect(url_for("dashboard"))
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if (form.validate_on_submit()):
        user = User.query.filter_by(username = form.username.data).first()
        if (user):
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("dashboard"))
    return render_template("login.html", form = form)


@app.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard(): 
    tasks = Task.query.filter_by(user_id = current_user.id).all()
    categories = Category.query.filter_by(user_id = current_user.id).all()

    form = CategoryForm()
    if (form.validate_on_submit()):
        new_category = Category(
            category_name=form.category_name.data,
            user_id=current_user.id
        )
        try: 
            db.session.add(new_category)
            db.session.commit()
            print("Added the category")
        except Exception as e: 
            print("Could not add the new category." )
            print(e)
    return render_template("dashboard.html", user = current_user, tasks = tasks, categories = categories, form=form)



@app.route("/create-new-task", methods = ["GET", "POST"])
@login_required
def createNewTask(): 
    form = TaskForm()
    form.category.choices = [(c.id, c.category_name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if (form.validate_on_submit()):
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            completed=False,
            category_id=form.category.data, 
            user_id=current_user.id,
            status=StatusEnum.PENDING
        )
        try: 
            db.session.add(new_task)
            db.session.commit()
            print("Added the task")
        except Exception as e: 
            print("Could not add the new task." )
            print(e)
        return redirect(url_for("dashboard"))
    return render_template("createNewTask.html",
                            form=form, 
                            user = current_user,
                            page_title="Create Task",
                            submit_text="Create Task")

@app.route("/add-category", methods=["POST"])
@login_required
def addCategory():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(
            category_name=form.category_name.data,
            user_id=current_user.id
        )
        try: 
            db.session.add(new_category)
            db.session.commit()
        except Exception as e:
            print("Could not add category:", e)
    return redirect(url_for("dashboard"))

@app.route("/update-task/<int:task_id>", methods = ["GET", "POST"])
@login_required
def updateTask(task_id): 
    print("TASK ID IS THIS - ", task_id)
    task = Task.query.get_or_404(task_id)

    # Make sure the current user owns this task
    if task.user_id != current_user.id:
        return "Unauthorized", 403

    form = TaskForm(obj=task)  # Populate form with existing task data

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        # completed field is not in form; keep existing value
        try:
            db.session.commit()
            print("Updated the task")
        except Exception as e:
            print("Could not update the task")
            print(e)
        return redirect(url_for("dashboard"))

    return render_template("createNewTask.html", 
                            form=form, 
                            user=current_user,        
                            page_title="Update Task",
                            submit_text="Update Task")

@app.route("/delete-task/<int:task_id>", methods=["POST"])
@login_required
def deleteTask(task_id):
    task = Task.query.get_or_404(task_id)

    # Make sure the current user owns this task
    if task.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        db.session.delete(task)
        db.session.commit()
        print(f"Deleted task {task_id}")
    except Exception as e:
        print("Could not delete the task")
        print(e)

    return redirect(url_for("dashboard"))

@app.route("/delete-category/<int:category_id>", methods=["POST"])
@login_required
def deleteCategory(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        db.session.delete(category)
        db.session.commit()
    except Exception as e:
        print("Could not delete category:", e)
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    print("inside the register form part. before if statement and after form")
    if (form.validate_on_submit()):
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        new_user = User(username=form.username.data, password=hashed_password)
        try: 
            db.session.add(new_user)
            db.session.commit()
            print("successfully added the new user to the database")
            return redirect(url_for("login"))
        except:
            print("failed to add the data to the database.")
    else : 
        print("form is not valid")
    return render_template("register.html", form = form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if (__name__ == "__main__"):
    app.run(debug=True)