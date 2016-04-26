#!/usr/bin/env python
import os, httplib, urllib
import csv
import datetime
from stravalib import Client
from stravalib.model import Activity
import matplotlib.pyplot as plt
import numpy as np

# Install oauth for python. On Ubuntu run: sudo apt-get install python-oauth
from oauth import oauth

ACCESS_TOKEN_STRING_FNAME = 'access_token.string'
STRAVA_ACCESS_TOKEN_STRING_FNAME = 'strava_access_token.string'
DEBUG = False

# pass oauth request to server (use httplib.connection passed in as param)
# return response as a string
def fetch_response(oauth_request, connection, debug=DEBUG):
   url= oauth_request.to_url()
   connection.request(oauth_request.http_method,url)
   response = connection.getresponse()
   s=response.read()
   if debug:
      print 'requested URL: %s' % url
      print 'server response: %s' % s
   return s

def get_login_token():
    last_activity = None
    # auth_token = ""

    if not os.path.exists(STRAVA_ACCESS_TOKEN_STRING_FNAME):

        print '* Obtain a request token ...'
        strava_client = Client()
        # auth_url = strava_client.authorization_url(client_id='601', redirect_uri='http://127.0.0.1:5000/authorisation')

        auth_token = strava_client.exchange_code_for_token(client_id='601', client_secret='600580e02b4814c75c93d3a60e15077147895776', code = '74cc257e6bc370d9da44cabc8852f3667ad95515')

        print auth_token

        fobj = open(STRAVA_ACCESS_TOKEN_STRING_FNAME, 'w')
        fobj.write(auth_token)

    else:
        print '* Reading request token from file ...'
        fobj = open(STRAVA_ACCESS_TOKEN_STRING_FNAME)
        auth_token = fobj.read()

    fobj.close()

    print auth_token
    return auth_token


def get_activities_from_strava():
    auth_token = get_login_token()
    #access_token = oauth.OAuthToken.from_string(access_token_string)

    strava_client = Client(access_token=auth_token)
    start_date = datetime.datetime(2016, 01, 01, 0, 0)
    activities = strava_client.get_activities(after=start_date)

    print "Activities.."
    print activities

    elevation_per_week = {}
    elevation_per_week_array = [0] * 54

    activitiesfile = open('activities.csv', 'w')
    activitieswriter = csv.writer(activitiesfile)


    for activity in activities:
        print activity
        details = strava_client.get_activity(activity_id=activity.id)
        print details
        csvLine =  str(details.start_date_local) + "," + str(details.distance) \
                + "," + str(details.total_elevation_gain) + "," + str(details.elapsed_time)
        activitieswriter.writerow([details.start_date_local.strftime("%x"), str(details.distance)[0:-1], str(details.total_elevation_gain)[0:-1],
                                  details.elapsed_time.seconds])

        print csvLine
        # print details.name
        # print unithelper.kilometers(details.distance)
        # print details.start_date_local
        # print details.elapsed_time
        # print details.calories
        # print details.type
        # print details.total_elevation_gain
        # print "------"

        date = details.start_date_local
        week = int(date.isocalendar()[1])
        print str(week) + "," + str(details.total_elevation_gain)

        elevation = details.total_elevation_gain
        print week
        try:
            elevation_per_week_array[week] = elevation_per_week_array[week] + int(elevation)
        except IndexError:
            elevation_per_week_array[int(week)] = int(elevation)

        # current_elevation = elevation_per_week.get(str(week), 0)

        # elevation_per_week[str(week)] = current_elevation + int(elevation)
        # print str(week) + ":" + str(elevation) + "," + str(elevation_per_week[str(week)])



        b = open('elevation.csv', 'w')
        a = csv.writer(b)

    cum_elevation_per_week_array = [0] * 52
    goal_elevation_per_week = [42200]
    last_week = 0

    for i in range (0, 52):
        if (elevation_per_week_array[i] > 0):
            last_week = i
        if (i > 0):
            cum_elevation_per_week_array[i] = cum_elevation_per_week_array[i-1] + elevation_per_week_array[i]
        else:
            cum_elevation_per_week_array[i] = elevation_per_week_array[i]

    print "last_week:" + str(last_week)
    for i in range (1,last_week):
        goal_elevation_per_week.append (42200 - cum_elevation_per_week_array[i])

    for i in range(0,len(goal_elevation_per_week)):
        print str(i) + ":" + str(goal_elevation_per_week[i])

    average_per_week = (42200 - goal_elevation_per_week[last_week-1]) / last_week
    estimated_total = goal_elevation_per_week[last_week-1] - (average_per_week * (52-last_week))

    goal_elevation_per_week.append(estimated_total)
    goal_elevation_per_week.append(0)

    weeks_axis = range(0,last_week) + [52,52]
    print len(weeks_axis)
    print len(goal_elevation_per_week)
    plt.ylim([0,42200])
    plt.xlim([0,52])

    plt.plot(np.array(weeks_axis), np.array(goal_elevation_per_week))
    plt.show()

    b.close()

    return strava_client.get_activity(activity_id=activity.id)

def main():
    # weeks_axis = range(0,5) + [52]
    # value_axis = [100,90,80,75,64,0]
    # print len(weeks_axis)
    # print len(value_axis)
    # plt.plot(np.array(weeks_axis), np.array(value_axis))
    # plt.show()
    last_activity = get_activities_from_strava()

if __name__ == '__main__':
   main()
