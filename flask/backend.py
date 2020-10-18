import os

import bcrypt
from flask import render_template, url_for, request, session, redirect
from pymongo import MongoClient

mongo = MongoClient(os.environ['MONGODB_HOST'], 27017)


def index():
    if 'email' not in session:
        return render_template('login.html')

    users = mongo.db.users.find({'email': {'$ne': session['email']}})
    message = 'You are logged in as {}'.format(session['email'])

    return render_template('index.html', message=message, users=users)


def register():
    message = ''
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email': request.form['email']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({
                'name': request.form['name'],
                'email': request.form['email'],
                'password': hashpass,
                'favorite': []
            })
            session['email'] = request.form['email']
            return redirect(url_for('index'))

        message = 'Email already exists!'

    return render_template('register.html', message=message)


def login():
    message = ''
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'email': request.form['email']})

        if user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), user['password']) == user['password']:
                session['email'] = request.form['email']
                return redirect(url_for('index'))

        message = 'Invalid email or password'

    return render_template('login.html', message=message)


def logout():
    session.clear()
    return render_template('login.html')


def favorite():
    if request.method == 'POST':
        fav_email = request.form['email']
        usr_email = session['email']
        res = mongo.db.users.update_one({'email': usr_email, 'favorite': {"$ne": fav_email}},
                                        {"$push": {"favorite": fav_email}})

        if res.matched_count != 0:
            tmp = '{} added you as their favorite'.format(usr_email)
            res = mongo.db.notifications.update_one({'email': fav_email}, {"$push": {"unread": tmp}})
            if not res.matched_count:
                mongo.db.notifications.insert({'email': fav_email, "unread": [tmp]})
            message = '{} added to your favorite'.format(fav_email)

        else:
            message = 'User already in your favorite'

        return render_template('index.html', message=message)

    if request.method == 'GET':
        favorites = list(mongo.db.users.aggregate([{
            "$match": {'email': session['email']}
        }, {
            "$project": {'favorite': 1}
        }, {
            "$unwind": "$favorite"
        }, {
            "$lookup": {
                "from": "users",
                "localField": "favorite",
                "foreignField": "email",
                "as": "favoriteData"
            }
        }, {
            "$unwind": "$favoriteData"
        }, {
            "$group": {
                "_id": "$_id",
                "favorite": {"$push": "$favorite"},
                "favoriteData": {"$push": "$favoriteData"}
            }
        }]))
        favorites = favorites[0] if favorites else []
        message = 'Here are your favorites'

        return render_template('favorite.html', message=message, favorites=favorites)


def fans():
    users = mongo.db.users.find({'favorite': [session['email']]})
    message = 'Here are your fans'

    return render_template('fans.html', message=message, users=users)


def notification():
    notifications = mongo.db.notifications.find_one({'email': session['email']})
    if notifications and notifications['unread']:
        mongo.db.notifications.update_one({'email': session['email']}, {
            "$set": {"unread": []},
            "$push": {"read": {"$each": notifications['unread']}}
        })

    return render_template('notifications.html', notifications=notifications)
