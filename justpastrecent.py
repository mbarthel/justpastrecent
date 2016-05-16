from bs4 import BeautifulSoup
import re
import urllib2
from random import randint
import datetime
import calendar
import time
import pytumblr
import string

consumer_key = 'fillIn'
consumer_secret = 'fillIn'
token_key = 'fillIn'
token_secret = 'fillIn'

client = pytumblr.TumblrRestClient(
    consumer_key,
    consumer_secret,
    token_key,
    token_secret
)

exclude = set([",",".","?"])

#tumblr loop
while True:
    
    #Subtract 5 years from date
    today = datetime.datetime.now()
    DD = datetime.timedelta(days=1827)
    earlier = today - DD
    url="http://www.nytimes.com/indexes/"+earlier.strftime("%Y")+"/"+earlier.strftime("%m")+"/"+earlier.strftime("%d")+"/todayspaper/index.html"

    #Get page
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    #Get all stories
    stories=soup.find_all("div", class_="columnGroup first")[2].find_all('div', class_='story')
    num_stories=len(stories)-1

    #Tumblr implementation: construct post of headlines, links, and summaries
    items=[]
    headlines=[]
    links=[]
    summaries=[]
    for s in stories:
        story = s.h3
        headline = unicode(story.a.contents[0].strip())
        link = unicode(story.a['href'])
        summary = unicode(s.p.contents[0].strip())
        item="<li><a href='"+link+"'>"+headline+"</a><br>"+summary+"<br>&nbsp;<br></li>"
        items.append(item)
        headlines.append(headline)
        links.append(link)
        summaries.append(summary)

    #create post
    post = "<p>Here are the top stories from 5 years ago today.</p><ul>"
    for i in items:
        post = post+i
    post=post+"</ul>"
    post = post.replace(u"\u2018", "'").replace(u"\u2019", "'")

    #Extracting tags - first proper noun in sentence (up to 2 words)
    propers=[earlier.strftime("%Y")]
    for summary in summaries:
        sentence = summary.split(" ")
        sentence=sentence[1:-1]
        i=0
        for word in sentence:
            s=sentence[i]
            if s.istitle():
                if i+2 <= len(sentence):
                    if (s + " " + sentence[i+1]).istitle():
                        s = s + " " + sentence[i+1]
                s = ''.join(ch for ch in s if ch not in exclude)
                propers.append(s)
                break
            i=i+1

            #Title post as Month Date, Year + tags
    post_title = calendar.month_name[earlier.month] + " " + earlier.strftime("%d").lstrip("0") + ", " + earlier.strftime("%Y")
    post_title = post_title.replace(u"\u2018", "'").replace(u"\u2019", "'")
    if len(propers) > 1:
        propsminus = propers[1:-1]
        for p in propsminus:
            if p == propsminus[-1]:
                if propsminus[-1] == propsminus[0]:
                    post_title = post_title + ": " + p
                    break
                post_title = post_title + ", and " + p
                break
            if p == propsminus[0]:
                post_title = post_title + ": " + p
            else:
                post_title = post_title + ", " + p       

    client.create_text("your_blog_name", state="published", format="html", tags=propers, title=post_title, body=post)

    time.sleep(86400)