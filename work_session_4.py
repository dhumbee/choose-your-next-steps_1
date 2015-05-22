import os
import cgi
import urllib

import jinja2

import webapp2
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(autoescape=True, loader = jinja2.FileSystemLoader(template_dir))

#This general handler code sets up for the jinja template
class myHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **params):
		template = jinja_env.get_template(template)
		return template.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template,**kw))


#Main page class is for all items on the Home page
class MainPage(myHandler):
	def get(self):
#The first item in each list is the clickable toggle button, the second is the description		
		template_values={
			'title': 'Intro To {{Programming}}',
				}

		self.render ("webpage_html.html", **template_values)#this will render the html page and template values

#The codepen class is for the navigation link to see the embedded codepen page, previous template value needs to be carried over to each page
class codepenHandler(myHandler):
	def get(self):
		template_values={
			'title': 'Intro To {{Programming}}',
				}

		self.render ("codepen.html", **template_values)

#This code identifies the name of the wall
DEFAULT_WALL='Public'
def wall_key(wall_name=DEFAULT_WALL):
	return ndb.Key('Wall', wall_name)

#This Post class sets up the model for my datastore
class Post(ndb.Model):
	guest_name=ndb.StringProperty(indexed=False)	
	guest_message=ndb.StringProperty(indexed=False)
	date=ndb.DateTimeProperty(auto_now_add=True)

class guestbookHandler(myHandler):
	def get(self):
		wall_name = self.request.get('wall_name',DEFAULT_WALL)
		if wall_name == DEFAULT_WALL.lower(): wall_name = DEFAULT_WALL
		guest_name=self.request.get_all("guest_name")
		guest_message=self.request.get_all("guest_message")
		posts_query = Post.query(ancestor = wall_key(wall_name)).order(-Post.date)
		posts=posts_query.fetch(50)

		template_values={
		'title': 'Intro To {{Programming}}',
		'posts': posts,}

		self.render ("guestbook.html", **template_values)

	def post(self):
		wall_name = self.request.get('wall_name',DEFAULT_WALL)
		post = Post(parent=wall_key(wall_name))

		guest_name = self.request.get('guest_name')
		guest_message = self.request.get('guest_message')

		if type(guest_name) != unicode:
			post.guest_name != unicode(self.request.get('guest_name'))
		else:
			post.guest_name = self.request.get('guest_name')

		if type(guest_message) != unicode:
			post.guest_message = unicode(self.request.get('guest_message'),'utf-8')
		else:
			post.guest_message = self.request.get('guest_message')

		

		post.put()#writes to the datastore
		query_params = {'wall_name': wall_name}
		self.redirect('/guestbook.html?' + urllib.urlencode(query_params))


application=webapp2.WSGIApplication([('/', MainPage),
	('/codepen.html', codepenHandler),
	('/guestbook.html', guestbookHandler)
	])
