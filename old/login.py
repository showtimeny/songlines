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
br.set_handle_gzip(True)
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

# Filter all links to mail messages in the inbox
links = br.links()
for foo in links:
    print str(foo)
all_links = [l for l in br.links()]
#br.follow_link(all_links)
#for link in station_links:
#    br.follow_link(link)
#    html = br.response().read()
#    soup = BeautifulSoup(html)
#print soup

for link in all_links[1:2]:
    #Open the link(s)
    br.follow_link(link)
    for link in br.follow_link(link):
        html = br.response().read()
    #Create a BeautifulSoup object using the HTML from the returned page
        soup = BeautifulSoup(html)

  #                                #
 ##                                ##
### And now, to hijack the data... ###
 ##                                ##
  #                                #

table_data = soup.find_all('td')
##rows = BeautifulSoup(str(artists))
##print(rows.prettify())
##for artist in artists.stripped_strings:
##    print artist

rows = []

def find_data(tags):
    for tag in tags:
        if tag.__class__ == NavigableString:
            rows.append(tag)
        else:
            find_data(tag)
find_data(table_data)

#print str(rows)

songs = []


x=0
for i in range(len(rows)):
   while x+3 < len(rows):
    if x==0 or x%4==0:
        songs.append((rows[x],rows[x+1],rows[x+2],rows[x+3]))
        x = x+4
    
for y in songs:
    for z in y:
        print str(z) + " "
    #print "\n"

##row = 1
##artists = []
##albums = []
##labels = []
##adds = []
##
##for i in rows:
##    if row == 1:
##        artists.append(i)
##        row = row + 1
##    elif row == 2:
##        albums.append(i)
##        row = row + 1
##    elif row == 3:
##        labels.append(i)
##        row = row + 1
##    elif row == 4:
##        adds.append(i)
##        row = 1
##
##for x in labels:
##    print x



