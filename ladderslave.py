# -*- coding: utf-8 -*-
from colors import *
from ParseConfig import *
import commands
import thread
import signal
import os
import time
import udpinterface
import subprocess
import traceback
import platform
import sys

if platform.system() == "Windows":
	import win32api
	
from utilities import *

def log(message):
	print green + message + normal
	
def saybattle(socket,battleid,message):
	try:
		print orange+"Battle:%i, Message: %s" %(battleid,message) + normal
		s.send("SAYBATTLE %s\n" % message)
	except:
		pass
		
def saybattleex(socket,battleid,message):
	try:
		print pink+"Battle:%i, Message: %s" %(battleid,message) + normal
		s.send("SAYBATTLEEX %s\n" % message)
	except:
		pass
	 	
class Main:
	sock = 0
	battleowner = ""
	battleid = -1
	script = ""
	ingame = 0
	gamestarted = 0
	ladderid = -1
	scriptbasepath = os.environ['HOME']
	battleusers = dict()
	battleoptions = dict()
	ladderlist = dict()
	
	def gs(self):# Game started
		self.gamestarted = 1
		
	def startspring(self,socket,g):
		cwd = os.getcwd()
		try:
			self.gamestarted = 0
			self.u.reset()
			if self.ingame == 1:
				saybattle(socket, battleid, "Error: game is already running")
				return
			self.output = ""
			self.ingame = 1
			if self.ladderid == -1 and self.checkvalidsetup():
				saybattleex(socket, battleid, "won't submit to the ladder the score results")
			else:
				saybattleex(socket, battleid, "is gonna submit to the ladder the score results")
			socket.send("MYSTATUS 1\n")
			st = time.time()
			if platform.system() == "Linux":
				log("*** Starting spring: command line \"%s\"" % (self.app.config["springdedpath"]+" "+os.path.join(os.environ['HOME'],"%f.txt" % g )))
				self.pr = subprocess.Popen((self.app.config["springdedpath"],os.path.join(os.environ['HOME'],"%f.txt" % g )),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			else:
				log("*** Starting spring: command line \"%s\"" % (self.app.config["springdedpath"]+" "+os.path.join(os.environ['USERPROFILE'],"%f.txt" % g )))
				os.chdir("\\".join(self.app.config["springdedpath"].replace("/","\\").split("\\")[:self.app.config["springdedpath"].replace("/","\\").count("\\")]))
				self.pr = subprocess.Popen((self.app.config["springdedpath"],os.path.join(os.environ['USERPROFILE'],"%f.txt" % g )),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			l = self.pr.stdout.readline()
			while len(l) > 0:
				self.output += l
				l = self.pr.stdout.readline()
			status = self.pr.wait()
			log("*** Spring has exited with status %i" % status )
			et = time.time()
			if status != 0:
				saybattle(socket,self.battleid,"Error: Spring Exited with status %i" % status)
				g = self.output.split("\n")
				for h in g:
					log("*** STDOUT+STDERR: "+h)
					time.sleep(float(len(h))/900.0+0.05)
			socket.send("MYSTATUS 0\n")
			if True:
				saybattle("has submitted ladder score updates")
		except:
			exc = traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
			loge(socket,"*** EXCEPTION: BEGIN")
			for line in exc:
				loge(socket,line)
			loge(socket,"*** EXCEPTION: END")
			os.chdir(cwd)
		os.chdir(cwd)
		self.ingame = 0
		self.gamestarted = 0
		
	def KillBot(self):
		if platform.system() == "Windows":
			handle = win32api.OpenProcess(1, 0, os.getpid())
			win32api.TerminateProcess(handle, 0)
		else:
			os.kill(os.getpid(),signal.SIGKILL)
			
	def CheckValidSetup( self, ladderid, echofailures ):
		return self.CheckvalidPlayerSetup(ladderid,echofailures) and self.CheckValidOptionsSetup(ladderid,echofailures)
		
	def CheckvalidPlayerSetup( self,ladderid , echofailures ):
		if self.ladderid == -1:
			return True
			
	def CheckValidOptionsSetup( self, ladderid, echofailures ):
		if self.ladderid == -1:
			return True
			
	def CheckOptionOk( self, ladderid, keyname, value ):
		if self.db.GetOptionKeyValueExists( self.ladderid, False, key, value ): # option in the blacklist
			return False
		if self.db.GetOptionKeyExists( self.ladderid, True, keyname ): # whitelist not empty
			return self.db.GetOptionKeyValueExists( self.ladderid, True, key, value )
		else:
			return True
			
	def onload(self,tasc):
		self.app = tasc.main
		self.hosttime = time.time()
		self.battleid = int(self.app.config["battleid"])
		self.ladderid = int(self.app.config["ladderid"])
		
	def oncommandfromserver(self,command,args,s):
		#print "From server: %s | Args : %s" % (command,str(args))
		self.sock = s
		if command == "JOINBATTLE":
			pass
		if command == "JOINBATTLEFAILED":
			error( "Join battle failed, ID: " + str(self.battleid) + " reason: " + " ".join(args[0:] )
			self.killbot()
		if command == "SETSCRIPTTAGS":
			for option in args:
				pieces = parselist( option, "=" )
				if len(pieces) != 2:
					error( "parsing error of option string: " + option )
				key = pieces[0]
				value = pieces[1]
				self.battleoptions[key] = value
			self.checkvalidoptionssetup()
		if command == "REQUESTBATTLESTATUS":
			socket.send("MYBATTLESTATUS \n")
		if command == "SAIDBATTLE" and len(args) > 1 and args[1].startswith("!"):
			who = args[0]
			command = args[1]
			args = args[2:]
			if command == "!checksetup":
				ladderid = self.ladderid
				if len(args) == 1 and args[0].isdigit():
					ladderid = int(args[0])
		if command == "BATTLEOPENED" and len(args) > 12 and int(args[0]) == self.battleid:
			self.battleoptions["battletype"] = args[1]
			self.battleoptions["mapname"] = args[10]
			self.battleoptions["modname"] = args[12]
		if command == "UPDATEBATTLEINFO" and len(args) > 4 and int(args[0]) == self.battleid:
			self.battleoptions["mapname"] = args[4]
			self.checkgeneraloptionssetup()
		
				if args[1] == "!startgame" and args[0] == self.battleowner:
						s.send("MYSTATUS 1\n")
						g = time.time()
						try:
							os.remove(os.path.join(self.scriptbasepath,"%f.txt" % g))
						except:
							pass
						if platform.system() == "Linux":
							f = open(os.path.join(os.environ['HOME'],"%f.txt" % g),"a")
						else:
							f = open(os.path.join(os.environ['USERPROFILE'],"%f.txt" % g),"a")
						self.script = ""
						f.write(self.script)
						f.close()
						thread.start_new_thread(self.startspring,(s,g))
			
	def onloggedin(self,socket):
		self.hosted = 0	
		if self.ingame == 1:
			socket.send("MYSTATUS 1\n")
		socket.send("JOINBATTLE " + self.battleid + "\n")
