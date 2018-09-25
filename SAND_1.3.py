import re 
import tweepy
import sys
from tweepy import AppAuthHandler 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as co

class SAND(object): 
    def __init__(self): 
        
        # API keys from the Twitter Dev Console
        # NOTE : Add yours here
        api_key = 'YOUR API KEY HERE'
        api_key_secret = 'YOUR API SECRET HERE'
  
        # Attempt authentication
        self.auth = AppAuthHandler(api_key, api_key_secret)
        # Create tweepy API object to get tweets, wait if we reach the rate limit (45,000 tweets/15 mins if using free API)
        self.api = tweepy.API(self.auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True) 
        if (not self.api) :
            print("Can't authenticate")
            sys.exit(-1)

    # Remove any unnecessary characters from tweets
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 

    def get_tweets(self, tweet_limit, query, count):
        tweets = [] # Create an empty list to store the tweets
        gotten = 0 # Number of tweets grabbed
        # sinceId and max_id are used to keep track of where the program last "left off"
        # in order to avoid scraping through the same set of tweets in the event of high-volume
        # runs which require waiting periods
        # NOTE : these variables probably won't be necessary with a higher-level paid license
        # which allows more tweets to be scraped per 15 minute cycle
        sinceId = None # Set the first sinceId to be None
        max_id = -sys.maxsize - 1 # Set maxId to be very large negative
        # While we wait for tweets to be collected
        print()
        print("        =============================================")
        print("        | Scraping Twitter for data, please wait... |")
        print("        |     This could take a very long time.     |")
        print("        =============================================")
        print()
        # While we haven't hit the max tweets allowed (chosen by user at start)
        while (gotten < tweet_limit) :
            # Try to grab the tweets
            try: 

                if (max_id <= 0) : # Always entered first
                    if (not sinceId) :
                        fetched_tweets = self.api.search(q = query, count = count) # Grabs tweets from Twitter API using Tweepy
                    else :
                        fetched_tweets = self.api.search(q = query, count = count, since_id = sinceId)
                else :
                    if (not sinceId) :
                        fetched_tweets = self.api.search(q = query, count = count, max_id = str(max_id - 1))
                    else :
                        fetched_tweets = self.api.search(q = query, count = count, max_id = str(max_id - 1), since_id = sinceId)
                if not fetched_tweets : # No more tweets through which to scan
                    print("All tweets available at this time have been scraped :(")
                    break

                gotten += len(fetched_tweets) # Keep track of the number of tweets grabbed so far
                #Iterating through
                for tweet in fetched_tweets:
                    addable = True
                    # Ensures that the tweet has location
                    if tweet.user.location:
                        #Clean up the text
                        cleantweet = self.clean_tweet(tweet.text)

                        if len(tweets) != 0:
                            # Iterate through tweets and check if they are already in the array
                            for i in range(0, len(tweets)): 
                                if tweets[i][0] == cleantweet :
                                    addable = False
                            if addable:
                                tweets.append([cleantweet, tweet.user.location])
                        # If list is empty, append the first item
                        else:
                            tweets.append([cleantweet, tweet.user.location])
                   
                max_id = fetched_tweets[-1].id # Keeps track of the maxId so far
            # If Try fails
            except tweepy.TweepError as e: 
                print("Error : " + str(e)) 
                
        return tweets
        

    def location_cleaner(self, tweetlist): # Function to parse through geolocation of Tweets
        big_town_list = [] # Create some empty arrays for later
        good_locs = []
        # We use the user's set location to determine their geographical location (coordinates)
        state_list = ["Alabama","AL", "Arizona","AZ","Arkansas","AR","California","CA","Colorado","CO","Connecticut","CT","Delaware","DE","District of Columbia","DC","Florida","FL",\
                    "Georgia","GA","Idaho","ID","Illinois","IL","Indiana","IN","Iowa","IA","Kansas","KS","Kentucky","KY","Louisiana","LA","Maine","ME","Montana","MT",\
                    "Nebraska","NE","Nevada","NV","New Hampshire","NH","New Jersey","NJ","New Mexico","NM","New York","NY","North Carolina","NC","North Dakota","ND",\
                    "Ohio","OH","Oklahoma","OK","Oregon","OR","Maryland","MD","Massachusetts","MA","Michigan","MI","Minnesota","MN","Mississippi","MS","Missouri","MO",\
                    "Pennsylvania","PA","Rhode Island","RI","South Carolina","SC","South Dakota","SD","Tennessee","TN","Texas","TX","Utah","UT","Vermont","VT","Virginia","VA",\
                    "Washington","WA","West Virginia","WV","Wisconsin","WI","Wyoming","WY"]
        # List to be returned
        out_list = []

        # Appends csv file of locations to array 
        fp = open('zip_codes_states.csv', 'r')
        fp.readline()
        for line in fp :
            line = fp.readline()
            splitline = line.strip("\n").replace('"', '').split(",")
            if len(splitline) == 6 :
                big_town_list.append(splitline)
        fp.close()

        # For each input
        for string_pair in tweetlist:

            # If the location has a comma
            if "," in string_pair[1] :

                # Split by comma
                split_str = string_pair[1].split(",")
                
                # If there are two words after comma split
                if len(split_str) == 2 :

                    # And if the second word is in the list of acceptable states:
                    if split_str[1].strip(" ") in state_list :

                        # Add the full, stripped string to the list of good locations
                        good_locs.append([string_pair[0], split_str[0].strip(" "), split_str[1].strip(" ")])

        # "zip_code","latitude","longitude","city","state","county"
        # 0 = zip   1 = lat    2 = long   3 = city  4 = state  5 = county

        # Sets the values in array to be sent to the sentiment function
        for cur_loc in good_locs :

            for cur_town in big_town_list :

                if (cur_loc[1] == cur_town[3] and cur_loc[2] == cur_town[4]) :

                    out_list.append([cur_loc[0], cur_town[1], cur_town[2]])
                    break

        return out_list

    # Determines the sentiments (pos or neg) of each tweet in list
    def List_Sentiments(self, tweetlist):
        analyzer = SentimentIntensityAnalyzer()
        newlist = tweetlist

        for i in range(0, len(tweetlist)):
            cur = tweetlist[i][0]
            newlist[i][0] = analyzer.polarity_scores(cur)

        return newlist


