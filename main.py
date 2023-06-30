from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from sqlalchemy.orm import relationship
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired
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
    name = db.Column(db.String(250), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    parent_category = relationship("Categories", back_populates="to_dos_category")
    due_date = db.Column(db.Date)
    sub_to_dos = relationship("SubToDos", back_populates="parent_to_do")

    def __repr__(self):
        """returns name of ToDo when printed instead of <ToDos ID>"""
        return self.name


class SubToDos(db.Model):
    __tablename__ = "sub_to_dos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    due_date = db.Column(db.Date)
    to_do_id = db.Column(db.Integer, db.ForeignKey("to_dos.id"))
    parent_to_do = relationship("ToDos", back_populates="sub_to_dos")
    category = db.Column(db.String(250), unique=True)

    def __repr__(self):
        """returns name of SubToDos when printed instead of <SubToDos ID>"""
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
class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')


class UpdateCategoryForm(FlaskForm):
    name = StringField('New Category Name', validators=[DataRequired()])
    submit = SubmitField('Update Category')


# ---------------------------- CREATE ROUTES ------------------------------- #
@app.route('/')
def dashboard():
    """renders index.html, calls all ToDos saved in the DB and shows an overview of the ToDo"""
    to_dos = db.session.query(ToDos).order_by(asc(ToDos.due_date))
    return render_template('index.html', all_to_dos=to_dos)


@app.route('/add-new-to-do', methods=["GET", "POST"])
def add_new_to_do():
    """renders 'add-new-to-do.html', if form is filled out and submitted, gets data from user input and saves it as new
    ToDo in the DB, redirects to show-to-do.html"""
    categories = db.session.query(Categories).all()

    # ToDoForm setup withing function to be able to call new categories to choose from
    class ToDoForm(FlaskForm):
        name = StringField('To Do Name', validators=[DataRequired()])
        category = SelectField('Category', choices=categories, validators=[DataRequired()])
        due_date = DateField('Due Date', validators=[DataRequired()])
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
    """renders show-to-do.html, calls requested ToDo from the DB and shows all info"""
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
        db.session.add(new_category)
        db.session.commit()
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
    """calls requested to_do from ToDos DB, deletes it and saves it in GotDones DB"""
    requested_to_do = db.session.get(ToDos, to_do_id)
    new_got_done = GotDones(
        name=requested_to_do.name,
        category=str(requested_to_do.parent_category),
        date=dt.datetime.now().date()
    )
    db.session.add(new_got_done)
    db.session.commit()
    return redirect(url_for('delete', to_do_id=to_do_id))


@app.route('/delete/<int:to_do_id>')
def delete(to_do_id):
    """deletes requested to_do from ToDos DB"""
    requested_to_do = db.session.get(ToDos, to_do_id)
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


if __name__ == "__main__":
    app.run(debug=True)
