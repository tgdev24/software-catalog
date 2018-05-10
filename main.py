#!flask/bin/python
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
import random, string
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Fields, MenuItem
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('clientsecrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "software catalog app"

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/login")
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template('login.html', state=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('clientsecrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
	
@app.route("/")
@app.route("/fields/")
def fields():
	# field = session.query(MenuItem).filter_by(id=7).one()
	# session.delete(field)
	# session.commit()
	fields = session.query(Fields).all()
	latestOnes = session.query(MenuItem).order_by(desc(MenuItem.id)).limit(7).all()
	return render_template('fields.html', fields = fields, latest=latestOnes)

@app.route("/fields/<id>/")
def languages(id):
	field = session.query(Fields).filter_by(id=id).one()
	fields = session.query(Fields).all()
	languages = session.query(MenuItem).filter_by(specialty_id=field.id).all()
	return render_template('menu.html',fields=fields, field = field, languages = languages)

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

@app.route("/fields/<id>/<menu_id>/edit/", methods=['GET', 'POST'])
def editMenuItem(id, menu_id):
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
				specialty = session.query(Fields).filter_by(name=request.form['category']).first()
				editedItem.specialty_id = specialty.id
			session.add(editedItem)
			session.commit()
			return redirect(url_for('languages', id=id))
		else:
			return redirect(url_for('languages', id=id))
	else:
		categories = session.query(Fields).all()
		return render_template('editMenuItem.html', categories=categories, menuitem=editedItem)

@app.route('/fields/<id>/<menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
    	if(request.form['choice'] == 'Delete'):
        	session.delete(itemToDelete)
        	session.commit()
        	return redirect(url_for('languages', id=id))
        else:
        	return redirect(url_for('languages', id=id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)
    # return "This page is for deleting menu item %s" % menu_id

# @app.route('/fields/latestnew', methods=['GET', 'POST'])
# def latestNew():
# 	fields=session.query(Fields).all()
# 	if(request.method == 'POST'):
# 		if(request.form['choice'] == "Submit"):
# 			field = session.query(Fields).filter_by(name=request.form["category"]).first()
# 			newMenuItem = MenuItem(name=request.form['name'], description=request.form['description'], website=request.form['website'], image=request.form['image'], specialty_id=field.id)
# 			session.add(newMenuItem)
# 			session.commit()
# 			return redirect(url_for("languages", id=field.id))
# 		else:
# 			return redirect(url_for("fields"))
# 	else:
# 		return render_template('latestNew.html', categories=fields)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)