import os
import platform
if platform.system() == "Windows":
	import win32api

from tasbot.customlog import Log

from match import AutomaticMatchToDbWrapper, UnterminatedReplayException


class ReplayReporter(object):
	def  __init__ ( self, db ):
		self.db = db

	def SubmitLadderReplay( self, replaypath, ladderid, do_validation=True ):
		try:
			if not self.db.LadderExists( ladderid ):
				Log.error( "Error: ladder %d does not exist" % ( ladderid ) )
				return False
			else:
				try:
					mr = AutomaticMatchToDbWrapper( replaypath, ladderid )
					return self.db.ReportMatch( mr, do_validation )
				except UnterminatedReplayException:
					Log.error('skipping unterminated replay %s'%replaypath, 'ReplayReporter')
				except Exception,e:
					Log.error('reporting match failed', 'ReplayReporter')
					Log.exception(e)
				return False
		except Exception, e:
			Log.exception(e)
			return False
		return True
