#!/usr/bin/env python
# -*- coding: utf-8 -*-

import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from mendeley import Mendeley
from mendeley.exception import MendeleyException

import config

define("port", default=9999, help="run on the given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", HomeHandler),
			(r"/ref", referenceMetaData)
		]
		settings = dict(
			debug = True,
			gzip = True,
		)
		super(Application, self).__init__(handlers, **settings)
		'''
		self.db = torndb.Connection(
			host = config.DB_HOST,
			database = config.DB_NAME,
			user = config.DB_USER,
			password = config.DB_PASS
		)
		'''

class BaseHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

class HomeHandler(BaseHandler):
	def get(self):
		d = {'name':'mencent','yeas':25}
		self.write(d)

	def put(self):
		self.write(dict(message="hello,world"))

	def delete(self):
		self.write(dict(message="hello,world"))

class referenceMetaData(BaseHandler):
	@property
	def mendeley(self):
		mendeley = Mendeley(config.MENDELEY_CLIENT_ID, client_secret=config.MENDELEY_SECRET)
		auth = mendeley.start_client_credentials_flow()
		session = auth.authenticate()
		return session

	def get(self):
		args = { k:v[0] for k,v in self.request.arguments.iteritems()}
		try:
			doc = self.mendeley.catalog.by_identifier(view='all', **args)
		except MendeleyException:
			self.write({'err': 'error'})
			return
		self.write({ f:getattr(doc, f) for f in doc.fields()})




def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()