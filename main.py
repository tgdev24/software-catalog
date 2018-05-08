#!flask/bin/python
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Fields, MenuItem

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/")
@app.route("/fields/")
def fields():
	# field = session.query(MenuItem).filter_by(id=7).one()
	# session.delete(field)
	# session.commit()
	fields = session.query(Fields).all()
	return render_template('fields.html', fields = fields)

@app.route("/fields/<id>/")
def languages(id):
	field = session.query(Fields).filter_by(id=id).one()
	languages = session.query(MenuItem).filter_by(specialty_id=field.id).all()
	return render_template('menu.html', field = field, languages = languages)

@app.route("/fields/new/", methods=['GET', 'POST'])
def newField():
	if(request.method == 'POST'):
		if(request.form["choice"] == "Submit"):
			newField = Fields(name=request.form['name'])
			session.add(newField)
			session.commit()
			return redirect(url_for('fields'))
		else:
			return redirect(url_for('fields'))
	else:
		return render_template('newField.html')

@app.route("/fields/<id>/edit/", methods=['GET', 'POST'])
def editField(id):
	field = session.query(Fields).filter_by(id=id).one()
	if(request.method == 'POST'):
		if(request.form["choice"] == "Submit"):
			field.name = request.form['name']
			session.add(field)
			session.commit()
			return redirect(url_for('fields'))
		else:
			return redirect(url_for('fields'))
	else:
		return render_template('editField.html', field=field)

@app.route("/fields/<id>/delete/", methods=['GET', 'POST'])
def deleteField(id):
	fieldToBeDeleted = session.query(Fields).filter_by(id=id).one()
	if(request.method == 'POST'):
		choice = request.form['choice']
		if(choice == "Yes"):
			session.delete(fieldToBeDeleted)
			session.commit()
			return redirect(url_for('fields'))
		else:
			return redirect(url_for('fields'))
	else:
		return render_template('deleteField.html', name=fieldToBeDeleted.name)

@app.route("/fields/<id>/new/", methods=['GET', 'POST'])
def newMenuItem(id):
	currentfield = session.query(Fields).filter_by(id=id).one()
	if(request.method == 'POST'):
		if(request.form["choice"] == "Add"):
			newMenuItem = MenuItem(name=request.form['name'], description=request.form['description'], website=request.form['website'], image=request.form['image'], specialty_id=currentfield.id)
			session.add(newMenuItem)
			session.commit()
			return redirect(url_for('languages', id = currentfield.id))
		else:
			return redirect(url_for('languages', id = currentfield.id))
	else:
		return render_template('newMenuItem.html', field = currentfield.name)

@app.route("/fields/<field>/<menu_id>/edit/", methods=['GET', 'POST'])
def editMenuItem(field, menu_id):
	editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == "POST":
		if(request.form["choice"] == "Edit"):
			if request.form['name']:
				editedItem.name = request.form['name']
			if request.form['description']:
				editedItem.description = request.form['description']
			if request.form['website']:
				editedItem.website = request.form['website']
			if request.form['image']:
				editedItem.image = request.form['image']
			if request.form['category']:
				specialty = session.query(Fields).filter_by(name=request.form['category']).one()
				editedItem.specialty_id = specialty.id
			session.add(editedItem)
			session.commit()
			return redirect(url_for('languages', field=field))
		else:
			return redirect(url_for('languages', field=field))
	else:
		categories = session.query(Fields).all()
		return render_template('editMenuItem.html', categories=categories, menuitem=editedItem)

@app.route('/fields/<field>/<menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(field, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
    	if(request.form['choice'] == 'Delete'):
        	session.delete(itemToDelete)
        	session.commit()
        	return redirect(url_for('languages', id=field))
        else:
        	return redirect(url_for('languages', field=field))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)
    # return "This page is for deleting menu item %s" % menu_id

@app.route('/fields/latestnew', methods=['GET', 'POST'])
def latestNew():
	fields=session.query(Fields).all()
	if(request.method == 'POST'):
		if(request.form['choice'] == "Submit"):
			field = session.query(Fields).filter_by(name=request.form["category"]).one()
			newMenuItem = MenuItem(name=request.form['name'], description=request.form['description'], website=request.form['website'], image=request.form['image'], specialty_id=field.id)
			session.add(newMenuItem)
			session.commit()
			return redirect(url_for("languages", field=request.form["category"]))
		else:
			return redirect(url_for("fields"))
	else:
		return render_template('latestNew.html', categories=fields)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)