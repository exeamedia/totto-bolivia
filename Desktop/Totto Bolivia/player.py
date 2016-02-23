#!/usr/bin/python

# import lirc
import urllib2
import sys
import RPi.GPIO as GPIO
import logging 
import logging.handlers
import thread 
#from threading import Thread
from lcd import LCD
from subprocess import * 
from time import sleep, strftime
from termcolor import colored
from datetime import datetime
from dynamicPlaylist import *

# Basic commands
cmd_ip = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
cmd_play_play_1 = "mpg123 -@ /home/pi/ExeaInternetRadio/playlist -l 1"
cmd_play_play_2 = "mpg123 -@ /home/pi/ExeaInternetRadio/playlist -l 2"
cmd_play_play_3 = "mpg123 -@ /home/pi/ExeaInternetRadio/playlist -l 3"
cmd_play_play_4 = "mpg123 -@ /home/pi/ExeaInternetRadio/playlist -l 4"

#cmd_play_bkp1 = "mpg123 -z /home/pi/Music/Dias/* &"
#cmd_play_bkp2 = "mpg123 -z /home/pi/Music/Tardes/* &"
#cmd_play_bkp3 = "mpg123 -z /home/pi/Music/Noches/* &"
cmd_stop_all = "killall mpg123"
cmd_check_sound = "ps -A | grep mpg123"

# Initialize log system
	
logger = logging.getLogger('ExeaMediaPlayer') 

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
handler = logging.handlers.RotatingFileHandler(filename='/home/pi/ExeaInternetRadio/logs/player.log', mode='a', maxBytes=1024000, backupCount=30)

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

# Control for threads
#thread_finished = False
#url = ""
title = ""

#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)

# Initialize LIRC connection for IR Remote Control
# sockid = lirc.init('irremote')

def run_cmd(cmd, Output = True):
	p = Popen(cmd, shell=True, stdout=PIPE)
	p.wait()
	if Output:
		output = p.communicate()[0]
		return output
	else:
		return

def checkInternetConnection():
	try:
		urllib2.urlopen("http://www.google.com").close()
	except urllib2.URLError:
		# print "Checking Internet...\t", colored('[Warning]', 'yellow')
		logger.warning("Checking Internet... [Failed]")
		return False
	else:
		# print "Checking Internet...\t", colored('[OK]', 'green')
		logger.info("Checking Internet... [OK]")
		return True

#def dateInRange(initialHour, initialMinute, finalHour, finalMinute):
#	currentHour = hour = datetime.now().hour
#	currentMinute = datetime.now().minute
#
#	if initialHour <= currentHour and finalHour >= currentHour:
#		if currentHour == initialHour:
#			if currentMinute >= initialMinute:
#				return True
#			else:
#				return False
#		if currentHour == finalHour:
#			if currentMinute <= finalMinute:
#				return True
#			else:
#				return False
#		return True
#	else:
#		return False

def playMusic():
#	run_cmd(cmd_stop_all, False)
#	logger.info("Playing backup")
#
#	if dateInRange(00, 00, 11, 00):
#		run_cmd(cmd_play_bkp1, True)
#		return "Dias"
#	if dateInRange(11, 00, 16, 00):
#		run_cmd(cmd_play_bkp2, True)
#		return "Tardes"
#	# Music for happy hour
#	if dateInRange(16, 00, 23, 59):
#		run_cmd(cmd_play_bkp3, True)
#		return "Noches"
#
#	return

        global thread_finished
        while True:
                # print "Refreshing playlist..."
                logger.info("Refreshing playlist...")
                buildAndSaveRandomPlaylist()

                try:
                        run_cmd(cmd_play_play_4, False)
                        run_cmd(cmd_play_play_3, False)
                        run_cmd(cmd_play_play_2, False)
                        run_cmd(cmd_play_play_1, False)

                except Exception:
                        print "Se ha producido un error al reproducir el archivo\nReintentando..."
                        # logger.error("Se ha producido un error al reproducir el archivo\nReintentando...")

        thread_finished = True

def reboot():
	global thread_finished

	logger.info("Button reboot pressed... [OK]")
	# Reboot rasp
	command = "/sbin/shutdown -r now"
	run_cmd(command, False)
	print "Reboot pressed!"

	thread_finished = True
	
def shutdown():
	global thread_finished
	
	logger.info("Button shutdown pressed... [OK]")
	command = "/sbin/shutdown -h now"
	run_cmd(command, False)
	print "Shutdown pressed!"
	
	thread_finished = True

def restart():
	global thread_finished

	logger.info("Button restart pressed... [OK]")
	command = "service player restart"
	run_cmd(command, False)
	print "Restart pressed!"

	thread_finished = True

#def buttons():
#	global thread_finished
#	
#	buttonShutdown = 11
#	
#	GPIO.setmode(GPIO.BCM)
#
#	GPIO.setup(buttonShutdown, GPIO.IN)

#	while True:
#		if (GPIO.input(buttonShutdown)):
#			lcd = LCD()
#			lcd.clear()
#			lcd.begin(16,1)
#			lcd.message("Apagando\nSistema...")
#			sleep(3)
#			lcd.clear()
#			shutdown()
#			sleep(0.5)
#	thread_finished = True

# This function check if mpg123 is running all time, in case of
# error, the software will be restarted
def checkSoundOutput():
	global thread_finished

	sleep(15) #Wait while the main function load

	while True:
		output = run_cmd(cmd_check_sound, True)
		if (output == ""):
			print "Error: mpg123 is not running"
			logger.error("mpg123 is not running")
			logger.critical("The software will be restarted")
			command = "service player restart"
			run_cmd(command, False)

		sleep(60) #Check each 60 seconds

	thread_finished = True

