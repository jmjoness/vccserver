import os

class Config:
	FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
	DEBUG = False
	SSL_REDIRECT = False

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True

config = {
	'development': DevelopmentConfig,
}

