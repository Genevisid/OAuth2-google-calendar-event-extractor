from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
import google.oauth2.credentials
import google_auth_oauthlib.flow
import os
import googleapiclient.discovery
red_url='http://127.0.0.1:8000/rest/v1/calendar/redirect'
CLIENT_SECRETS_FILE = "/home/geneviptop/PycharmProjects/djangoinitial/gcal/gcal/credentials.json"
scope_list=['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/userinfo.email','openid']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
@api_view(['GET'])
def GoogleCalendarInitView(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE,scopes=scope_list)
    flow.redirect_uri = red_url
    authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
    request.session['state'] = state
    return Response({"authorization_url": authorization_url})
@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    state = request.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE,scopes=scope_list,state=state)
    flow.redirect_uri = red_url
    flow.fetch_token(authorization_response=request.get_full_path())
    cred=flow.credentials
    cred_dict={'token': cred.token,'token_uri': cred.token_uri,'refresh_token': cred.refresh_token,'client_id': cred.client_id,'client_secret': cred.client_secret,'scopes': cred.scopes}
    request.session['credentials']=cred_dict
    if 'credentials' not in request.session:
        return redirect('rest/v1/calendar/init')
    credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])
    service = googleapiclient.discovery.build('calendar','v3', credentials=credentials)
    calendar_list = service.calendarList().list().execute()
    calendar_id = calendar_list['items'][0]['id']
    events = service.events().list(calendarId=calendar_id).execute()
    events_list_append = []
    if not events['items']:
        return Response({"message":"no events were found"})
    else:
        for events_list in events['items']:
            events_list_append.append(events_list)
            return Response({"events": events_list_append})