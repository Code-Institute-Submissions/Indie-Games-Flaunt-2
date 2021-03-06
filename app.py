from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo

#for accessing the databse uri from Heroku
import os

#ObjectId to cast identifiers to the correct format for Mongo
from bson.objectid import ObjectId

#needed for implementation of random game feature
from random import randint

app = Flask(__name__)

#connect to the database using heroku env variable
app.config["MONGO_DBNAME"] = "IGF_DB"
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

#make an instance of PyMongo and pass the app in
mongo = PyMongo(app)

#get a list of all the games currently in the database
@app.route("/")

#load the home page along with a cursor containing all games currently in the database
@app.route("/get_games")
def get_games():
    return render_template("games.html", games = mongo.db.IGF_COLL.find())

#opens share game page. This page allows users to share information on a game
#the information input here is uploaded to the database
@app.route("/share_game")
def share_game():
    return render_template("share.html", games = mongo.db.IGF_COLL.find())

#opens a page containing all games in the 'action' category
@app.route("/action")
def action():
    return render_template("action.html", games = mongo.db.IGF_COLL.find())

#opens a page containing all games in the 'sports' category
@app.route("/sports")
def sports():
    return render_template("sports.html", games = mongo.db.IGF_COLL.find())

#opens a page containing all games in the 'educational' category
@app.route("/educational")
def educational():
    return render_template("educational.html", games = mongo.db.IGF_COLL.find())

#opens a page containing all games in the 'puzzle' category
@app.route("/puzzle")
def puzzle():
    return render_template("puzzle.html", games = mongo.db.IGF_COLL.find())

#open up the dedicated game page (page that features all of the information on one particular game)
#'gameId' is passed from games.html, the database is searched to find this game and its '_id' attribute is
#then passed to "dedicated.html"
@app.route("/dedicated")
def dedicated():
    gameId = request.args.get('gameId', None)
    return render_template("dedicated.html", game=mongo.db.IGF_COLL.find_one({ '_id': ObjectId(gameId) }))

#Allows users to edit a game that is already in the database
#User clicks a button on the games page, this action passes the games "_id" attribute here
#"_id" is then passed to the variable "gameId. The database is then searched  for this game
@app.route("/edit")
def edit():
    gameId=request.args.get('gameId', None)
    return render_template("edit.html", game=mongo.db.IGF_COLL.find_one({ '_id': ObjectId(gameId) }))

#Takes the modified database fields 'title', 'genre', 'developer', 'link',
#'shortDescription', 'description', 'screenshot1', 'screenshot2', 'screenshot3'
#that are passed from the 'edit' page and inserts them back into the database
#uses the MongoDB method update()
@app.route('/update_game', methods=["POST"])
def update_game():
    gameId=request.args.get('gameId', None)
    games = mongo.db.IGF_COLL
    games.update( {'_id': ObjectId(gameId)},
    {
        'title':request.form.get('title'),
        'genre':request.form.get('genre'),
        'developer':request.form.get('developer'),
        'link': request.form.get('link'),
        'shortDescription':request.form.get('shortDescription'),
        'description':request.form.get('description'),
        'screenshot1':request.form.get('screenshot1'),
        'screenshot2':request.form.get('screenshot2'),
        'screenshot3':request.form.get('screenshot3')
    })
    return redirect(url_for('get_games'))

#When the user clicks delete on a games page, the games "_id" attribute is
#passed here into the gameId variable. The MongoDB function remove() uses the
#remove() function with the gameId as the argument. This completely removes the
#specified data from the database.
@app.route("/delete_game")
def delete_game():
    gameId=request.args.get("gameId", None)
    mongo.db.IGF_COLL.remove({ "_id": ObjectId(gameId) })
    return redirect(url_for("get_games"))

#Takes the form input from 'share' page and uses the inser_one()
#method to put the data into the database. The data is inserted in the form of
#a document with a unique '_id' attribute. The user is then redirected to the home page.
@app.route("/add_game", methods=["POST"])
def add_game():
    games=mongo.db.IGF_COLL
    games.insert_one(request.form.to_dict())
    return redirect(url_for('get_games'))

#The home page features a button where the user can be directed to information about a
#randomly selected game.
@app.route("/random_game")
def random_game():
    #generate a random number between 0 and the number of documents in the database
    #subtract 1 from the number of documents to prevent index bounds issues
    random_number = randint(0, (mongo.db.IGF_COLL.count() - 1))

    #use this random number to pick one game from the database
    selected_game=mongo.db.IGF_COLL.find()[random_number]

    #use the selected games _id attribute to redirect the user to that games page
    return render_template("dedicated.html", game=mongo.db.IGF_COLL.find_one({ '_id': ObjectId(selected_game["_id"]) }))