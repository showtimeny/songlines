#!/usr/bin/python
# -*- coding: utf-8 -*-

##This is a screen scraper for www.fmqb.com
##The script logs into fmqb using supplied credentials,
##then navigates to the Add Board page and copies the data
##there into a list called "songs".
##
##TO-DO:
##    1. Refactor the code to be generic for all pages at FMQB
##    2. Pass the data into an actual database with a sensible
##       model logic
##    3. Build a django web app to pull data from the DB and
##       display it in interesting ways
##
##Happy hacking! ;)




import mechanize, cookielib, sys
from bs4 import BeautifulSoup, NavigableString
import sqlite3 as lite
from django.utils.encoding import smart_str, smart_unicode


  #                                #
 ##                                ##
### First, we log into the site... ###
 ##                                ##
  #                                #

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
#br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# The site we will navigate into, handling its session
br.open('http://triplea.fmqb.com/home.aspx')


#Code for displaying the forms returned by the page
##for f in br.forms():
##    print f

# Select the first (index zero) form
br.select_form(nr=0)

# User credentials
br.form['txtUser'] = ''
br.form['txtPass'] = ''

# Login
br.submit()

### Scrape data from every page ###

# Get all the links on the home page
all_links = [l for l in br.links()]

#pages is a List of each page's html code, as a string
pages_strings = []

# For every link except the 0th one (the home page), follow
# it, read it's html as a string, and pop it into the pages[] List
for link in all_links[1:]:
    br.follow_link(link)
    html = br.response().read()
    pages_strings.append(html)

#pages_soup is a List containing all pages inside BeautifulSoup objects
pages_soup = []

# Turns each page into a BS object and stuffs it into pages_soup
for page in pages_strings:
    soup = BeautifulSoup(page)
    pages_soup.append(soup)

con = lite.connect('sqlite3.db')
with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS Stations")
    cur.execute("DROP TABLE IF EXISTS Adds")
    cur.execute("DROP TABLE IF EXISTS Top200")
    cur.execute("DROP TABLE IF EXISTS Top200_nc")
    cur.execute("DROP TABLE IF EXISTS Playlists")
    
    cur.execute("CREATE TABLE Stations(name TEXT, status TEXT, address TEXT, phone TEXT, market TEXT, calls TEXT, specialty TEXT)")
    cur.execute("CREATE TABLE Adds(artist TEXT, album TEXT, label TEXT, adds INT)")
    cur.execute("CREATE TABLE Top200(artist TEXT, song TEXT, album TEXT, label TEXT, rank_tw TEXT, rank_lw TEXT, spins_tw TEXT, spins_lw TEXT, spins_chg TEXT)")
    cur.execute("CREATE TABLE Top200_nc(artist TEXT, album TEXT, label TEXT, rank_tw TEXT, rank_lw TEXT, spins_tw TEXT, spins_lw TEXT, spins_chg TEXT)")
    cur.execute("CREATE TABLE Playlists(rank_tw TEXT, rank_lw TEXT, artist TEXT, title TEXT, album TEXT, label TEXT, adds_tw TEXT, adds_lw TEXT, move TEXT, added TEXT, station_name TEXT, station_address TEXT)")
 #Scrape everything from the top list