def main():
    # MAIN
    
    # User Interface
    api = SAND()
    print()
    print("==============================================================")
    print("|                    Welcome to S.A.N.D.!                    |")
    print("|        (Sentiment Analysis via Network Data-mining)        |")
    print("==============================================================")
    print("|                                                            |")
    print("|     This program will take given search parameters and     |\n\
|    collect relevant tweets. These are then run through a   |\n\
|    sentiment analysis program, and tied to their city of   |\n\
|     origin. The results are then displayed on a map of     |\n\
|     the continental United States, scaled according to     |\n\
|  tweet density and colored according to average sentiment. |")
    print("==============================================================")
    print()
    print("Search Options:")
    print()
    print("'S'  : Scrape  10,000  tweets (~2-5 min)")
    print("'M'  : Scrape  45,000  tweets (~10-15 min)")
    print("'L'  : Scrape  90,000  tweets (~20-30 min)")
    print("'XL' : Scrape  180,000 tweets (~60+ min)")
    print()
    print("Warning: only a small percentage of scraped tweets\n\
will contain the necessary data to be analyzed and\n\
added to the map. ")
    print()
    option = input("Please choose an option, then press <return>: ")
    if (option.upper() == 'S') :
        tweet_limit = 10000
    elif (option.upper() == 'M') :
        tweet_limit = 45000
    elif (option.upper() == 'L') :
        tweet_limit = 90000
    elif (option.upper() == 'XL') :
        tweet_limit = 180000
    elif (option.upper() == 'TINYTEST') : # For backend to test small cases
        tweet_limit = 1000
    else :
        print("Invalid input. Shutting down...")
        quit()

    searchterm = str(input("Please enter a search term: "))
    # Starts with list of tweets
    goodTweets = api.get_tweets(tweet_limit, query = searchterm, count = 100)
    # Cleans and finds tweets' geolocation and sets their sentiments
    goodList = api.location_cleaner(goodTweets)

    finalList = api.List_Sentiments(goodList) # finalList is in the format [[{VADER sentiment output}, 'latitude', 'longitude'], ...]
                                              # with an entry corresponding to each tweet with the proper location data


    final2 = []

    # Ensures no faulty coordinates got through
    for term in finalList :
        # If a term has proper coordinates
        if term[1] != "" and term[2] != "" :
            temp = term[0]['compound'] # Replaces the VADER dictionary with its compund sentiment value
            term[0] = temp
            term[0] = float(term[0]) # Convert all terms to float values
            term[1] = float(term[1].strip())
            term[2] = float(term[2].strip())
            final2.append(term) # Add cleaned data to new list

    print("Found " + str(len(final2)) + " tweets with usable data.")

    # Averages the sentiments for each tweet and totals the number of tweets from each location
    avged_list = []

    # list final2 is of the format: [[compound sentiment score, latitude, longitude], ...] for each tweet, with all values being floats
    for term in final2 : # For each set of cleaned, good location data

        # Assume location hasn't been added to avged_list yet
        present = False

        # Check current term with every present location in avged_list
        for cluster in avged_list :

            # If lat/lon pair already exists
            if (term[1] == cluster[1] and term[2] == cluster[2]) :

                # Add term's compound sentiment score to location's total
                cluster[0] += term[0]
                # And iterate location's number of entries up by 1
                cluster[3] += 1
                # And mark the location as already existing in avged_list
                present = True
                break

        # If location has no entry in avged_list, add it with entry quantity starting at 1
        if present == False :

            avged_list.append([term[0], term[1], term[2], 1])

    for cluster in avged_list : # For each location

        cluster[0] = cluster[0]/cluster[3] # Divide total sentiment score by number of entries at location
                                           # to obtain average sentiment at that location

    # avged_list is now of the form: [[avg sentiment, latitude, longitude, number of tweets from this location], ...] with one
    #                                                                              entry for each unique town that contributed
    #                                                                                   at least 1 tweet to the data set

    # Finds highest clusters of locations and highest pos/neg averages
    big_town_list = []

    fp = open('zip_codes_states.csv', 'r')
    fp.readline()
    for line in fp :
        line = fp.readline()
        splitline = line.strip("\n").replace('"', '').split(",")
        if len(splitline) == 6 :
            big_town_list.append(splitline)
    fp.close()

    # Initialize variables used to print notable data points
    most_participation = avged_list[0]
    most_pos = avged_list[0]
    most_neg = avged_list[0]

    # Set above variables to the "cluster" corresponding to their names
    for cluster in avged_list :

        if cluster[3] > most_participation[3] :
            most_participation = cluster

        if cluster[3] >= 5 and cluster[0] > most_pos[0] :
            most_pos = cluster

        if cluster[3] >= 5 and cluster[0] < most_neg[0] :
            most_neg = cluster

    # Initialize variables used to print notable data points
    big_town_name = ""
    most_pos_loc = ""
    most_neg_loc = ""

    # For every town in the US
    for town in big_town_list :

        # If lat/lon match any of the notable points, get the town name and make it a string
        if town[1] == str(most_participation[1]) and town[2] == str(most_participation[2]) :
            big_town_name = str(town[3] + ", " + town[4])

        if town[1] == str(most_pos[1]) and town[2] == str(most_pos[2]) :
            most_pos_loc = str(town[3] + ", " + town[4])

        if town[1] == str(most_neg[1]) and town[2] == str(most_neg[2]) :
            most_neg_loc = str(town[3] + ", " + town[4])

    # Print any relevant data points that were found
    print()
    if big_town_name == "" :
        pass
    else :
        print("Most participation: " + str(most_participation[3]) + " usable tweets from " + big_town_name + ".")
    if most_pos_loc == "" or most_pos[0] <= 0 :
        print("Most positive area: Not enough data present")
    else :
        print("Most positive area: " + most_pos_loc + " with an average rating of %.3f." % most_pos[0])
    if most_neg_loc == "" or most_neg[0] >= 0 :
        print("Most negative area: Not enough data present")
    else :
        print("Most negative area: " + most_neg_loc + " with an average rating of %.3f." % most_neg[0])
    print()

    # Establish window size
    fig = plt.figure(figsize=(12, 7))
    # Set background color to grey and opacity to 30%
    fig.patch.set_facecolor('gray')
    fig.patch.set_alpha(0.3)
    # Set window title
    fig.canvas.set_window_title('Sentiment Map')
    # Create basemap object and set proper coordinates and sizing to line up with continental United States
    m = Basemap(projection='lcc', resolution='l',width=4800000, height=3300000, lat_0=39, lon_0=-96.5)

    # Draw lines marking countries, coastlines, and US states
    m.drawcountries(linewidth=0.5, linestyle='solid', color='gray', antialiased=1, ax=None, zorder=None)
    m.drawcoastlines(linewidth=0.5, linestyle='solid', color='gray', antialiased=1, ax=None, zorder=None)
    m.drawstates(linewidth=0.5, linestyle='solid', color='gray', antialiased=1, ax=None, zorder=None)

    # Sets color mapping to Red-Yellow-Green gradient
    cmap = plt.cm.RdYlGn
    # Normalizes colors into the range -1, 1
    norm = co.Normalize(-1, 1)
    # Creates ScalarMappable color object to properly color data points on map
    pointcolors = plt.cm.ScalarMappable(norm, cmap)

    # For each city's trimmed and averaged data
    for data in avged_list :
        # Take the cube root of the value in order to make sentiment differences more visible
        if data[0] <= 0 : # data[0] corresponds to the sentiment value of that particular lat/lon (city)
            # Special case to avoid taking cube root of a negative number
            data[0] = -((abs(data[0]))**(1/3))
        else :
            data[0] = ((data[0])**(1/3))
        sentiment = data[0]
        x = data[1] # latitude of current city
        y = data[2] # longitude of current city
        size = np.pi*data[3] # scale size of circles by pi
        col = pointcolors.to_rgba(sentiment) # convert city's sentiment value into RGBA value
        # Add city's data point to scatter plot (add it onto the map)
        m.scatter(y, x, latlon =True, c = col, cmap = 'cmap', s = size, linewidth = 0, alpha = 0.75 )

    pointcolors.set_array(sentiment) # Attach color object to a sentiment value
    plt.colorbar(pointcolors, label="Average Sentiment") # Create color bar to help describe map
    plt.clim(-1, 1) # Set limits of values to range -1, 1
    # Add text to corner indicating how many tweets were used to create this particular map
    plt.text(0.5, 0.5, 'Total tweets plotted: ' + str(len(final2)), horizontalalignment='left', verticalalignment='bottom')
    plt.title("Twitter Sentiment of " + searchterm) # Set title

    plt.show() # Display map

if __name__ == "__main__" :
    main()