from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, ValidationError
import datetime as dt

# ---------------------------- START FLASK FRAMEWORK ------------------------------- #
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]

# ---------------------------- CONNECT TO DATABASE ------------------------------- #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///to-dos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ---------------------------- DATABASE SETUP ------------------------------- #
class Categories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    to_dos_category = relationship("ToDos", back_populates="parent_category")

    def __repr__(self):
        """returns name of Category when printed instead of <Categories ID>"""
        return self.name


class ToDos(db.Model):
    __tablename__ = "to_dos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    parent_category = relationship("Categories", back_populates="to_dos_category")
    due_date = db.Column(db.Date)
    subtasks = relationship("SubTasks", back_populates="parent_to_do")

    def __repr__(self):
        """returns name of ToDo when printed instead of <ToDos ID>"""
        return self.name


class SubTasks(db.Model):
    __tablename__ = "subtasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    due_date = db.Column(db.Date)
    to_do_id = db.Column(db.Integer, db.ForeignKey("to_dos.id"))
    parent_to_do = relationship("ToDos", back_populates="subtasks")
    category = db.Column(db.String(250))

    def __repr__(self):
        """returns name of SubTasks when printed instead of <SubToDos ID>"""
        return self.name


class GotDones(db.Model):
    __tablename__ = "got_dones"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    date = db.Column(db.Date)

    def __repr__(self):
        """returns name of GotDone when printed instead of <GotDones ID>"""
        return self.name


# # only run the first time to create DBs
# with app.app_context():
#     db.create_all()
#     new_category_one = Categories(
#         name="Personal",
#     )
#     new_category_two = Categories(
#         name="Business",
#     )
#     db.session.add(new_category_one)
#     db.session.add(new_category_two)
#     db.session.commit()


# ---------------------------- CREATE FORMS ------------------------------- #
# create custom validator so due dates can't be in the past
def date_check(form, field):
    if field.data < dt.datetime.now().date():
        raise ValidationError("Due Date can't be in the past!")


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')


class UpdateCategoryForm(FlaskForm):
    name = StringField('New Category Name', validators=[DataRequired()])
    submit = SubmitField('Update Category')


