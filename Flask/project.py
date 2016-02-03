from flask import Flask, render_template, request, redirect, url_for,flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__, template_folder="templates")

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Making an API Endpoint (GET Request)
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def resMenuJSON(restaurant_id):
    res = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuJSON(restaurant_id, menu_id):
    items = session.query(MenuItem).filter_by(id=menu_id).one()
    if items:
        return jsonify(Item=items.serialize)

@app.route('/')
@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html',restaurant=restaurant, items=items)

# Task 1: Create route for newMenuItem function here

@app.route('/restaurant/add/<int:restaurant_id>', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method =='POST':
        newItem = MenuItem(name = request.form['res_name'], restaurant_id= restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('new_menu.html', restaurant_id=restaurant_id)
# Task 2: Create route for editMenuItem function here

@app.route('/restaurant/edit/<int:restaurant_id>/<int:menu_id>', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method =='POST':
        if request.form['menu_name']:
            item.name = request.form['menu_name']
            session.commit()
            flash("Edit menu %s !" % request.form['menu_name'])
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        item = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('edit_menu.html', restaurant_id=restaurant_id, menu_id=menu_id, menu_name=item.name)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurant/delete/<int:restaurant_id>/<int:menu_id>', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method =='POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('delete_menu.html', i=item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

