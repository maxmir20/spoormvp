import datetime
from uuid import UUID

import requests
import spotipy
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spotipy.oauth2 import SpotifyOAuth
from personal_portfolio import settings
from django.shortcuts import render

from spoor.models import Credential

CLIENT_ID = settings.SPOTIPY_CLIENT_ID
CLIENT_SECRET = settings.SPOTIPY_CLIENT_SECRET
REDIRECT_URI = settings.SPOTIPY_REDIRECT_URI
SCOPE = ["user-read-currently-playing"]
# Create your views here.
def get_access_token(host_info):
    sp_oath = SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE
            )
    print(sp_oath)
    #Retrieve User's Access Token and Refresh Token using db
    try:
        credentials = Credential.objects.get(profile=host_info.profile.id)
        # print(credentials)
    except:
        print("unable to find credentials")
        return None
    print(f'created_at is {credentials.created_at}')
    if credentials.updated_at:
        print(f'updated_at is {credentials.updated_at}')
        # print(f'tz aware updated: {credentials.updated_at.tzinfo}')
        # print(f'tz aware now: {datetime.datetime.utcnow().tzinfo}')

        delta = datetime.datetime.now() - credentials.updated_at.replace(tzinfo=None)
        print(delta)
        if delta.seconds//3600 > 0:
            print('refreshing token')
            token_info = sp_oath.refresh_access_token(refresh_token=credentials.encrypted_token)
            # print(f'old token was {credentials.encrypted_token}')
            credentials.encrypted_token = token_info.get('refresh_token')
            credentials.save()
            # print(f'new token is {credentials.encrypted_token}')

            access_token = token_info.get('access_token')
        else:
            print('less than one hour has passed')
            access_token = sp_oath.get_access_token(as_dict=False)
    else:
        print('no updated_at')
        access_token = sp_oath.get_access_token(as_dict=False)
    # print(f'access token is {access_token}')
    return access_token


    # refresh_token =
    #If expired, use refresh token by accessing cache


    # access_token = sp_oath.get_access_token(as_dict=False)
    # # access_token = sp_oath.refresh_access_token(refresh_token="AQA4Iu4cEpJv-z9ZGrd5OWfuTH5xU3nG8dkvzBF12NAKW7JzBxdBg-g0nRcNxLtpQU1YYEvXK-P0r63fpiTGguRzaK48AaiIMToe9rG6CIBjt5QL0QkDnl9c67qSte__4MM").get('access_token')
    # print(access_token)
    # return access_token
    # print(access_token)
    # get_current_track(access_token)

@api_view(['GET'])
def get_current_track(request, userID = 1):
    """
       API endpoint to get either the currently playing track or posted playlists.
   """
    #use UserID to retrieve User record + Credential
    #validate user is live
    #retrieve Credential record
    #if updated longer than one hour, refresh, otherwise, use access token
    #get_current_track
    #(stretch, add track to index db for easier reference)
    #return HTTPResponseRedirect
    # userID = request.query_params.get('id', userID)
    print(userID)
    try:
        host = User.objects.get(id=userID)
    except:
        print("failed to retrieve user")
        return Response('Unable to retrieve user')

    # if not check_access_token(SPOTIFY_ACCESS_TOKEN):
    #     SPOTIFY_ACCESS_TOKEN = refresh_access_token(SPOTIFY_ACCESS_TOKEN)

    SPOTIFY_ACCESS_TOKEN = get_access_token(host)

    if not SPOTIFY_ACCESS_TOKEN:
        return Response('Unable to retrieve access token')

    #current track if live
    if host.profile.live:
        print("host is live")
        url = 'https://api.spotify.com/v1/me/player/currently-playing'
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"
            }
        )
        current_track_info = {}
        if response.status_code == 200:
            resp_json = response.json()
            current_track_info["track_name"] = resp_json.get('item', {}).get('name')
            current_track_info["track_artist"] = resp_json.get('item', {}).get('artists', [])
            current_track_info["track_url"] = resp_json.get('item', {}).get('external_urls', {}).get('spotify')
            print(current_track_info)
            return HttpResponseRedirect(current_track_info["track_url"])
        else:
            print("no track playing")
            return Response('no track playing')

    else:
        #return list of public playlists
        return Response('returning public playlists')

def main():
    current_track_info = get_current_track()
    # track_name = current_track_info.get('item', {}).get('name')
    # track_url = current_track_info.get('item', {}).get('external_urls', {}).get('spotify')
    print(current_track_info)


if __name__ == '__main__':
    print('hello_world')
    # get_access_token()
    get_current_track()
    # main()
    # code = get_access_token()
    # print(code)