class SubTaskForm(FlaskForm):
    name = StringField('Subtask Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired(), date_check])
    submit = SubmitField('Add Subtask')


# ---------------------------- CREATE ROUTES ------------------------------- #
@app.route('/')
def dashboard():
    """renders index.html, calls all ToDos saved in the DB and shows an overview of the ToDo"""
    to_dos = db.session.query(ToDos).order_by(asc(ToDos.due_date))
    print(to_dos)
    return render_template('index.html', all_to_dos=to_dos)


@app.route('/add-new-to-do', methods=["GET", "POST"])
def add_new_to_do():
    """renders 'add-new-to-do.html', if form is filled out and submitted, gets data from user input and saves it as new
    To Do in the DB, redirects to show-to-do.html"""
    categories = db.session.query(Categories).all()

    # ToDoForm setup withing function to be able to call new categories to choose from
    class ToDoForm(FlaskForm):
        name = StringField('To Do Name', validators=[DataRequired()])
        category = SelectField('Category', choices=categories, validators=[DataRequired()])
        due_date = DateField('Due Date', validators=[DataRequired(), date_check])
        submit = SubmitField('Add To Do')
    form = ToDoForm()
    if form.validate_on_submit():
        category = Categories.query.filter_by(name=form.category.data).first()
        new_to_do = ToDos(
            name=form.name.data,
            parent_category=category,
            due_date=form.due_date.data)
        db.session.add(new_to_do)
        db.session.commit()
        return redirect(url_for('show_to_do', to_do_id=new_to_do.id))
    else:
        return render_template('add-new-to-do.html', form=form)


@app.route('/show-to-do/<int:to_do_id>')
def show_to_do(to_do_id):
    """renders show-to-do.html, calls requested To Do from the DB and shows all info"""
    requested_to_do = db.session.get(ToDos, to_do_id)
    return render_template('show-to-do.html', to_do=requested_to_do)


@app.route('/show-category/<category>')
def show_category(category):
    """renders show-category.html, calls requested Category from the DB and shows all related To Dos"""
    requested_category = Categories.query.filter_by(name=category).first()
    return render_template('show-category.html', category=requested_category)


@app.route('/all-categories')
def all_categories():
    """renders all-categories.html, calls all Categories from the DB"""
    categories = db.session.query(Categories).all()
    return render_template('all-categories.html', categories=categories)


@app.route('/add-new-category', methods=["GET", "POST"])
def add_new_category():
    """renders 'add-new-category.html', if form is filled out and submitted, gets data from user input and saves it as new
    Category in the DB, redirects to show-category.html"""
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Categories(
            name=form.name.data
        )
        try:
            db.session.add(new_category)
            db.session.commit()

        except IntegrityError:
            flash("This Category already exists!")
        return redirect(url_for('show_category', category=new_category.name))
    else:
        return render_template('add-new-category.html', form=form)


@app.route('/got-done')
def got_done():
    """renders got-done.html, calls all GotDones saved in the DB and shows an overview of the GotDone"""
    got_dones = db.session.query(GotDones).order_by(desc(GotDones.date))
    return render_template('got-done.html', all_got_dones=got_dones)


@app.route('/mark-done/<int:to_do_id>')
def mark_done(to_do_id):
    """calls requested to_do from ToDos DB and all related SubTasks, saves them in GotDones DB, redirects to delete.html
    """
    requested_to_do = db.session.get(ToDos, to_do_id)
    new_got_done = GotDones(
        name=requested_to_do.name,
        category=str(requested_to_do.parent_category),
        date=dt.datetime.now().date()
    )
    db.session.add(new_got_done)
    db.session.commit()
    subtasks = requested_to_do.subtasks
    if subtasks:
        for subtask in subtasks:
            new_got_done = GotDones(
                name=subtask.name,
                category=str(subtask.category),
                date=dt.datetime.now().date()
            )
            db.session.add(new_got_done)
            db.session.commit()
    return redirect(url_for('delete', to_do_id=to_do_id))


@app.route('/delete/<int:to_do_id>')
def delete(to_do_id):
    """deletes requested To Do and all related SubTasks from DB"""
    requested_to_do = db.session.get(ToDos, to_do_id)
    subtasks = requested_to_do.subtasks
    for subtask in subtasks:
        db.session.delete(subtask)
        db.session.commit()
    db.session.delete(requested_to_do)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/update-category/<int:category_id>', methods=["GET", "POST"])
def update_category(category_id):
    category_update = db.session.get(Categories, category_id)
    form = UpdateCategoryForm()
    if form.validate_on_submit():
        category_update.name = form.name.data
        db.session.commit()
        return redirect(url_for('show_category', category=category_update))
    else:
        return render_template('update-category.html', form=form, category=category_update)


@app.route('/add-new-subtask/<int:to_do_id>', methods=["GET", "POST"])
def add_new_subtask(to_do_id):
    """renders 'add-new-subtask.html', if form is filled out and submitted, gets data from user input and saves it as new
    Subtask of the requested To Do to the DB, redirects to show-to-do.html"""
    form = SubTaskForm()
    if form.validate_on_submit():
        to_do = db.session.get(ToDos, to_do_id)
        new_subtask = SubTasks(
            name=form.name.data,
            due_date=form.due_date.data,
            parent_to_do=to_do,
            category=str(to_do.parent_category))
        db.session.add(new_subtask)
        db.session.commit()
        return redirect(url_for('show_to_do', to_do_id=to_do.id))
    else:
        return render_template('add-new-subtask.html', form=form)


@app.route('/mark-done-sub/<int:subtask_id>')
def mark_done_sub(subtask_id):
    """calls requested subtask from SubTasks DB, deletes it and saves it in GotDones DB"""
    requested_subtask = db.session.get(SubTasks, subtask_id)
    new_got_done = GotDones(
        name=requested_subtask.name,
        category=str(requested_subtask.category),
        date=dt.datetime.now().date()
    )
    db.session.add(new_got_done)
    db.session.commit()
    return redirect(url_for('delete_sub', subtask_id=subtask_id))


@app.route('/delete_sub/<int:subtask_id>')
def delete_sub(subtask_id):
    """deletes requested subtask from SubTasks DB"""
    requested_subtask = db.session.get(SubTasks, subtask_id)
    to_do_id = requested_subtask.to_do_id
    db.session.delete(requested_subtask)
    db.session.commit()
    return redirect(url_for('show_to_do', to_do_id=to_do_id))


if __name__ == "__main__":
    app.run(debug=True)
