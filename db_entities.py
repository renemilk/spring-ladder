# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
import datetime
import hashlib
import trueskill
import os

Base = declarative_base()

class Roles:
	"""need to be strongly ordered integers"""
	GlobalBanned= -1 #special role mapped in Bans class, not Player
	Banned 		= 0 #special role mapped in Bans class, not Player
	Unknown		= 1
	User		= 2
	Verified	= 3
	LadderAdmin	= 4 #special role mapped in ladderoptions, not Player class
	GlobalAdmin	= 5
	Owner		= 42

class Ladder(Base):
	__tablename__ 	= 'ladders'
	id 				= Column( Integer, primary_key=True,index=True )
	name 			= Column( String(100) )
	description 	= Column( Text )
	min_team_size 	= Column( Integer )
	max_team_size 	= Column( Integer )
	min_ally_size 	= Column( Integer )
	max_ally_size 	= Column( Integer )
	min_ally_count 	= Column( Integer )
	max_ally_count 	= Column( Integer )
	min_team_count 	= Column( Integer )
	max_team_count 	= Column( Integer )
	min_ai_count	= Column( Integer )
	max_ai_count	= Column( Integer )
	ranking_algo_id	= Column( String(30) )
	match_average_sum = Column( Integer )
	match_average_count = Column( Integer )

	options = relation( 'Option', order_by='Option.key' )

	def __init__(self, name="noname"):
		self.name = name
		self.min_team_size 	= 1
		self.max_team_size 	= 1
		self.min_ally_size 	= 1
		self.max_ally_size 	= 1
		self.min_ally_count = 2
		self.max_ally_count = 2
		self.min_team_count = 2
		self.max_team_count = 2
		self.min_ai_count	= 0
		self.max_ai_count	= 0
		self.match_average_sum = 0
		self.match_average_count  = 0

	def __str__(self):
		try:
			return "Ladder(id:%d) %s\n\tteam-size (%d/%d)\n\tally-size (%d/%d)\n\tteam-count (%d/%d)\n\tally-count (%d/%d)"%\
				(self.id,self.name,self.min_team_size,self.max_team_size,self.min_ally_size,self.max_ally_size,self.min_team_count,self.max_team_count,self.min_ally_count,self.max_ally_count)
		except Exception:
			return "invalid ladder"


class Option(Base):
	__tablename__ 	= 'options'
	id 				= Column( Integer, primary_key=True )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ),index=True )
	key 			= Column( String(100) )
	value 			= Column( String(100) )
	is_whitelist 	= Column( Boolean )

	adminkey		= 'ladderadmin'

	def __init__(self,key='defaultkey',value='emptyvalue',is_whitelist=True):
		self.key = key
		self.value = value
		self.is_whitelist = is_whitelist

	def __str__(self):
		return "Option(id:%d) %s -> %s (%s)"%(self.id,self.key, self.value, "wl" if self.is_whitelist else "bl")

class Player(Base):
	__tablename__ 	= 'players'
	id 				= Column( Integer, primary_key=True )
	server_id		= Column( Integer, index=True )
	nick 			= Column( String(50),index=True )
	pwhash 			= Column( String(80) )
	role			= Column( Integer )
	do_hide_results = Column( Boolean )

	def __init__(self, nick='noname', role=Roles.User, pw=''):
		self.nick 		= nick
		self.role 		= role
		self.do_hide_results = False
		self.server_id		= -1
	def __str__(self):
		return "Player(id:%d,server_id:%d) %s "%(self.id, self.server_id, self.nick)

	def validate( self, password ):
		if self.pwhash == '':
			return False
		return self.pwhash == hashlib.sha224(password).hexdigest()

	def SetPassword( self, password ):
		self.pwhash = hashlib.sha224(password).hexdigest()
		
class Map(Base):
	__tablename__	= 'maps'
	name	= Column( String(100), primary_key=True )
	md5 = Column( String(32) )
	minimap = Column( String(256) )
	startpos = Column(PickleType())
	height = Column( Integer )
	width = Column( Integer )
	
	def basedir(self,config):
		return os.path.join( config.get('ladder','base_dir'), 'images',
									'minimaps')
class Match(Base):
	__tablename__ 	= 'matches'
	id 				= Column( Integer, primary_key=True )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ),index=True )
	date 			= Column( DateTime )
	modname 		= Column( String( 60 ) )
	replay 			= Column( String( 200 ) )
	duration 		= Column( Interval )
	last_frame		= Column( Integer )

	settings    	= relation("MatchSetting", 	order_by="MatchSetting.key" )#, backref="match" )#this would auto-create a relation in MatchSetting too
	results			= relation("Result", 		order_by="Result.died" )
	ladder			= relation("Ladder" )

	mapname 		= Column( String(100), ForeignKey( Map.name ))
	map = relation(Map, primaryjoin=mapname == Map.name)


class MatchSetting(Base):
	__tablename__ 	= 'matchsettings'
	id 				= Column( Integer, primary_key=True )
	key 			= Column( String(40) )
	value 			= Column( String(80) )
	match_id 		= Column( Integer, ForeignKey( Match.id ),index=True )

