"""A general utils module for doing a bunch of useful stuff"""


def prep_dash_metrics(ga_data: list = None, sc_data: list = None, yt_data: list = None):
    metrics = {
        'ga_sessions': [],
        'ga_users': [],
        'ga_pageViews': [],
        'ga_pageViewsPerSession': [],
        'ga_avgSessionDuration': [],
        'ga_bounces': [],
        'ga_percentNewSessions': [],
        'ga_user_dates': [],
        'ga_NewUser': [],
        'ga_ReturningUser': [],
        'ga_dates': [],
        'sc_clicks': [],
        'sc_impressions': [],
        'sc_ctr': [],
        'sc_position': [],
        'sc_dates': [],
        'yt_dates': [],
        'yt_estimatedMinutesWatched': [],
        'yt_views': [],
        'yt_likes': [],
        'yt_subscribersGained': [],
        'yt_dislikes': []
    }
    for x in ga_data['reports'][0]['data']['rows']:
        metrics['ga_dates'].append(str(
            x['dimensions'][0][0:4] + "-" + x['dimensions'][0][4:6] + "-" +
            x['dimensions'][0][6:8]))
        metrics['ga_sessions'].append(int(x['metrics'][0]['values'][0]))
        metrics['ga_users'].append(int(x['metrics'][0]['values'][1]))
        metrics['ga_pageViews'].append(int(x['metrics'][0]['values'][2]))
        metrics['ga_pageViewsPerSession'].append(float(x['metrics'][0]['values'][3]))
        metrics['ga_avgSessionDuration'].append(float(x['metrics'][0]['values'][4]))
        metrics['ga_bounces'].append(int(x['metrics'][0]['values'][5]))
        metrics['ga_percentNewSessions'].append(float(x['metrics'][0]['values'][6]))

    UsersTypesTemp = {
        'new_users_dates': [],
        'new_users': [],
        'ret_users_dates': [],
        'ret_users': []
    }
    for x in ga_data['reports'][1]['data']['rows']:
        if x['dimensions'][0] == 'New Visitor':
            UsersTypesTemp['new_users_dates'].append(int(x['dimensions'][1]))  # 20200403 - int
            UsersTypesTemp['new_users'].append(int(x['metrics'][0]['values'][0]))
        else:
            UsersTypesTemp['ret_users_dates'].append(int(x['dimensions'][1]))
            UsersTypesTemp['ret_users'].append(int(x['metrics'][0]['values'][0]))

    metrics['ga_dates'] = UsersTypesTemp['new_users_dates'] + UsersTypesTemp['ret_users_dates']
    metrics['ga_dates'].sort()  # sort by date
    metrics['ga_dates'] = list(dict.fromkeys(metrics['ga_dates']))  # remove duplicates

    for date in metrics['ga_dates']:
        for x in ga_data['reports'][0]['data']['rows']:
            if date == x['dimensions'][0]:  # looking for same dates
                if x['dimensions'][0] == 'New Visitors':
                    metrics['NewUser'].append(int(x['metrics'][0]['values'][0]))
                else:
                    metrics['NewUser'].append(0)
                if x['dimensions'][0] == "Returning Visitor":
                    metrics['ReturningUser'].append(int(x['metrics'][0]['values'][0]))
                else:
                    metrics['ReturningUser'].append(0)
    print(UsersTypesTemp)
    # TODO: make combine 4 lists into 3 lists

    for x in sc_data['rows']:
        metrics['sc_dates'].append(x['keys'][0])
        metrics['clicks'].append(x['clicks'])
        metrics['impressions'].append(x['impressions'])
        metrics['ctr'].append(x['ctr'])
        metrics['position'].append(x['position'])

    print(metrics)
    print(make_a_prediction(metrics['sessions'], metrics['ga_dates']))
    return metrics


def make_a_prediction(data, time_frame):
    count = 0
    avg = 0
    for time in range(len(time_frame)):
        avg += data[time]
        count += 1
    prediction = abs(avg / count)
    return prediction


def checkedboxed_to_scope(checkedboxed: list) -> list:
    """Turns ['ga', 'sc','yt'] into a Auth.SCOPE list"""
    SCOPE = ['openid', 'email', 'profile']  # deafault scopes
    for system in checkedboxed:
        if system == 'ga':
            SCOPE.append('https://www.googleapis.com/auth/analytics.readonly')
        elif system == 'sc':
            SCOPE.append('https://www.googleapis.com/auth/webmasters.readonly')
        elif system == 'yt':
            SCOPE.append(
                'https://www.googleapis.com/auth/yt-analytics.readonly')
            SCOPE.append(
                'https://www.googleapis.com/auth/youtube.readonly'
            )
    return SCOPE
