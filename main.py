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

if __name__ == '__main__':
	app.debug = True
	app.run(host='localhost', port=5000)