for soup in pages_soup:
    #LINK 1: STATION DIRECTORY

    if soup == pages_soup[0]:
        print "Scraping Station Directory..."
        stations = []

        #for each table row, make a BS object
        for table_row in soup.find_all('tr'):
            tr_soup = BeautifulSoup(str(table_row))
            station_data =[]
            #for each table data, make a BS object
            for table_data in table_row.find_all('td'):
                td_soup = BeautifulSoup(str(table_data))
                td_string = str(td_soup.string.encode('ascii', 'ignore'))
                #compile all the TDs into a list
                station_data.append(td_string)
            #add each list of TDs into a list of stations
            stations.append(station_data)
        try:
            con = lite.connect('sqlite3.db',isolation_level=None)
            cur = con.cursor()
            for station in stations[1:]:
                station_name = station[0]
                station_status = station[1]
                station_addr = station[2]
                station_phone = station[3]
                station_market = station[4]
                station_calls = station[5]
                station_specialty = station[6]
                #cur.execute("DROP TABLE IF EXISTS Stations")
                cur.execute("INSERT INTO Stations VALUES("+"\""+station_name+"\""+","+"\""+station_status+"\""+","+"\""+station_addr+"\""+","+"\""+station_phone+"\""+","+"\""+station_market+"\""+","+"\""+station_calls+"\""+","+"\""+station_specialty+"\""+")")
        except lite.Error, e:
            print "Error %s: " % e.args[0]
    elif soup == pages_soup[1]: 
        print "\t\t\t...good!\nScraping Adds Board..."
    #LINK 2: ADD BOARD
        adds = []
        #for each table row, make a BS object
        for table_row in soup.find_all('tr'):
            tr_soup = BeautifulSoup(str(table_row))
            add_data =[]
            #for each table data, make a BS object
            for table_data in table_row.find_all('td'):
                td_soup = BeautifulSoup(str(table_data))
                td_string = str(td_soup.string.encode('ascii', 'ignore'))
                #compile all the TDs into a list
                add_data.append(td_string)
            #add each list of TDs into a list of stations
            adds.append(add_data)

        #This next bit is to see that we can actually grab each added song's attributes
        #one-by-one. Later, we'll push this data to a database.

        try:
            con = lite.connect('sqlite3.db',isolation_level=None)
            cur = con.cursor()
            for add in adds[1:]:
                add_artist = add[0]
                add_album = add[1]
                add_label = add[2]
                add_adds = add[3]
                cur.execute("INSERT INTO Adds VALUES("+"\""+add_artist+"\""+","+"\""+add_album+"\""+","+"\""+add_label+"\""+","+"\""+add_adds+"\""+")")
        except lite.Error, e:
            print "Error %s: " % e.args[0]

        print "\t\t\t...good!\nScraping Top 200 (Commercial)..."
    #LINK 3: TOP 200 (COMMERCIAL)
    elif soup == pages_soup[2]:
        top_comm_songs = []
        #for each table row, make a BS object
        for table_row in soup.find_all('tr'):
            tr_soup = BeautifulSoup(str(table_row))
            top_comm_song_data =[]
            #for each table data, make a BS object
            for table_data in table_row.find_all('td'):
                td_soup = BeautifulSoup(str(table_data))
                td_string = str(td_soup.string.encode('ascii', 'ignore'))
                #compile all the TDs into a list
                top_comm_song_data.append(td_string)
            #add each list of TDs into a list of stations
            top_comm_songs.append(top_comm_song_data)

        try:
            con = lite.connect('sqlite3.db',isolation_level=None)
            cur = con.cursor()
            for top_comm_song in top_comm_songs[1:]:
                tcs_artist = top_comm_song[2]
                tcs_song = top_comm_song[3]
                tcs_album = top_comm_song[4]
                tcs_label = top_comm_song[5]
                tcs_rank_tw = top_comm_song[1]
                tcs_rank_lw = top_comm_song[0]
                tcs_spins_tw = top_comm_song[6]
                tcs_spins_lw = top_comm_song[7]
                tcs_spins_change = top_comm_song[8]

                cur.execute("INSERT INTO Top200 VALUES("+"\""+tcs_artist+"\""+","+"\""+tcs_song+"\""+","+"\""+tcs_album+"\""+","+"\""+tcs_label+"\""+","+"\""+tcs_rank_tw+"\""+","+"\""+tcs_rank_lw+"\""+","+"\""+tcs_spins_tw+"\""+","+"\""+tcs_spins_lw+"\""+","+"\""+tcs_spins_change+"\""+")")
        except lite.Error, e:
            print "Error %s: " % e.args[0]
            print top_comm_song
        print "\t\t\t...good!\nScraping Top 200 (Non-Comm)..."
    #LINK 4: TOP 200 (NON-COMM)
    if soup == pages_soup[3]:
        top_non_comm_songs = []
        #for each table row, make a BS object
        for table_row in soup.find_all('tr'):
            tr_soup = BeautifulSoup(str(table_row))
            top_non_comm_song_data =[]
            #for each table data, make a BS object
            for table_data in table_row.find_all('td'):
                td_soup = BeautifulSoup(str(table_data))
                td_string = str(td_soup.string.encode('ascii', 'ignore'))
                #compile all the TDs into a list
                top_non_comm_song_data.append(td_string)
            #add each list of TDs into a list of stations
            top_non_comm_songs.append(top_non_comm_song_data)

        try:
            con = lite.connect('sqlite3.db',isolation_level=None)
            cur = con.cursor()
            for top_non_comm_song in top_non_comm_songs[1:]:
                tncs_artist = top_non_comm_song[2]
                tncs_album = top_non_comm_song[3]
                tncs_label = top_non_comm_song[4]
                tncs_rank_tw = top_non_comm_song[1]
                tncs_rank_lw = top_non_comm_song[0]
                tncs_spins_tw = top_non_comm_song[5]
                tncs_spins_lw = top_non_comm_song[6]
                tncs_spins_change = top_non_comm_song[7]

                cur.execute("INSERT INTO Top200_nc VALUES("+"\""+tncs_artist+"\""+","+"\""+tncs_album+"\""+","+"\""+tncs_label+"\""+","+"\""+tncs_rank_tw+"\""+","+"\""+tncs_rank_lw+"\""+","+"\""+tncs_spins_tw+"\""+","+"\""+tncs_spins_lw+"\""+","+"\""+tncs_spins_change+"\""+")")
        except lite.Error, e:
            print "Error %s: " % e.args[0]

        print "\t\t\t...good!\nScrape completed successfully!"
