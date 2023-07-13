import base64
from datetime import datetime, timedelta
import socket
import jwt
from time import time
from uuid import UUID

import requests
import spotipy
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
import environ
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spotipy.oauth2 import SpotifyOAuth
from personal_portfolio import settings
from django.shortcuts import render

from spoor.models import Credential, Profile

SCOPE = ["user-read-currently-playing"]
# Create your views here.
def get_access_token(host_info):
    print("running spoor access token method")

    sp_oath = SpotifyOAuth(
                scope=SCOPE
            )
    print(sp_oath)
    #Retrieve User's Access Token and Refresh Token using db
    try:
        print('attempting to retrieve credential')
        credentials = Credential.objects.get(profile=host_info.profile.id)
        # print(credentials)
        # updated at greater than one hour
        if (datetime.now() - credentials.updated_at.replace(tzinfo=None)).seconds // 3600 > 0:
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
    except:
        print("unable to find credentials")
        token_info = sp_oath.get_access_token(as_dict=True)
        print(f'adding new credentials {token_info}')
        profile = Profile.objects.get(id=host_info.profile.id)
        credentials = Credential(profile=profile, encrypted_token=token_info.get('refresh_token'))
        credentials.save()
        access_token = token_info.get('access_token')

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

def authorize_spotify_user(request, userID):
    print('starting spotify authorization')
    url = 'https://accounts.spotify.com/authorize'
    params = {
        'response_type': 'code',
        'client_id': settings.CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': settings.REDIRECT_URI,
    }
    spotify_request = requests.get(url=url, params=params)
    print(spotify_request.url)
    return HttpResponseRedirect(spotify_request.url)


def generate_apple_developer_token(keyID, teamID):

    # # Initialise environment variables
    # env = environ.Env()
    # environ.Env.read_env()
    #
    # keyID = env('APPLE_KEY_ID')
    # teamID = env('APPLE_TEAM_ID')
    # privateKey = env('APPLE_PRIVATE_KEY')

    dt = datetime.now() + timedelta(days=180)

    headers = {
        "alg": "ES256",
        "kid": keyID,
        "typ": "JWT",
    }

    payload = {
        "iss": teamID,
        "iat": int(time()),
        "exp": "180d",
    }

    with open("/Users/maxingraham-rakatansky/Downloads/AuthKey_2X9R4HXF34.p8", "rb") as fh:  # Add your file
        signing_key = fh.read()

    gen_jwt = jwt.encode(payload, signing_key, algorithm="ES256", headers=headers)

    print(f"[JWT] {gen_jwt}")

def request_access_token(request):
    print('now that we have our callback, request access token')
    print(request)
    print(request.GET)

    auth_header = base64.urlsafe_b64encode((settings.CLIENT_ID + ':' + settings.CLIENT_SECRET).encode())
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": f"Basic {auth_header.decode('ascii')}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'redirect_uri': settings.REDIRECT_URI
    }
    response = requests.post(url=url, params=params, headers=headers)

    if response.status_code == 200:
        print(response.json())
    token_info = response.json()
    #hardcode to deal with deadline
    profile = Profile.objects.get(id=1)
    credentials = Credential(
        profile=profile,
        encrypted_token=token_info.get('access_token'),
        encrypted_refresh=token_info.get('refresh_token')
    )
    credentials.save()
    return HttpResponse('authorized and created credential record')

def refresh_token(request, credentials):
    print('refreshing token')
    auth_header = base64.urlsafe_b64encode((settings.CLIENT_ID + ':' + settings.CLIENT_SECRET).encode())
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": f"Basic {auth_header.decode('ascii')}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': credentials.encrypted_refresh
    }
    response = requests.post(url=url, params=params, headers=headers)
    print(response.json())
    # update credentials
    try:
        credentials.encrypted_token = response.json()['access_token']
        credentials.encrypted_refresh = response.json()['refresh_token']
        credentials.save()
    except:
        print('failed to refresh tokens')
    return credentials.encrypted_token

@api_view(['GET'])
def get_current_track(request, userID = 1):
    print('starting get current track')
    """
       API endpoint to get either the currently playing track or posted playlists under user.
    """
    #use UserID to retrieve User record + Credential
    print(userID)
    try:
        host = User.objects.get(id=userID)
    except:
        print("failed to retrieve user")
        return Response('Unable to retrieve user')

    print('attempting to retrieve url')
    # print(socket.getfqdn())
    print(request)
    #retrieve Credential record
    try:
        credentials = Credential.objects.get(profile=host.profile.id)
    except ObjectDoesNotExist:
        print('no credentials found, authorize first')

        return Response('made it as far as token info')
        # profile = Profile.objects.get(id=host.profile.id)
        # credentials = Credential(profile=profile, encrypted_token=token_info.get('access_token'))
        # credentials.save()
        # access_token = token_info.get('access_token')

    refreshed_token = None
    # if updated longer than one hour, refresh, otherwise, use access token
    if (datetime.now() - credentials.updated_at.replace(tzinfo=None)).seconds // 3600 > 0:
        #refresh token
        refreshed_token = refresh_token(request, credentials)
        print(f'just to check, new encrypted token is now {refreshed_token}')




    # SPOTIFY_ACCESS_TOKEN = get_access_token(host)
    SPOTIFY_ACCESS_TOKEN = credentials.encrypted_token
    print(f'compared with the encypted token from credentials should be the same {SPOTIFY_ACCESS_TOKEN}')

    print(refreshed_token==SPOTIFY_ACCESS_TOKEN)

    if not SPOTIFY_ACCESS_TOKEN:
        return Response('Unable to retrieve access token')

    # validate user is live
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