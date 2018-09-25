SANDMapMaker
Welcome to S.A.N.D. — Please read before you get started!

This application utilizes many powerful python libraries / APIs that are available for free. 
These must be installed in order for the program to function properly. 
Below is a list of these libraries:

1) Tweepy (link: http://docs.tweepy.org/en/v3.6.0/install.html)
IMPORTANT: Tweepy requires you to have access to a twitter API key 
(found here: https://developer.twitter.com/en/docs.html). 
On lines 17 and 18 of SAND_1_3 enter your valid key and key 
secret, respectfully, in place of the text.

2) vaderSentiment (link: https://github.com/cjhutto/vaderSentiment)

3) matplotlib (link: https://matplotlib.org/users/installing.html)

4) basemap (link: https://matplotlib.org/basemap/users/installing.html)

5) numpy (link: https://www.scipy.org/install.html)


S.A.N.D. will take given search parameters and collect relevant tweets. 
These are then run through a sentiment analysis program, and tied to their city of origin. 
The results are then displayed on a map of the continental United States, scaled according to 
tweet density and colored according to average sentiment. 

Disclaimer: Several code samples were taken directly from developers’ websites in this program. 
We did our best to indicate this in the comments near any copied code. 

September 23, 2018

Team:
Seth Layton
Greg Pennisi
Will Wolz