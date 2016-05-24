from flask import Flask, render_template, url_for, request, redirect, flash,jsonify
from database import Base, Catalog, Item, User
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random, string

#gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from datetime import datetime
#from pprint import pprint

CLIENT_ID = json.loads(
    open('client_secret.json','r').read())['web']['client_id']

app = Flask(__name__, template_folder="templates")

engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

LATEST_ITEM_NUM = 10

@app.route('/catalog/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/')
@app.route('/catalog')
def showCatalogs():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    latest_items = session.query(Item).order_by(desc(Item.create_time)).limit(LATEST_ITEM_NUM)
    return render_template('catalogs.html', catalogs=catalogs, latest_items=latest_items)

@app.route('/catalog/new', methods=['GET','POST'])
def newItem():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        catalog_id = session.query(Catalog).filter_by(name=request.form['catalog']).one().id
        newItem = Item(name=request.form['name'], description=request.form['description'], catalog_id=catalog_id, user_id=login_session['user_id'], create_time=datetime.now())
        session.add(newItem)
        flash('New Item %s Successfully Creadted' % newItem.name)
        session.commit()
        return redirect(url_for('showCatalogs'))
    else:
        catalogs = session.query(Catalog).all()
        return render_template('newItem.html', catalogs=catalogs)

@app.route('/catalog/<string:catalog_name>/<string:item_name>/edit', methods=['GET','POST'])
def editItem(catalog_name, item_name):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    catalog_id = session.query(Catalog).filter_by(name=catalog_name).one().id
    item = session.query(Item).filter_by(name=item_name).filter_by(catalog_id=catalog_id).one()
    if item.user_id == None or login_session['user_id'] != item.user_id:
        flash('Sorry, you have no permission to edit %s. ' % item_name)
        return redirect(url_for('showOneItem', catalog_name=catalog_name, item_name=item_name))
    if request.method == 'POST':
        pprint(request.form)
        if request.form['item_name']:
            item.name = request.form['item_name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['item_catalog']:
            item.catalog_id = session.query(Catalog).filter_by(name=request.form['item_catalog']).one().id
        session.commit()
        flash("Edit item %s " % item.name)
        return redirect(url_for('showOneItem', catalog_name=item.catalog.name, item_name=item.name))
    else:
        catalogs = session.query(Catalog).all()
        return render_template('editItem.html', catalogs=catalogs, item=item)

@app.route('/catalog/<string:catalog_name>/<string:item_name>/delete', methods=['GET','POST'])
def deleteItem(catalog_name, item_name):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    catalog_id = session.query(Catalog).filter_by(name=catalog_name).one().id
    item = session.query(Item).filter_by(name=item_name).filter_by(catalog_id=catalog_id).one()
    if item.user_id == None or login_session['user_id'] != item.user_id:
        flash('Sorry, you have no permission to delete %s. ' % item_name)
        return redirect(url_for('showOneItem', catalog_name=catalog_name, item_name=item_name))
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showItems', catalog_name=catalog_name))
    else:
        return render_template('deleteItem.html', item=item)   

@app.route('/catalog/<string:catalog_name>/items')
def showItems(catalog_name):
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    #print "catalog: " + catalog.name
    items = session.query(Item).filter_by(catalog_id=catalog.id).order_by(asc(Item.name))
    return render_template('items.html', catalogs=catalogs, items=items)

@app.route('/catalog/<string:catalog_name>/<string:item_name>')
def showOneItem(catalog_name, item_name):
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    item = session.query(Item).filter_by(catalog_id=catalog.id).filter_by(name=item_name).one()
    return render_template('item.html', item=item)

@app.route('/catalog.json')
def catalogsJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(Catalogs=[c.serialize for c in catalogs])

@app.route('/catalog/<string:catalog_name>.json')
def itemsJSON(catalog_name):
    catalog_id = session.query(Catalog).filter_by(name=catalog_name).one().id
    items = session.query(Item).filter_by(catalog_id=catalog_id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response=make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type']='application/json'
        return response
    code = request.data
    try:
        oauth_flow=flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri='postmessage'
        credentials=oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response=make_response(json.dumps('Failed to upgrad the authorization code.'),401)
        response.headers['Content-Type']='application/json'
        return response
    #check that the access token is valid
    access_token=credentials.access_token
    url=('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    #If there was an error in the access token info, abort
    if result.get('error') is not None:
        response=make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Verify that the accsee token is used for the intended user
    gplus_id=credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response=make_response(json.dumps("Token's user id doesn't match given user" ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response=make_response(json.dumps("Token's client id does not match app's"),401)
        print "Token's client id dose not match app's"
        response.headers['Content-Type'] = 'application/json'
        return response
    #Check to see if user is already logged in
    stored_credentials =login_session.get('credentials')
    stored_gplus_id=login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response=make_response(json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'    
        return response  
    #Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    #get user info
    userinfo_url="https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token,'alt':'json'}
    answer= requests.get(userinfo_url, params=params)
    data=json.loads(answer.text)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if user exists, if it doesn't exist make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output =''
    output +='<h1>Welcome,'
    output +=login_session['username']
    output +='!</h1>'
    output +='<img src="'
    output +=login_session['picture']
    output +=' "style="width:300px; height:300px; border-radius:150px;-webkit-border-radius:150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    return output

@app.route("/gdisconnect")
def gdisconnect():
    #only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user is not connected'),401)
        response.headers['Content-Type']='application/json'
        return response
    access_token= credentials.access_token
    url='https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token  
    h=httplib2.Http()
    result = h.request(url,'GET')[0]
    if result['status']=='200':
        #reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response=make_response(json.dumps('Successfully disconnect'),200)
        response.headers['Content-Type']='application/json'
        return response
    else:
        response=make_response(json.dumps('Failed to revoke token for given user.'),400)
        response.headers['Content-Type']='application/json'
        return response

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except Exception as e:
        print "Unexpected error: %s" % e
        return None

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.debug = False
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0', port=8000)    