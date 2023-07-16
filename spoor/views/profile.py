import base64
import json

import requests
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from personal_portfolio import settings
from django.shortcuts import render

from spoor.models import Credential, Profile, Playlist
from spoor.views import retrieve_track_from_spotify

SCOPE = ["user-read-currently-playing"]
# Create your views here.


@api_view(['GET'])
def get_current_track(request, userID = 1):
    """
      API endpoint to get either the currently playing track or posted playlists under user.
    """
    print('starting get current track')

    try:
        host = User.objects.get(id=userID)
    except User.DoesNotExist:
        print("failed to retrieve user")
        return Response('unable to retrieve user', status=400)

    if not host.profile.is_live():
        # TODO have this be a function
        # playlists = Playlist.objects.all()
        playlists = Playlist.objects.filter(user=host.profile).order_by("-created_at")
        # if not playlists:
        #     #TODO render no playlists found
        #     print('no playlists found')
        #     pass
        print(playlists)
        print(host.profile.name)
        print(list(playlists))

        #convert to list of dicts
        playlists_array = [model_to_dict(playlist) for playlist in playlists]
        print(playlists_array)

        context = {
            "user":
                {
                    "username": host.profile.name
                },
            "playlists": playlists_array
        }
        return render(request, 'user_playlists.html', context)


    else:
        # TODO temporarily use retrieve_track_from_spotify to update track
        retrieve_track_from_spotify(host)
        #return the host's last_track_url
        return HttpResponseRedirect(host.profile.last_track_url)


@api_view(['PUT'])
def update_session(request, userID):
    """
      API endpoint start or stop the session of a user.
    """
    try:
        # TODO validate user
        # TODO switch over to authorization header)
        profile = User.objects.get(pk=userID).profile
        # regardless of whether we're stopping or starting, we're going to want to make sure
        # this is clear
        profile.last_track_url = ""
        profile.save()
        print(f"Session is live: {profile.is_live()}")

        profile.flip_live()
        status = "Started" if profile.is_live() else "Ended"
        data = json.dumps({
            "status": f"Session {status}"
        })
        print(data)
        return Response(data=data, status=200)
    except User.DoesNotExist:
        return Response("Could not find user", status=400)



"""
V.0 Proof of concept stage (authorization takes place on Web App)
"""


# TODO depricate once we're doing spotify authorization in app
@api_view(['GET'])
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

# Helper functions
# def get_access_token(host_info):
#     print("running spoor access token method")
#
#     sp_oath = SpotifyOAuth(
#                 scope=SCOPE
#             )
#     print(sp_oath)
#     #Retrieve User's Access Token and Refresh Token using db
#     try:
#         print('attempting to retrieve credential')
#         credentials = Credential.objects.get(profile=host_info.profile.id)
#         # print(credentials)
#         # updated at greater than one hour
#         if (datetime.now() - credentials.updated_at.replace(tzinfo=None)).seconds // 3600 > 0:
#             print('refreshing token')
#             token_info = sp_oath.refresh_access_token(refresh_token=credentials.encrypted_token)
#             # print(f'old token was {credentials.encrypted_token}')
#             credentials.encrypted_token = token_info.get('refresh_token')
#             credentials.save()
#             # print(f'new token is {credentials.encrypted_token}')
#
#             access_token = token_info.get('access_token')
#         else:
#             print('less than one hour has passed')
#             access_token = sp_oath.get_access_token(as_dict=False)
#     except:
#         print("unable to find credentials")
#         token_info = sp_oath.get_access_token(as_dict=True)
#         print(f'adding new credentials {token_info}')
#         profile = Profile.objects.get(id=host_info.profile.id)
#         credentials = Credential(profile=profile, encrypted_token=token_info.get('refresh_token'))
#         credentials.save()
#         access_token = token_info.get('access_token')
#
#     # print(f'access token is {access_token}')
#     return access_token


    # refresh_token =
    #If expired, use refresh token by accessing cache


    # access_token = sp_oath.get_access_token(as_dict=False)
    # # access_token = sp_oath.refresh_access_token(refresh_token="AQA4Iu4cEpJv-z9ZGrd5OWfuTH5xU3nG8dkvzBF12NAKW7JzBxdBg-g0nRcNxLtpQU1YYEvXK-P0r63fpiTGguRzaK48AaiIMToe9rG6CIBjt5QL0QkDnl9c67qSte__4MM").get('access_token')
    # print(access_token)
    # return access_token
    # print(access_token)
    # get_current_track(access_token)


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

