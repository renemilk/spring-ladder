# -*- coding: utf-8 -*-

from db_entities import *

class IRanking():
	
	def Update(self,ladder_id,matchresult,db):
		raise NotImplemented

class RankingAlgoSelector:
	available_ranking_algos = ['simple']

	def __init__(self):
		self.algos = dict()
		self.algos[RankingAlgoSelector.available_ranking_algos[0]] =  SimpleRanks()

	def GetInstance(self, name ):
		if not name in RankingAlgoSelector.available_ranking_algos:
			raise ElementNotFoundException( name )
		return self.algos[name]

class SimpleRanks(IRanking):

	def Update(self,ladder_id,matchresult,db):
		#calculate order of deaths
		deaths = dict()
		scores = dict()
		session = db.sessionmaker()
		playercount = len(matchresult.players)
		for r in matchresult.players.values():
			session.add( r )
			
		for name,player in matchresult.players.iteritems():
			deaths[player.died] = name
			if player.timeout > -1:
				scores[name] = -1
			if player.disconnect > -1:
				scores[name] = -2
			if player.quit > -1:
				scores[name] = -5
			if player.desync > -1:
				scores[name] = 0
		#find last team standing
		for name in matchresult.players.values():
			if name not in deaths.values() and name not in scores.keys():
				scores[name] = playercount

		
		qu = session.query( SimpleRanks ).all()#.filter( SimpleRanks.ladder_id == ladder_id )
		for name,player in matchresult.players.iteritems():
			rank = qu.filter( SimpleRanks.player_id == player.id ).first()
			rank.points += scores[name]
			session.add(rank)
			#must i commit everytime?
			session.commit()
		session.close()
			


GlobalRankingAlgoSelector = RankingAlgoSelector()

#team			= Column( Integer )
#ally			= Column( Integer )
#disconnect		= Column( Integer )
#quit			= Column( Integer )
#died			= Column( Integer )
#desync			= Column( Integer )
#timeout			= Column( Integer )
#connected		= Column( Boolean )