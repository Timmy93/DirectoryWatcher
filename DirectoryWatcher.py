#!/usr/bin/env python3
import threading
import inotify.adapters
import logging
import os
import time

# The main class
class DirectoryWatcher (threading.Thread):
   
	def __init__(self, callbackFunction, logging=None):
		threading.Thread.__init__(self)
		self.logging = logging
		self.callbackFunction = callbackFunction
		self.logging.info("Created DirectoryWatcher element")
		
	def watchThisDirectory(self, directory, events, recursively=False):
		if not os.path.isdir(directory):
			self.logging.error("The given directory ["+str(directory)+"] is not a directory")
			raise Exception("The given directory ["+str(directory)+"] is not a directory")
			
		if events:
			#Consider all events as array
			if type(events) is str:
				events = [events]
			self.watchedEvents = events
			self.logging.info("Monitoring the following events: ["+str(self.watchedEvents)+"]")
		else:
			self.error.info("No events to monitor")
			raise Exception('No events to monitor')
			
		if recursively:
			self.notifier = inotify.adapters.InotifyTree(directory)
			self.logging.info("Starting a recursive monitoring on directory and subdirectory ["+directory+"]")
		else:
			self.notifier = inotify.adapters.Inotify()
			self.notifier.add_watch(directory)
			self.logging.info("Starting a plain monitoring on directory ["+directory+"]")
	
	def run(self):
		while(1):
			try:
				for event in self.notifier.event_gen():
					if event is not None:
						for we in self.watchedEvents:
							if we in event[1]:
								newfile = os.path.join(event[2], event[3])
								self.logging.info("Registered event ["+str(event[1])+"] for file ["+newfile+"]")
								try:
									while not self.stableSize(newfile):
										self.logging.info("Still writing on file ["+newfile+"]")
									self.callbackFunction(newfile)
								except FileNotFoundError as err:
									self.logging.warning("File missing ["+newfile+"] - Skipping callback ["+str(err)+"]")
				self.logging.warning("DirectoryWatcher stopped checking directory")
			except RuntimeError as err:
				self.logging.warning("Thread is dead for a Runtime error ["+str(err)+"]")
			except Exception as err:
				self.logging.error("Unexpected thread dead ["+str(err)+"]")
	
	#Check if the file is still being written
	def stableSize(self, myFile):
		initialSize = os.path.getsize(myFile)
		time.sleep(1)
		return os.path.getsize(myFile) == initialSize
