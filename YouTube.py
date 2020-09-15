from googleapiclient.discovery import build

from Google_auth import auth_credentials

from flask import session

from math import ceil


# TODO: For now this only works with one account - one chanel system. Not with Content owner - multiple accounts.


class Channel:
    """Youtube chanel class for yt data api v3"""
    def __init__(self, name: str, picture: str, uploads: str, stats: list):
        """:parameter name(str): the name of the chanel,
           :parameter picture(str): the lick to a profile picture of the channel,
           :parameter uploads(str): a id str to a uploads playlist,
           :parameter stats(dict): a dict of channel stats*
           *stats(viewCount : int, commentCount : int, subscriberCount : int, hiddenSubscriberCount : bool, videoCount : int)"""
        self.name = name,
        self.pic = picture,
        self.videos_playlist = uploads
        self.stats = stats


def yt_fill_chanel_class():
    reporting_api = build(serviceName='youtube', version='v3', http=auth_credentials())
    chanel_list = yt_get_chanel(reporting_api)
    print(chanel_list)
    name = yt_get_title(chanel_list)
    picture = yt_get_chanel_pic(chanel_list)
    vid_playlist = utils_get_uploads(chanel_list)
    stats = utils_get_statistics(chanel_list)
    channel = Channel(name, picture, vid_playlist, stats)
    print("YT ------- \n", channel.name, '\n', channel.pic, '\n', channel.videos_playlist, '\n', channel.stats, '\n')
    return channel


def yt_get_chanel(reporting_api):
    """Calls the yt data api channels().list to retrieve a list of channels for this token"""
    response = reporting_api.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    ).execute()
    return response


def yt_get_title(chanel_list):
    """Gets a chanel name from chanel_list returned from yt_get_chanel()
    :param chanel_list: the response from google data api call channels().list"""
    return chanel_list['items'][0]['snippet']["title"]


def yt_get_chanel_pic(chanel_list):
    """Get the yt profile picture as a str link
    :param chanel_list: the response from google data api call channels().list"""
    return chanel_list['items'][0]['snippet']['thumbnails']['medium']['url']


def utils_get_uploads(chanel_list):
    """Goes trough the chanel json list and gets uploads
        uploads is a yt playlist that contains all users videos
        :param chanel_list: See yt_get_chanel() function
        :return A list containing multiple playlists ids or a str of one playlist id"""
    if len(chanel_list['items']) > 1:
        uploads = []
        for chanel in chanel_list['items']:
            uploads.append(chanel['contentDetails']['relatedPlaylists']['uploads'])
        return uploads
    else:
        upload = chanel_list['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return upload


def utils_get_statistics(chanel_list):
    """Goes trough the chanel json list and gets chanel statistics
        statistics(viewCount, commentCount, subscriberCount, hiddenSubscriberCount : bool, videoCount)
        :param chanel_list: See yt_get_chanel() function
        :return A list containing multiple dicts of stats or a dict of stats for one acc"""
    if len(chanel_list) > 1:
        stats = []
        for chanel in chanel_list['items']:
            stats.append(chanel['statistics'])
            return stats
    else:
        stats = chanel_list['items'][0]['statistics']
        return stats


def get_dash_yt_metrics(start_date: str, end_date: str):
    reporting_api = build(serviceName='youtube', version='v3', http=auth_credentials())
    chanel = yt_fill_chanel_class()
    videos = get_all_channel_videos(reporting_api, chanel.videos_playlist)
    response = get_videos_analytics(videos, '2020-05-01', '2020-05-26')  # session['start_date'], session['end_date'])
    return response


def get_videos_analytics(videos, start_date, end_date):
    """Youtube analytics query by two dates from and to
        :param videos: a videos dict created in get_all_channel_videos() is a list of dicts('title','thumbnail', 'id')
        :param start_date: the start of the report
        :param end_date: the end of the report"""
    # videos_str = utils_convert_videos_to_str(videos)
    api_service = build(serviceName='youtubeAnalytics', version='v2', http=auth_credentials())
    response = api_service.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        filters="",  # video=={}".format(videos_str),  # TODO: if the string will contain more than 200 ids it will break. Write a for loop of API requests.
        metrics='estimatedMinutesWatched,views,likes,subscribersGained,dislikes',
        dimensions='day',
        sort='day'
    ).execute()
    return response


def utils_convert_videos_to_str(videos):
    """Converts the video list containing into a str.
       :param videos: list containing dicts('title', 'thumbnail' and 'id' of an video)
       :return filter_str: separated with a comma like suck vid_id,vid_id2,vid_id3. Max videos ids in one string can 200"""
    videos_str = ""
    for _id in videos:
        videos_str = str(videos_str + "," + _id['id'])  # TODO: do another way of conversion. I don't think this is ideal.
    videos_str = videos_str.replace(",", "", 1)  # was ",id,id,id" became "id,id,id"
    print(videos_str)
    return videos_str


def get_all_channel_videos(reporting_api, upload_playlist):
    """With uploads id(url) trough playlistItems().list gets a list of all videos
    :param reporting_api: an youtube api object
    :param upload_playlist: a id str of channel all uploaded videos
    :return a list of dicts were each dict contains a 'title', 'thumbnail' and 'id' of an video"""

    response = reporting_api.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=upload_playlist
    ).execute()

    videos = []
    for video in range(response['pageInfo']['totalResults']):
        videos.append({
            "title": response['items'][video]['snippet']['title'],
            "thumbnail": response['items'][video]['snippet']['thumbnails']['medium']['url'],
            "id": response['items'][video]['contentDetails']['videoId']
        })

    try:
        if response["pageInfo"]:  # If there is more than 50 videos on the chanel
            next_request_page_token = response['nextPageToken']  # get the next page token for the next request

            for request in range(ceil(response['pageInfo']['totalResults'])):  # Ignore if works
                response = reporting_api.playlistItems().list(
                    part="snippet,contentDetails",
                    pageToken=next_request_page_token,
                    maxResults=50,
                    playlistId=upload_playlist
                ).execute()
                next_request_page_token = response['nextPageToken']
                for video in range(len(response['pageInfo']['totalResults'])):  # add all videos to a videos list as a dict
                    videos.append({
                        "title": response['items'][video]['snippet']['title'],
                        "thumbnail": response['items'][video]['snippet']['thumbnails']['medium']['url'],
                        "id": response['items'][video]['contentDetails']['videoId']
                    })
            return videos
        print("videos ", videos)
    except KeyError:
        print("videos ", videos)
        return videos


def yt_analytics_query(start_date, end_date):
    """Youtube analytics query by two dates from and to
        :param start_date: the start of the report
        :param end_date: the end of the report"""
    api_service = build(serviceName='youtubeAnalytics', version='v2', http=auth_credentials())
    response = api_service.reports().query(
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='estimatedMinutesWatched,views,likes,subscribersGained',
        dimensions='day',
        sort='day'
    ).execute()

    return response
