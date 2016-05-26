#!/usr/bin/env python
import os, httplib, urllib
import csv
from datetime import datetime
from stravalib import Client
from stravalib.model import Activity
import matplotlib.pyplot as plt
import numpy as np

# Install oauth for python. On Ubuntu run: sudo apt-get install python-oauth
from oauth import oauth

ACCESS_TOKEN_STRING_FNAME = 'access_token.string'
STRAVA_ACCESS_TOKEN_STRING_FNAME = 'strava_access_token.string'
STRAVA_CLIENT_SECRET_STRING_FNAME = 'strava_client_secret.string'
STRAVA_CLIENT_CODE_STRING_NAME = 'strava_client_code.string'

# pass oauth request to server (use httplib.connection passed in as param)
# return response as a string
def fetch_response(oauth_request, connection, debug=False):
   url= oauth_request.to_url()
   connection.request(oauth_request.http_method,url)
   response = connection.getresponse()
   s=response.read()

   # print 'requested URL: %s' % url
   # print 'server response: %s' % s

   return s

def get_login_token():
    last_activity = None
    # auth_token = ""

    if not os.path.exists(STRAVA_ACCESS_TOKEN_STRING_FNAME):

        print '* Obtain a request token ...'
        strava_client = Client()
        # auth_url = strava_client.authorization_url(client_id='601', redirect_uri='http://127.0.0.1:5000/authorisation')

        client_secret = open(STRAVA_CLIENT_SECRET_STRING_FNAME).read().strip()
        print client_secret
        client_code = open(STRAVA_CLIENT_CODE_STRING_NAME).read().strip()
        print client_code

        auth_token = strava_client.exchange_code_for_token(client_id='601',
                                                           client_secret= client_secret,
                                                           code = client_code)

        print auth_token

        f = open(STRAVA_ACCESS_TOKEN_STRING_FNAME, 'w')
        f.write(auth_token)

    else:
        print '* Reading request token from file ...'
        f = open(STRAVA_ACCESS_TOKEN_STRING_FNAME)
        auth_token = f.read()

    f.close()

    print auth_token
    return auth_token


def get_activities_from_strava(strava_client):

    start_date = datetime(2016, 01, 01, 0, 0)
    activities = strava_client.get_activities(after=start_date)

    print "Activities.."
    print activities

    return activities

def calculate_elevation(activities, strava_client):
    elevation_per_week_array = [0] * 54

    existingActivities = {}
    try:
        activitiesfile = open('activities.csv', 'r')
        activitiesreader = csv.reader(activitiesfile)

        for line in activitiesreader:
            print "Ha:" + str(line[0])
            existingActivities[line[0]] = {"date":line[1],
                                           "distance":line[2],
                                           "elevation":line[3],
                                           "time":line[4]}

        activitiesfile.close()
    except IOError:
        #Don't worry if the file doesn't exist, it'll be created next
        print "sweet nothing"

    activitiesfile = open('activities.csv', 'ab+')
    activitieswriter = csv.writer(activitiesfile)


    for activity in activities:
        try:
            print "--- Existing activity:" + str(activity.id)
            existingActivities[str(activity.id)]
        except KeyError:
            print "--- Adding new activity:" + str(activity.id)
            details = strava_client.get_activity(activity_id=activity.id)
            csvLine = [str(activity.id), details.start_date_local.strftime("%x"), str(details.distance)[0:-2], str(details.total_elevation_gain)[0:-2],
                                      details.elapsed_time.seconds]
            print csvLine
            activitieswriter.writerow(csvLine)

            existingActivities[str(activity.id)] = {"date":details.start_date_local.strftime("%x"),
                                            "distance":str(details.distance)[0:-2],
                                            "elevation":str(details.total_elevation_gain)[0:-2],
                                            "time":str(details.elapsed_time.seconds)}
    activitiesfile.close()

    for key, activity in existingActivities.iteritems():
        date = datetime.strptime(activity['date'],'%x')
        week = int(date.isocalendar()[1])
        print str(week) + "," + activity['elevation']

        try:
            elevation_per_week_array[week] = elevation_per_week_array[week] + int(activity['elevation'][0:-3])
        except IndexError:
            elevation_per_week_array[int(week)] = int(activity['elevation'][0:-3])


        cum_elevation_per_week_array = [0] * 52
        goal_elevation_per_week = [42200]
        last_week = 0

        for i in range (0, 52):
            if (elevation_per_week_array[i] > 0):
                last_week = i + 1
            if (i > 0):
                cum_elevation_per_week_array[i] = cum_elevation_per_week_array[i-1] + elevation_per_week_array[i]
            else:
                cum_elevation_per_week_array[i] = elevation_per_week_array[i]

        print "last_week:" + str(last_week)
        for i in range (1,last_week):
            goal_elevation_per_week.append (42200 - cum_elevation_per_week_array[i])

        for i in range(0,len(goal_elevation_per_week)):
            print str(i) + ":" + str(goal_elevation_per_week[i])


    return goal_elevation_per_week

# def plot_graph(goal_elevation_per_week, last_week):
#     weeks_axis = range(0,len(goal_elevation_per_week) - 1) + [52]
#     print len(weeks_axis)
#     print len(goal_elevation_per_week)
#     plt.ylim([0,42200])
#     plt.xlim([0,52])
#
#     plt.plot(np.array(weeks_axis), np.array(goal_elevation_per_week))
#     plt.show()

def plot_graph(goal_elevation_per_week):
    weeks_axis = range(0,len(goal_elevation_per_week))
    print "---"
    print weeks_axis
    print "---"
    print goal_elevation_per_week
    print "---"
    print len(weeks_axis)
    print len(goal_elevation_per_week)
    plt.ylim([0,42200])
    plt.xlim([0,52])

    plt.plot(np.array(goal_elevation_per_week))

    last_week = len(goal_elevation_per_week)
    average_per_week = (42200 - goal_elevation_per_week[last_week-1]) / last_week
    estimated_total = goal_elevation_per_week[last_week-1] - (average_per_week * (52-last_week))

    x = [last_week - 1, 52]
    y = [goal_elevation_per_week[-1],estimated_total]
    plt.plot(x, y, linestyle="dashed", color="green")
    # goal_elevation_per_week.append(estimated_total)
    # goal_elevation_per_week.append(0)


    plt.show()

def main():
    # weeks_axis = range(0,5) + [52]
    # value_axis = [100,90,80,75,64,0]
    # print len(weeks_axis)
    # print len(value_axis)
    # plt.plot(np.array(weeks_axis), np.array(value_axis))
    # plt.show()
    strava_client = Client(access_token=get_login_token())
    activities = get_activities_from_strava(strava_client)
    goal_elevation_per_week = calculate_elevation(activities, strava_client)
    plot_graph(goal_elevation_per_week)

if __name__ == '__main__':
   main()