####    #LINK 5: YEAR TO DATE
####    if soup == pages_soup[4]:
####        YTD_songs = []
####        #for each table row, make a BS object
####        for table_row in soup.find_all('tr'):
####            tr_soup = BeautifulSoup(str(table_row))
####            YTD_song_data =[]
####            #for each table data, make a BS object
####            for table_data in table_row.find_all('td'):
####                if table_data:
####                    f = open('log.txt', 'a')
####                    "                        "
####                    f.write("\n======TABLE DATA======\n"+str(table_data))
####                    table_data = table_data.remove("\n")
####                    td_soup = BeautifulSoup(str(table_data))
####                    f.write("\n======TD_SOUP======\n"+str(td_soup))
####
######                td_string = str(td_soup.string).encode('ascii', 'ignore')
########                f.write("\n======TD_STRING======\n"+str(td_string))
######                #compile all the TDs into a list
######                YTD_song_data.append(td_string)
######            #add each list of TDs into a list of stations
######            YTD_songs.append(YTD_song_data)
######
########        #This next bit is to see that we can actually grab each added song's attributes
########        #one-by-one. Later, we'll push this data to a database.
########        for YTD_song in YTD_songs[1:]:
######             print "Rank:\t"+YTD_song[0]
######             print "Song: \t"+YTD_song[1]
######             print "Artist:\t"+YTD_song[2]
######             print "Album: \t"+YTD_song[3]
######             print "Label: \t"+YTD_song[4]
######             print "Spins: \t"+YTD_song[5]
######             print
##
##
##

### Scrape data from every station's playlist ###
print "Going to the Station Directory page..."
br.open('http://triplea.fmqb.com/stationDirectory.aspx')
station_links = [l for l in br.links()]

station_links_strings = [] #a List of each page's html code, as a string

print "following links..."
# For every link, follow
# it, read it's html as a string, and pop it into the station_links_strings List
for link in station_links[13:-1]:
    #print str(link)
    br.follow_link(link)
    #print "link followed"
    html = br.response().read()
    #print "response read"
    station_links_strings.append(html)
    #print "response added to list of pages"

#playlist_soup is a List containing all pages inside BeautifulSoup objects
playlist_soup = []


# Turns each page into a BS object and stuffs it into playlist_soup
for page in station_links_strings:
    soup = BeautifulSoup(page)
    #print "page changed to soup: "+soup.name
    playlist_soup.append(soup)
    #print "soup of playlists added to master playlist list"
for playlist in playlist_soup:
    playlists = []
    station_name = "SOME STATION"
    try: station_name = smart_str(playlist.h2.span.string)
    except: print "STATION NAME ERROR"
    station_address = "SOME PLACE"
    try: station_address = smart_str(playlist.h2.span.nextSibling.nextSibling.string)
    except: print "STATION ADDRESS ERROR"
    print "Scraping playlist from "+ station_name + " in " + station_address + ". . ."
    
    #for each table row, make a BS object
    table_rows = playlist.find_all('tr')
    for table_row in table_rows[:]:
        tr_soup = BeautifulSoup(str(table_row))
        playlists_data =[]
        #for each table data, make a BS object
        for table_data in table_row.find_all('td'):
            td_soup = BeautifulSoup(str(table_data))
            td_string = smart_str(td_soup.string)
            
            #compile all the TDs into a list
            playlists_data.append(td_string)
        #add each list of TDs into a list of stations
        #print str(playlists_data)
        playlists.append(playlists_data)

    try:
        con = lite.connect('sqlite3.db',isolation_level=None)
        cur = con.cursor()
        rank_lw = "rank_lw"
        rank_tw = "rank_tw"
        artist = "artist"
        title = "title"
        album = "album"
        label = "label"
        adds_tw = "adds_tw"
        adds_lw = "adds_lw"
        move = "move"
        added = "added"
        
        for playlist in playlists[1:]:
            rank_lw = playlist[0]
            rank_tw = playlist[1]
            artist = playlist[2]
            title = playlist[3]
            album = playlist[4]
            label = playlist[5]
            adds_tw = playlist[6]
            adds_lw = playlist[7]
            move = playlist[8]
            added = playlist[9]
            if rank_lw == "NEW": added="True"
            

          #  print rank_lw + "\t"+rank_tw+"\t"+artist+"\t"+title+"\t"+album+"\t"+label+"\t"+adds_tw+"\t"+adds_lw+"\t"+move+"\t"+added+"\t"+station_name+"\t"+station_address+"\n\n"

            cur.execute("INSERT INTO Playlists VALUES("+"\""+str(rank_tw)+"\""+","+"\""+str(rank_lw)+"\""+","+"\""+str(artist)+"\""+","+"\""+str(title)+"\""+","+"\""+str(album)+"\""+","+"\""+str(label)+"\""+","+"\""+str(adds_tw)+"\""+","+"\""+str(adds_lw)+"\""+","+"\""+str(move)+"\""+","+"\""+str(added)+"\""+","+"\""+str(station_name)+"\""+","+"\""+str(station_address)+"\""+")")
    except lite.Error, e:
        print "Error %s: " % e.args[0]
