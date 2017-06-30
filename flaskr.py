import os
import sqlite3
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash


DATABASE = '/home/chenxiang/myproject/flaskr/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory= sqlite3.Row
	return rv

def get_db():
	if not hasattr(g, 'sqlite_db'):
	    g.sqlite_db=connect_db()
	return g.sqlite_db

def init_db():
	with app.app_context():
		db=get_db()
		with app.open_resource('schema.sql',mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def close_db():
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def show_entries():
	g.db = connect_db()
	cur = g.db.execute('select title,text from entries order by id desc')
	entries = [dict(title=row[0],text=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html',entries=entries)

@app.route('/add',methods=['POST'])
def add_entry():
	g.db = connect_db()
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into entries(title,text) values(?,?)',[request.form['title'],request.form['text']])
	g.db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/login',methods=['GET','POST'])
def login():
	error = None
	if request.method=='POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You are logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html',error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in',None)
	flash('You are logged out')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
	init_db()
	app.run('10.20.6.131')