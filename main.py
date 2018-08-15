#!flask/bin/python
from database_setup import Base, User, Fields, MenuItem
from flask import(
	Flask,
	render_template, 
	request,
	redirect, 
	url_for, 
	jsonify, 
	flash, 
	make_response,
	session as login_session)
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests

CLIENT_ID=json.loads(open(
	'client_secrets3.json',
	'r').read())['web']['client_id']
APPLICATION_NAME = "software_catalog"

app = Flask(__name__)
engine = create_engine('sqlite:///catalogwithusers.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/fields/JSON')
def fieldsJSON():
	fields = session.query(Fields).all()
	return jsonify(fields=[f.serialize for f in fields])


@app.route('/fields/<int:id>/JSON')
def languagesJSON(id):
	languages = session.query(MenuItem).filter_by(specialty_id=id).all()
	return jsonify(languages=[lang.serialize for lang in languages])


@app.route("/login")
def login():
	state = ''.join(
		random.choice(
			string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)


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
		oauth_flow = flow_from_clientsecrets('client_secrets3.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)				# noqa
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
		print("Token's client ID does not match app's.")
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(
			json.dumps('Current user is already connected.'), 200)
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
	flash("you are now logged in as %s" % login_session['username'])
	print("done!")
	return redirect(url_for('fields'))


@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session.get('access_token')
	if access_token is None:
		print('Access Token is None')
		response = make_response(
			json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	print('In gdisconnect access token is %s', access_token)
	print('User name is: ')
	print(login_session['username'])
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']			# noqa
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print('result is ')
	print(result)
	if result['status'] == '200':
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		flash("Successfully disconnected")  
		return redirect(url_for('fields'))
	else:
		response = make_response(
			json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


def createUser(login_session):
	newUser = User(
		name=login_session['username'], 
		email=login_session['email'], 
		picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id


def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user


def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None


@app.route("/")
@app.route("/fields/")
def fields():
	fields = session.query(Fields).all()
	latestOnes = session.query(MenuItem).order_by(
		desc(MenuItem.id)).limit(7).all()
	if('username' not in login_session):
		state = ''.join(
			random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		login_session['state'] = state
		return render_template(
			'publicfields.html', fields=fields, latest=latestOnes, STATE=state)
	flash('Successfully logged in.')
	return render_template('fields.html', fields=fields, latest=latestOnes)


@app.route("/fields/<int:id>/")
def languages(id):
	field = session.query(Fields).filter_by(id=id).one()
	creator = getUserInfo(field.user_id)
	fields = session.query(Fields).all()
	languages = session.query(MenuItem).filter_by(specialty_id=field.id).all()
	if(
		'username' not in login_session or 
		creator.id != login_session['user_id']):
		return render_template(
			'publicmenu.html', 
			fields=fields, 
			field=field, 
			languages=languages, 
			creator=creator)
	return render_template(
		'menu.html',
		fields=fields, 
		field=field, 
		languages=languages)


@app.route("/fields/new/", methods=['GET', 'POST'])
def newField():
	if 'username' not in login_session:
		flash("You are not authorized to add a new field.")
		return redirect('/fields')
	if(request.method == 'POST'):
		if(request.form["choice"] == "Submit"):
			# must store the user that's currently logged in
			newField = Fields(
				name=request.form['name'], 
				user_id=login_session['user_id'])
			session.add(newField)
			session.commit()
			flash("New field successfully created")
			return redirect(url_for('fields'))
		else:
			return redirect(url_for('fields'))
	else:
		return render_template('newField.html')


@app.route("/fields/<int:id>/edit/", methods=['GET', 'POST'])
def editField(id):
	field = session.query(Fields).filter_by(id=id).one()
	creator = getUserInfo(field.user_id)

	if(
		'username' not in login_session or 
		creator.id != login_session['user_id']):
		flash("You are not authorized to edit this field.")
		return redirect('/fields')
	if(request.method == 'POST'):
		if(request.form["choice"] == "Submit"):
			field.name = request.form['name']
			session.add(field)
			session.commit()
			flash("Successfully Edited")
			return redirect(url_for('fields'))
		else:
			return redirect(url_for('fields'))
	else:
		return render_template('editField.html', field=field)


@app.route("/fields/<int:id>/delete/", methods=['GET', 'POST'])
def deleteField(id):
	field = session.query(Fields).filter_by(id=id).one()
	creator = getUserInfo(field.user_id)
	if(
		'username' not in login_session or 
		creator.id != login_session['user_id']):
		flash("You are not authorized to delete this field.")
		return redirect('/fields')
	fieldToBeDeleted = session.query(Fields).filter_by(id=id).one()
	itemsToBeDeleted = session.query(MenuItem).filter_by(
		specialty_id=fieldToBeDeleted.id).all()
	if(request.method == 'POST'):
		choice = request.form['choice']
		if(choice == "Yes"):
			for i in itemsToBeDeleted:
				session.delete(i)
			session.commit()
			session.delete(fieldToBeDeleted)
			session.commit()
			flash("Successfully Deleted Field")
			return redirect(url_for('fields'))
		else:
			return redirect(url_for('fields'))
	else:
		return render_template('deleteField.html', name=fieldToBeDeleted.name)


@app.route("/fields/<int:id>/new/", methods=['GET', 'POST'])
def newMenuItem(id):
	field = session.query(Fields).filter_by(id=id).one()
	creator = getUserInfo(field.user_id)
	if(
		'username' not in login_session or 
		creator.id != login_session['user_id']):
		flash("You are not authorized to create a new field.")
		return redirect('/fields')
	currentfield = session.query(Fields).filter_by(id=id).one()
	if(request.method == 'POST'):
		if(request.form["choice"] == "Add"):
			newMenuItem = MenuItem(
				name=request.form['name'], 
				description=request.form['description'], 
				website=request.form['website'], 
				image=request.form['image'], 
				specialty_id=currentfield.id, 
				user_id=login_session['user_id'])
			session.add(newMenuItem)
			session.commit()
			flash("New menu item successfully created")
			return redirect(url_for('languages', id=currentfield.id))
		else:
			return redirect(url_for('languages', id=currentfield.id))
	else:
		return render_template('newMenuItem.html', field=currentfield.name)


@app.route("/fields/<int:id>/<int:menu_id>/edit/", methods=['GET', 'POST'])
def editMenuItem(id, menu_id):
	editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	creator = getUserInfo(editedItem.user_id)
	if(
		'username' not in login_session or 
		creator.id != login_session['user_id']):
		flash("You are not authorized to edit the menu item.")
		return redirect('/fields')
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
				specialty = session.query(
					Fields).filter_by(name=request.form['category']).first()
				editedItem.specialty_id = specialty.id
			session.add(editedItem)
			session.commit()
			flash("Successfully edited menu item")
			return redirect(url_for('languages', id=id))
		else:
			return redirect(url_for('languages', id=id))
	else:
		categories = session.query(Fields).all()
		return render_template(
			'editMenuItem.html', 
			categories=categories, 
			menuitem=editedItem)


@app.route('/fields/<int:id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(id, menu_id):
	itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
	creator = getUserInfo(itemToDelete.user_id)
	if(
		'username' not in login_session or 
		creator.id != login_session['user_id']):
		flash("You are not authorized to delete the menu item.")
		return redirect('/fields')
	if request.method == 'POST':
		if(request.form['choice'] == 'Delete'):
			session.delete(itemToDelete)
			session.commit()
			flash("Successfully deleted menu item")
			return redirect(url_for('languages', id=id))
		else:
			return redirect(url_for('languages', id=id))
	else:
		return render_template('deleteMenuItem.html', item=itemToDelete)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)