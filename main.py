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
@app.route("/fields")
def fields():
	fields = session.query(Fields).all()
	return render_template('fields.html', fields = fields)

@app.route("/fields/<field>")
def languages(field):
	print(field)
	field = session.query(Fields).filter_by(name=field).first()
	languages = session.query(MenuItem).filter_by(specialty_id=field.id).all()
	return render_template('menu.html', field = field, languages = languages)

@app.route("/fields/new", methods=['GET', 'POST'])
def newField():
	if(request.method == 'POST'):
		newField = Fields(name=request.form['name'])
		session.add(newField)
		session.commit()
		return redirect(url_for('fields'))
	else:
		return render_template('newField.html')

@app.route("/fields/<field>/edit", methods=['GET', 'POST'])
def editField(field):
	field = session.query(Fields).filter_by(name=field).first()
	if(request.method == 'POST'):
		field.name = request.form['name']
		return redirect(url_for('fields'))
	else:
		return render_template('editField.html', field=field)

@app.route("/fields/<field>/delete", methods=['GET', 'POST'])
def deleteField(field):
	if(request.method == 'POST'):
		choice = request.form['choice']
		if(choice == "Yes"):
			fieldToBeDeleted = session.query(Fields).filter_by(name=field).one()
			session.delete(fieldToBeDeleted)
			session.commit()
			return redirect(url_for('fields'))
		else:
			return redirect(url_for('fields'))
	else:
		return render_template('deleteField.html', name=field)

@app.route("/fields/<field>/new", methods=['GET', 'POST'])
def newMenuItem(field):
	print(field)
	currentfield = session.query(Fields).filter_by(name=field).first()
	if(request.method == 'POST'):
		newMenuItem = MenuItem(name=request.form['name'], description=request.form['description'], website=request.form['website'], image=request.form['image'], specialty_id=currentfield.id)
		print(newMenuItem.name)
		print(newMenuItem.image)
		session.add(newMenuItem)
		session.commit()
		return redirect(url_for('languages', field = currentfield.name))
	else:
		return render_template('newMenuItem.html', field = currentfield.name)

@app.route("/fields/<field>/<menuitem>/edit", methods=['GET', 'POST'])
def editMenuItem(field, menuitem):
	

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)