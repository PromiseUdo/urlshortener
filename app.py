from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import shortuuid

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname('__file__'))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(basedir, "base.db"))
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	shortid = db.Column(db.String(13))
	old_url = db.Column(db.String(4000))
	new_url = db.Column(db.String(4000))

	def __repr__(self):
		return f'<{self.old_url}>'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/link', methods=['POST'])
def link():
	if request.method == 'POST':
		urlid = shortuuid.ShortUUID().random(length=4)
		url = request.form['url']
		check_url = URL.query.filter_by(old_url=url).first()
		if check_url:
			return render_template('link.html', url=check_url.new_url, present=True)

		else:
			url_formed = 'https://urlshortener-vee.herokuapp.com/{}'.format(urlid)
			new_url = URL(old_url=url, new_url=url_formed, shortid=urlid,)
			db.session.add(new_url)
			db.session.commit()
			return render_template('link.html', url=url_formed)

	return redirect(url_for('index'))

@app.route('/<url_id>')
def url(url_id):
	check_url = URL.query.filter_by(shortid=url_id).first()
	if check_url:
		if 'http://' in check_url.old_url or 'https://' in check_url.old_url:
			return redirect(check_url.old_url)

		return redirect('https://{}'.format(check_url.old_url))
	return 'URL does not exist'



if __name__ == '__main__':
	app.run(debug=True)