#def playStreaming(url, *args):
#	if checkInternetConnection():
#		cmd_play_streaming = "mpg123 -v " + url + " &"
#		while True:
#			run_cmd(cmd_play_streaming, True)
#	else:
#		while True:
#			playBackup()
	

def main():
        global thread_finished
#	logger.info('Player started!')
	
	# Basic commands for play the music
#	currentBackup = ""

	# Initialize LCD
	lcd = LCD()
	lcd.clear()
	lcd.begin(16,1)

        # Stop all players
        run_cmd(cmd_stop_all, False)

	# Start radio or backup
#	ledConnection = 2
#	ledCheck = 3

	GPIO.setmode(GPIO.BCM)
#	GPIO.setup(ledConnection, GPIO.OUT)

	# Start the main program in an infinite loop
	while True: 
		lcd.clear()
		lcd.message("ExeaMusicPlayer")
		sleep(2)
		
		lcd.clear()
		lcd.message("Escuchas:\n")
		lcd.message(title)
		sleep(2)
		
		#Check connection of internet
#		GPIO.output(ledConnection, 1)
		if checkInternetConnection():
#			GPIO.output(ledConnection, 0)
			#sleep(0.5)
                        lcd.clear()
                        lcd.message("Estas conectado\na Internet")
                        sleep(3)
		#Show IP info 
		lcd.clear()
		ipaddr = run_cmd(cmd_ip)
		if not ipaddr:
			lcd.message('Sin Internet\n')
		else:
			lcd.message('IP%s' % ( ipaddr ))

		#Show date for 10 seconds
		i = 0
		while i<10:
			lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
			sleep(1)
			i = i+1
			pass

	thread_finished = True

# def setup():
# 	global thread_finished

# 	while True:
# 		code = lirc.nextcode()
# 		if (len(code) > 0):
# 			code = code[0]
# 			if(code == 'MENU'):
# 				print 'Ha presionado el boton Menu!'
# 			elif(code == 'BACK'):
# 				print 'Ha presionado el boton Back!'
# 			elif(code == 'SELECT'):
# 				print 'Ha presionado el boton Select!'
# 			elif(code == 'NUMBER_0'):
# 				print 'Ha presionado el boton 0!'
# 			elif(code == 'NUMBER_1'):
# 				print 'Ha presionado el boton 1!'
# 			elif(code == 'NUMBER_2'):
# 				print 'Ha presionado el boton 2!'
# 			elif(code == 'NUMBER_2'):
# 				print 'Ha presionado el boton 2!'
# 			elif(code == 'NUMBER_3'):
# 				print 'Ha presionado el boton 3!'
# 			elif(code == 'NUMBER_4'):
# 				print 'Ha presionado el boton 4!'
# 			elif(code == 'NUMBER_5'):
# 				print 'Ha presionado el boton 5!'
# 			elif(code == 'NUMBER_6'):
# 				print 'Ha presionado el boton 6!'
# 			elif(code == 'NUMBER_7'):
# 				print 'Ha presionado el boton 7!'
# 			elif(code == 'NUMBER_8'):
# 				print 'Ha presionado el boton 8!'
# 			elif(code == 'NUMBER_9'):
# 				print 'Ha presionado el boton 9!'
# 		pass

# 	thread_finished = True

def blinker():

	global thread_finished

	ledTest = 4
	GPIO.setup(ledTest, GPIO.OUT)
	
	while True:
		GPIO.output(ledTest, 0)
		sleep(0.5)
		GPIO.output(ledTest, 1)
		sleep(0.5)

	thread_finished = True

if __name__ == '__main__':

        # Control for threads
#        thread_finished = False

	# Read arguments
	if len(sys.argv) >= 3:
#		url = sys.argv[1]
		for x in xrange(1, len(sys.argv)):
			title = title + sys.argv[x] + " "
#
#		print "The url of the streaming is:",colored(url, "green")
		print "The name of the radio is:", colored(title, "green")
#		logger.info('The url of the streaming is: ' + url)
		logger.info('The name of the radio is: ' + title)
#
	else:
#		print "Usage: player.py {url} {title}";
		logger.error("Usage: player.py {title}")
#
#	try:
#		Thread(target=blinker, args=()).start()
#		Thread(target=playStreaming, args=(url, 1)).start()
#		Thread(target=main, args=()).start()
#	except KeyboardInterrupt:
#		print "Bye!"
#	 	logger.info('Bye!')
#	except Exception, errtxt:
#		logger.info('Program finished by external exception')
#		logger.error(errtxt)

        # Control for threads
	thread_finished = False
	
	try:
	 	# No warnings for GPIO use
	 	GPIO.setwarnings(False)
	 	GPIO.setmode(GPIO.BCM)
	 	thread.start_new_thread(playMusic, ())
		thread.start_new_thread(checkSoundOutput, ())
		thread.start_new_thread(blinker, ())
	# 	# thread.start_new_thread(setup, ())
	# 	thread.start_new_thread(playStreaming, (url))
	 	thread.start_new_thread(main, ())
		
	 	while (not thread_finished):
	 		pass
	 	logger.info('Program finished')

	except KeyboardInterrupt:
	 	print "Bye!"
	 	logger.info('Bye!')
	except Exception:
	 	logger.info('Program finished by external exception')
