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
	field = session.query(Fields).filter_by(name=field).one()
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
	field = session.query(Fields).filter_by(name=field).one()
	if(request.method == 'POST'):
		field.name = request.form['name']
		return redirect(url_for('fields'))
	else:
		return render_template('editField.html', field=field)
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)