#session_manager.py
from foundation.session import SessionState

class SessionManager:
	"""
	The SessionManager class allows to add and remove sessions in the core system.
	"""
	def __init__(self):
		self.session_objects = {}
		self.session_objects_done = {}
	
	def add_session(self, session):
		"""
		Adding new session to the Auction system will parse and syntax
        check the given auction object specifications. 
        It lookup the database for already installed sessions 
        and store the session into the database. 
		""" 
		key = session.get_key()
		if key in self.session_objects.keys():
			raise ValueError('Session with this name is already installed')
		session.set_state(SessionState.SS_VALID)
		self.session_objects[key] = session


	def get_session(self, key):
		"""
		lookup the database of sessions for a specific session
        """ 
		if key in self.session_objects.keys():
			return self.session_objects[key]
		else:
			raise ValueError('Session {} does not exist'.format(key))

	def get_session_done(self, key):
		"""
		Get session with key from the stored mark as done.
		""" 
		if key in self.session_objects_done.keys():
			return self.session_objects_done[key]
		else:
			raise ValueError('Session {} does not exist'.format(key))

	def del_session(self, key):
		"""
		Deletes a session, parses and syntax checks the
        identification string, it tests the presence of the given session
        in the database, and it removes the session from the database
		""" 
		if key in self.session_objects.keys():
			session = self.session_objects.pop(key)
			self.store_session_as_done(session)
		else:
			raise ValueError('Session {} does not exist'.format(key))

	def store_session_as_done(self, session):
		"""
		Add the session to the list of finished sessions
		""" 
		session.set_state(SessionState.SS_DONE)
		key = session.get_key()
		self.session_objects_done[key] = session