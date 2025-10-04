from flask_wtf import FlaskForm
from wtforms import  DateField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, Length
from entity.Category import Category 
class TaskForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Task title"})
    
    description = StringField(validators=[InputRequired(), Length(
        min=4, max=100)], render_kw={"placeholder": "Task description"})
    
    due_date = DateField(
        "Due Date", 
        format="%Y-%m-%d", 
        validators=[InputRequired()]
    )

    category = SelectField(
        "Category",
        validators=[InputRequired()],
        coerce=int 
    )

    submit = SubmitField("Create Task")

    