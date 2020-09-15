from facebook_business.api import FacebookAdsApi
from facebook_business import adobjects
from facebook_business.adobjects.adaccountuser import AdAccountUser
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.adreportrun import AdReportRun

from flask_login import current_user

from user import User

FACEBOOK_APP_ID = '217283073022581'
FACEBOOK_APP_SECRET = 'b85df256a9c94ed3dbf1b8b2069de149'


def get_me():
    FacebookAdsApi.init(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, User.get_fb_token(current_user.id))
    me = AdAccount(fbid='me')
    return me


def query_fb_analytics():
    params = {
        'time_range': {
            'since': "2018-12-02",
            'until': "2018-12-02"
        },
        'fields': [
            AdsInsights.Field.campaign_id,
            AdsInsights.Field.campaign_name,
            AdsInsights.Field.adset_name,
            AdsInsights.Field.ad_name,
            AdsInsights.Field.spend,
            AdsInsights.Field.impressions,
            AdsInsights.Field.clicks,
            AdsInsights.Field.buying_type,
            AdsInsights.Field.objective,
            AdsInsights.Field.actions
        ],
        'level': 'ad',
        'time_increment': 1
    }
    async_job = get_me().get_insights_async(fields=params.get('fields'), params=params)
    async_job.remote_read().get("async_percent_completion")
    result = async_job.get_result()
    print(result)