class Result(Base):
	__tablename__ 	= 'results'
	id 				= Column( Integer, primary_key=True )
	player_id 		= Column( Integer, ForeignKey( Player.id ) )
	match_id 		= Column( Integer, ForeignKey( Match.id ) )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ),index=True )
	date 			= Column( DateTime )
	team			= Column( Integer )
	ally			= Column( Integer )
	disconnect		= Column( Integer )
	quit			= Column( Boolean )
	died			= Column( Integer )
	desync			= Column( Integer )
	timeout			= Column( Boolean )
	kicked			= Column( Boolean )
	connected		= Column( Boolean )

	player			= relation(Player)
	match			= relation(Match)

	def __init__(self):
		self.team 		= -1
		self.disconnect = -1
		self.ally		= -1
		self.died		= -1
		self.desync		= -1
		self.timeout	= False
		self.connected	= False
		self.quit		= False
		self.kicked		= False

	def __cmp__(self,other):
		assert isinstance(other,Result)
		valuetocompare1 = -1
		valuetocompare2 = -1
		if self.disconnect < self.match.last_frame and self.quit:
			valuetocompare1 = self.disconnect
		if other.disconnect < self.match.last_frame and other.quit:
			valuetocompare2 = other.disconnect
		if self.quit != -1 and self.quit < self.match.last_frame:
			valuetocompare1 = self.quit
		if other.quit != -1 and other.quit < self.match.last_frame:
			valuetocompare2 = other.quit
		if other.kicked or self.kicked:
			return 0
		return valuetocompare1 < valuetocompare2
	
	def __str__(self):
		try:
			return 'Result: %s team(%d) died(%d) quit(%d) '%(self.player.nick,
						self.team,self.died,self.quit)
		except:
			return'Result: team(%s) died(%d) quit(%d) '%(
						self.team,self.died,self.quit)

class Bans(Base):
	__tablename__	= 'bans'
	id 				= Column( Integer, primary_key=True )
	player_id 		= Column( Integer, ForeignKey( Player.id ) )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ) )
	end				= Column( DateTime )

	player			= relation("Player")
	ladder			= relation('Ladder')

	def __str__(self):
		if self.ladder_id != -1:
			ret = '%s on Ladder %s: %s remaining'%( self.player.nick,
							self.ladder.name,str(self.end - datetime.datetime.now() ) )
		else:
			ret = '%s (global ban): %s remaining'%( self.player.nick,
							str(self.end - datetime.datetime.now() ) )
		return ret


"""this does not actually work, but should only show what's min for new tables
class IRanks(Base):
	id 				= Column( Integer, primary_key=True )
	player_id 		= Column( Integer, ForeignKey( Player.id ) )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ) )
	def compare(otherRank): return -1,0,1
"""
class SimpleRanks(Base):
	__tablename__	= 'simpleranks'
	id 				= Column( Integer, primary_key=True )
	player_id 		= Column( Integer, ForeignKey( Player.id ) )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ),index=True )
	points			= Column( Integer )

	def __init__(self):
		self.points = 0

	player			= relation("Player")

	def __str__(self):
		return '%d points'%self.points

	def compare(self,otherRank):
		if otherRank:
			return cmp( self.points, otherRank.points )
		else:
			return 1
			
class GlickoRanks(Base):
	__tablename__	= 'glickoranks'
	id 				= Column( Integer, primary_key=True )
	player_id 		= Column( Integer, ForeignKey( Player.id ) )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ),index=True )
	rating			= Column( Float )
	rd				= Column( Float )

	def __init__(self):
		self.rating = 1500
		self.rd		=  350

	player			= relation("Player")

	def __str__(self):
		return '%f/%f (rating/rating deviation)'%(self.rating,self.rd)

	def compare(self,otherRank):
		if otherRank:
			return cmp( self.rating, otherRank.rating )
		else:
			return 1

class TrueskillRanks(Base):
	__tablename__	= 'trueskillranks'
	id 				= Column( Integer, primary_key=True )
	player_id 		= Column( Integer, ForeignKey( Player.id ) )
	ladder_id 		= Column( Integer, ForeignKey( Ladder.id ),index=True )
	mu				= Column( Float )
	sigma			= Column( Float )
	
	player			= relation("Player")

	def __init__(self):
		self.mu		= 25.0
		self.sigma	= 25.0/3.0
		#this is just a dummy that's used when updating rank from a match result
		self.rank = -666

	def combined(self):
		return self.mu - 3*self.sigma
		
	def _setRating(self,rating):
		self.mu 	= rating.mu
		self.sigma 	= rating.sigma
		
	def _getRating(self):
		return trueskill.Rating(self.mu,self.sigma)
		
	rating = property(_getRating,_setRating)

	def __str__(self):
		return '%f (%f|%f)'%(self.combined(),self.mu,self.sigma)

	def compare(self,otherRank):
		if otherRank:
			return cmp( self.combined(), otherRank.combined() )
		else:
			return 1

class Config(Base):
	__tablename__	= 'config'
	dbrevision		= Column( Integer, primary_key=True )

	def __init__(self):
		self.dbrevision = 1
