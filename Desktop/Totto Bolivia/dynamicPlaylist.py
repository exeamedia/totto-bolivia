#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import syslog
import logging 
import logging.handlers 
from random import shuffle
from random import random
from time import sleep, strftime
from datetime import datetime, date, time, timedelta

'''
This script generates a dynamic playlist from mp3 music in one folder for the SHOUTcast transcoder. Additionally, jingles are supported.

To use the script, do the following
1. change baseDirectory, musicDirectory and jinglesDirectory according to your music folder structure
2. call it from a SHOUTcast transcoder playlist in the following way:
#!/usr/bin/python /home/shoutcast/sc_trans_folder/playlists/dynamicPlaylist.py
(see also http://wiki.winamp.com/wiki/SHOUTcast_DNAS_Transcoder_2#Remote_Applications)
3. If you change music in the music or the jingle folder delete the file called 'position' in the baseDirectory to trigger the generation of a new dynamic playlist. You can, however, also wait until all songs in the current playlist have been played and afterwards a new playlist will be generated automagically.

The script basically does the following:
1. It figures out if there is a position file in the baseDirectory. If this file is there it reads the position number in this file.
1b) If the position file is not there it generates one. position number will be set to 0. Additionally, buildAndSaveRandomPlaylist() looks for all mp3s in musicDirectory and creates a shuffled dynamic playlist from all mp3s. The playlist is stored in the file 'playlist' in baseDirectory.
2. printNextSongs() parses the generated playlist and looks for the next song at position. It then prints out that song to the SHOUTcast transcoder. Additionally, the next 'length' songs will be output to allow SHOUTcast transcoder to give this information to the SHOUTcast server in order to give this information to the yp. Although this functionality is includeed in SHOUTcast transcoder's documentation, SHOUTcast transcoder does currently not support this functionality (see http://forums.winamp.com/showthread.php?p=2896457&posted=1#post2896457) If the playlist has arrived at its end, a new playlist will be generated. If the next mp3 file from the current playlist has been removed from the filesystem, a new playlist will be generated.
'''

#change base directory appropriately to your system
baseDirectory = "/home/pi/ExeaInternetRadio/"

#set directory with mp3 files
musicBaseDirectory = baseDirectory+"Musica/"
musicDirectory = ""

#if you want to include jngles every once and again put them in jingles and set the
#folder name here appropriately
jinglesBaseDirectory = baseDirectory+"Producción/"
jinglesDirectory = ""

#help files. delete position (or playlist) file to trigger the generation of a new playlist.
positionFile = baseDirectory+"position"
playlistFile = baseDirectory+"playlist"

#if SHOUTcast does not send the information how much songs should be output by printNextSongs(), numTracks songs will be output.
numTracks = 3

#if JINGLE_FACTOR is bigger than 0, then an mp3 file from the jingle folder will be included in the dynamic playlist every JINGLE_FACTOR+1 song.
JINGLE_FACTOR = 2

# Initialize log system

logger = logging.getLogger('Dynamic Playlist') 

# Max level of security for messages
# Levels are:
# DEBUG - Higher level
# INFO 
# WARNING 
# ERROR 
# CRITIAL - lower lever
logger.setLevel(logging.DEBUG) 

# If maxBytes=0, the file will not rotate by size 
# If backupCount=0, any file rotated will be deleted
handler = logging.handlers.RotatingFileHandler(filename=baseDirectory+'playlist.log', mode='a', maxBytes=1024000, backupCount=30)

# Define the formater
formatter = logging.Formatter(fmt='[%(asctime)s] %(name)s [%(levelname)s]: %(message)s',datefmt='%y-%m-%d %H:%M:%S') 
handler.setFormatter(formatter)

# Add the handler
logger.addHandler(handler) 

# Use for logging messages:
# logger.debug('message debug') 
# logger.info('message info') 
# logger.warning('message warning') 
# logger.error('message error') 
# logger.critical('message critical')

def getPlaylistFile():
	return playlistFile

def getMp3Files(files):
	return [each for each in files if each.endswith('.mp3')]

def printNextSongs(position, length):
	plf = open(playlistFile, 'r')
	entries = plf.readlines()
	
	#integrity check: figure out if next music file still exists in the music directory.
	#if has been removed, create new playlist and start again.
	nextMp3FileExists = checkIfMusicFileExists(entries[position%len(entries)][:-1])
	if not nextMp3FileExists:
		buildAndSaveRandomPlaylist()
		position = 0
	for x in range(position, position+length):
		print entries[x%len(entries)][:-1]
	if position > 0 and position%len(entries) == 0:
		#if the playlist has been played up till its end create a new playlist
		buildAndSaveRandomPlaylist()
	position = position%len(entries)
	return position

def checkIfMusicFileExists(mp3File):
	fileExists = True
	try:
		f = open(mp3File, 'r')
		f.close()
	except IOError:
		fileExists = False
	return fileExists
	
