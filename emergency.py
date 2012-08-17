#!/usr/bin/python
#
# IRC b0t that keeps track of RSS feeds
#
# Licensed under the GNU General Public License v3
#
# Copyright (2009) by Akarsh Simha
# Copyright (2012) by Spencer Krum
 
import irclib
import feedparser
import os
import threading
import time
import re
 
channel_list = [ "#emergency" ]  # Put in a list of channels
feed_list = [ "http://www.publicalerts.org/rss.cfm", "http://pbfnode.pl/forum/index.php?PHPSESSID=a5b67416eb5fff2a4dff0f9ec8f7140d&action;=.xml;type=rss"]
old_entries_file = os.environ.get("HOME") + "/sandbox/ebs/old-feed-entries"
reject_list = ['TripCheckPDX']
def reject_against_list(string, list_of_re):
  for regex in list_of_re:
    if re.search(regex, string) is not None:
      return
  return string
 
irc = irclib.IRC()
server = irc.server()
 
server.connect( "irc.cat.pdx.edu", 6667, "ebs" ) # TODO: Make this general
# server.privmsg( "NickServ", "identify " )
 
msgqueue = []
 
def feed_refresh():
 #print "Test"
 FILE = open( old_entries_file, "r" )
 filetext = FILE.read()
 FILE.close()
 for feed in feed_list:
  NextFeed = False
  d = feedparser.parse( feed )
  for entry in d.entries:
   id = entry.link.encode('utf-8')+entry.title.encode('utf-8')
   if id in filetext:
    NextFeed = True
   else:
    FILE = open( old_entries_file, "a" )
    #print entry.title + "\n"
    FILE.write( id + "\n" )
    FILE.close()
    msgqueue.append( entry.title.encode('utf-8') + " : " + entry.link.encode('utf-8') )
   if NextFeed:
    break;
 
 t = threading.Timer( 900.0, feed_refresh ) # TODO: make this static
 t.start()
 
for channel in channel_list:
  server.join( channel )
 
feed_refresh()
 
while 1:
 while len(msgqueue) > 0:
  msg = msgqueue.pop()
  print msg
  grepped_msg = reject_against_list(msg, reject_list)
  if grepped_msg is not None:
    for channel in channel_list:
     server.privmsg( channel, grepped_msg )
 time.sleep(1) # TODO: Fix bad code
 irc.process_once()
 time.sleep(1) # So that we don't hog the CPU!

