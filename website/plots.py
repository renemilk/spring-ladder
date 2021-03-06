#!/usr/bin/env python
from datetime import timedelta,datetime,date,time
import os
import matplotlib 
matplotlib.use('Agg')#must stay here for matplotlib to function w/o DISPLAY set
import matplotlib.pyplot as plt
from threading import Lock

from globe import config, cache, db, mkdir_p
from db_entities import Match,Player,Result

mutex = Lock()
fail_offset = timedelta(days=363)

@cache.cache('matches_per_ladder',expire=3600)
def matches_per_ladder( ladderid ):
	print 'not cached: matches_per_ladder( %s )'% ladderid
	s = db.session()
	inc = timedelta(days=1)
	today = datetime.combine(date.today(), time.min ) #datetime( now.year, now.month, now.day )
	since = today - timedelta(days=7) - fail_offset
	now = since
	data = []
	i = 1
	while now < datetime.now() - fail_offset:
		data.append( s.query( Match.id ).filter( Match.ladder_id == ladderid).filter( Match.date < now + inc ).filter( Match.date >= now ).count() )
		i += 1
		now += inc
	fn = 'images/plots/ladder_matches_%i.png'%int(ladderid)
	path = os.path.join(config.get('ladder','base_dir'), fn)
	url = '%s/%s'%(config.get('ladder','base_url'), fn)
	mkdir_p(path)
	with mutex:
		f = plt.figure(1)
		plt.plot(range(len(data)),data)
		plt.ylabel('matches per day')
		plt.xlabel('days past')
		plt.savefig(path,transparent=True)
		plt.close(1)
	s.close()
	return url
	
@cache.cache('matches_per_player',expire=3600)
def matches_per_player( playerid ):
	print 'not cached: matches_per_player( %s )'% playerid
	s = db.session()
	inc = timedelta(days=1)
	today = datetime.combine(date.today(), time.min ) #datetime( now.year, now.month, now.day )
	since = today - timedelta(days=7) - fail_offset
	now = since
	data = []
	i = 1
	while now < datetime.now() - fail_offset:
		data.append( s.query( Result.id ).filter( Result.player_id == playerid).filter( Result.date < now + inc ).filter( Result.date >= now ).count() )
		i += 1
		now += inc
	fn = 'images/plots/player_matches_%i.png'%int(playerid)
	path = os.path.join(config.get('ladder','base_dir'), fn)
	url = '%s/%s'%(config.get('ladder','base_url'), fn)
	mkdir_p(path)
	with mutex:
		f = plt.figure(1)
		plt.plot(range(len(data)),data)
		plt.ylabel('matches per day')
		plt.xlabel('days past')
		plt.savefig(path,transparent=True)
		plt.close(1)
	s.close()
	return url