def buildAndSaveRandomPlaylist():
	getCurrentMusicDirectory()
	shuffledMusicFiles = getMp3Files(os.listdir(musicDirectory))
	shuffle(shuffledMusicFiles)
	shuffledJingles = getMp3Files(os.listdir(jinglesDirectory))
	shuffle(shuffledJingles)
	
	jingleCountdown = JINGLE_FACTOR
	try:
		playlistFileObj = open(playlistFile, 'w')
		for filename in shuffledMusicFiles:
			playlistFileObj.write(musicDirectory+filename+"\n")
			if JINGLE_FACTOR > 0 and jingleCountdown == 0:
				jingle = jinglesDirectory + shuffledJingles[int(random()*len(shuffledJingles))]
				playlistFileObj.write(jingle+"\n")
				jingleCountdown = JINGLE_FACTOR
			jingleCountdown = jingleCountdown-1
		playlistFileObj.close()
	except IOError:
		syslog.syslog("could not create or write dynamic playlist in path "+playlistFile+". Script: "+sys.argv[0]+" - param length: "+str(len(sys.argv))+", sys.argv[1]: "+sys.argv[1])

def dateInRange(initialHour, initialMinute, finalHour, finalMinute):
	initialTime = time(initialHour, initialMinute, 0)
	finalTime = time(finalHour, finalMinute, 0)
	currentDate = datetime.now()
	currentTime = time(currentDate.hour, currentDate.minute, currentDate.second)

	return (currentTime < finalTime and currentTime > initialTime)

#Get the current directory of music
def getCurrentMusicDirectory():
	global musicDirectory
	global jinglesDirectory

	print "Getting current music and jingles directory..."
	logger.info("Getting current music and jingles directory...")

	tottoMornings = ["Dance", "Funk", "Deep House Casual", "Indie Electro"]
	tottoEvening = ["Deep House", "Indie Pop", "Dance Londinense", "Electro Swing", "Electronica"]
	tottoNights = ["Remix", "Funk", "Deep House", "Electronica", "Disco"]

	jingles = ["Saludos Totto"]	
	jinglesDirectory = jinglesBaseDirectory + jingles[int(random()*len(jingles))] + "/"

	# Since 0:00 to 6:00am
	if dateInRange(22, 0, 6, 59):
		musicDirectory = musicBaseDirectory + tottoNights[int(random()*len(tottoNights))] +"/"
	elif dateInRange(7, 0, 11, 59):
		musicDirectory = musicBaseDirectory + tottoMornings[int(random()*len(tottoMornings))] +"/"
	elif dateInRange(12, 0, 16, 59):
		musicDirectory = musicBaseDirectory + tottoEvening[int(random()*len(tottoEvening))] +"/"
	elif dateInRange(17, 0, 21, 59):
		musicDirectory = musicBaseDirectory + tottoNights[int(random()*len(tottoNights))] +"/"

	print "The current music directory is: " + musicDirectory
	print "The current jingles directory is: " + jinglesDirectory
	logger.info("The current music directory is: " + musicDirectory)
	logger.info("The current jingles directory is: " + jinglesDirectory)


def generatePlaylist():
	global numTracks

	syslogMessage = sys.argv[0]
	if len(sys.argv) > 1:
		try:
			syslog.syslog(syslogMessage + " " + sys.argv[1])	
			numTracks =  int(sys.argv[1])
		except ValueError:
			syslog.syslog("Oops!  Argument 1 was not a valid number in dynamicPlaylist.py. Taking 3 songs for default.")

	# os.remove(positionFile)
	# os.remove(playlistFile)

	positionFileExists = True
	position = 0
	try:
		f = open(positionFile, 'r')
		try:
			#read position value from file
			position = int(f.read())
			position = position+1
			f.close()
		except ValueError:
			#if there is no number in the file, set position to 0
			position = 0
	except IOError:
		#if there is no position file (or if it is corrupted) generate new one
		positionFileExists = False
		position = 0
	f = open(positionFile, 'w')

	#if no position file has been found we also create a new playlist (therefore, by deleting
	#the position file you can trigger the generation of a new playlist)
	if not positionFileExists:
		buildAndSaveRandomPlaylist()

	#figure out if playlist exists
	try:
		plf = open(playlistFile, 'r')
		plf.close()
	except IOError:
		#if somehow the playlistFile has been deleted generate a new one
		buildAndSaveRandomPlaylist()

	#print out the songs coming up for SHOUTcast. the returned value position is only important
	#if the generated playlist has been played up till its end. then a 0 will be returned for
	#position. otherwise position will be returned unchanged.
	position = printNextSongs(position, numTracks)
	f.write(str(position))
	f.close()

if __name__ == '__main__':
		generatePlaylist()
	# try:
	# 	logger.info('Program finished')

	# except KeyboardInterrupt:
	# 	print "Bye!"
	# 	logger.info('Program finished by keyboard interrupt')

	# except Exception:
	# 	print Exception
	# 	logger.info('Program finished by external exception')
