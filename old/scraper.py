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
br.form['txtUser'] = 'scoakley'
br.form['txtPass'] = 'sophie'

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

f = open('log.txt', 'a')

for soup in pages_soup:
    #LINK 1: STATION DIRECTORY
    if soup == pages_soup[0]:
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

        #This next bit is to see that we can actually grab each stations attributes
        #one-by-one. Later, we'll push this data to a database.
        for station in stations[1:]:
             f.write("Name: \t\t"+station[0]+"\n")
             f.write("Comm/Public:\t"+station[1]+"\n")
             f.write("Address: \t"+station[2]+"\n")
             f.write("Phone: \t\t"+station[3]+"\n")
             f.write("Market: \t"+station[4]+"\n")
             f.write("Calls: \t\t"+station[5]+"\n")
             f.write("Specialty: \t"+station[6]+"\n")
             f.write("\n")

    #LINK 2: ADD BOARD
    elif soup == pages_soup[1]:
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
        for add in adds[1:]:
             f.write("Artist:\t"+add[0]+"\n")
             f.write("Album:\t"+add[1]+"\n")
             f.write("Label: \t"+add[2]+"\n")
             f.write("Adds: \t"+add[3]+"\n")
             f.write("\n")
                     
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

        #This next bit is to see that we can actually grab each added song's attributes
        #one-by-one. Later, we'll push this data to a database.
        for top_comm_song in top_comm_songs[1:]:
             f.write("Artist:\t\t"+top_comm_song[2]+"\n")
             f.write("Song:\t\t"+top_comm_song[3]+"\n")
             f.write("Album: \t\t"+top_comm_song[4]+"\n")
             f.write("Label: \t\t"+top_comm_song[5]+"\n")
             f.write("Rank TW: \t"+top_comm_song[1]+"\n")
             f.write("Rank LW: \t"+top_comm_song[0]+"\n")
             f.write("Spins TW: \t"+top_comm_song[6]+"\n")
             f.write("Spins LW: \t"+top_comm_song[7]+"\n")
             f.write("Spins (+/-): \t"+top_comm_song[8]+"\n")
             f.write("\n")         
        
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

        #This next bit is to see that we can actually grab each added song's attributes
        #one-by-one. Later, we'll push this data to a database.
        for top_non_comm_song in top_non_comm_songs[1:]:
             f.write("Artist:\t\t"+top_non_comm_song[2]+"\n")
             f.write("Album: \t\t"+top_non_comm_song[3]+"\n")
             f.write("Label: \t\t"+top_non_comm_song[4]+"\n")
             f.write("Rank TW: \t"+top_non_comm_song[1]+"\n")
             f.write("Rank LW: \t"+top_non_comm_song[0]+"\n")
             f.write("Spins TW: \t"+top_non_comm_song[5]+"\n")
             f.write("Spins LW: \t"+top_non_comm_song[6]+"\n")
             f.write("Spins (+/-): \t"+top_non_comm_song[7]+"\n")
             f.write("\n")
##    #LINK 5: YEAR TO DATE
##    if soup == pages_soup[4]:
##        YTD_songs = []
##        #for each table row, make a BS object
##        for table_row in soup.find_all('tr'):
##            tr_soup = BeautifulSoup(str(table_row))
##            YTD_song_data =[]
##            #for each table data, make a BS object
##            for table_data in table_row.find_all('td'):
##                if table_data:
##                    f = open('log.txt', 'a')
##                    "                        "
##                    f.write("\n======TABLE DATA======\n"+str(table_data))
##                    table_data = table_data.remove("\n")
##                    td_soup = BeautifulSoup(str(table_data))
##                    f.write("\n======TD_SOUP======\n"+str(td_soup))
##     
####                td_string = str(td_soup.string).encode('ascii', 'ignore')
######                f.write("\n======TD_STRING======\n"+str(td_string))
####                #compile all the TDs into a list
####                YTD_song_data.append(td_string)
####            #add each list of TDs into a list of stations
####            YTD_songs.append(YTD_song_data)
####
######        #This next bit is to see that we can actually grab each added song's attributes
######        #one-by-one. Later, we'll push this data to a database.
######        for YTD_song in YTD_songs[1:]:
####             print "Rank:\t"+YTD_song[0]
####             print "Song: \t"+YTD_song[1]
####             print "Artist:\t"+YTD_song[2]
####             print "Album: \t"+YTD_song[3]
####             print "Label: \t"+YTD_song[4]
####             print "Spins: \t"+YTD_song[5]
####             print 

