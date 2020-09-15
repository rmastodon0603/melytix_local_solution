from Google_auth import auth_credentials

from googleapiclient.discovery import build


def get_site_list():
    webmasters_service = build('webmasters', 'v3', http=auth_credentials())
    site_list = webmasters_service.sites().list().execute()

    verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
                           if s['permissionLevel'] != 'siteUnverifiedUser'
                           and s['siteUrl'][:4] == 'http']
    return verified_sites_urls


def make_sc_request(site_uri, start_date, end_date):
    service = build('webmasters', 'v3', http=auth_credentials())
    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['date']
    }
    response = service.searchanalytics().query(siteUrl=site_uri, body=request).execute()
    return response
