# done-o-saur
Website that enables User to set and track To Dos in different Categories. Built with Flask-Framework.

CRUD-Functions:
CREATE:
- Categories
- To Dos with due date in Categories
- Subtasks with seperate due date to To Dos
READ:
- All Categories
- All To Dos (sorted ascending by due date)
- Each To Do including Subtasks
- All Got Dones
UPDATE:
- Name of Category
- Name, category and due date of To Dos and all relational Subtasks
- Mark To Dos and Subtasks as done (automatically creates new entry in DB for GotDones)
DELETE:
- To Dos and all relational Subtasks (after warning)
- Single Subtasks
- All GotDones

# What I learned / used for the first time:
- Building a Website with the Bootstrap Framework and Bootstrap Snippets (e.g. Dropdown-Menu in Navbar)
- Creating my own validation for a FlaskForm
- Sorting items in a Database by a certain attribute (for the output with sqlalchemy.asc and .desc, as well as when creating the DB with sqlalchemy.ext.orderinglist)
- Reusing data from WTForms in different contents (rendering pages, passing over to other forms)
- Calling DB relational objects and adjusting type to reuse (Categories)

Homepage
![image](https://github.com/lauraporsch/done-o-saur/assets/127047376/9037002c-20fe-490a-9d7f-92614336cb49)

Example for To Do with Subtasks
![image](https://github.com/lauraporsch/done-o-saur/assets/127047376/49825767-fc88-4a5b-a939-daf716e0449e)

Example for Got Done List
![image](https://github.com/lauraporsch/done-o-saur/assets/127047376/a50fade2-3218-4657-8099-5545eae2a863)

