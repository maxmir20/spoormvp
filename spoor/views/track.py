import base64
from datetime import datetime

import requests
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from personal_portfolio import settings
from spoor.models import Track, Credential
from spoor.serializers import TrackSerializer


@api_view(['POST'])
def add_track(request: Request, userID):
    """
    API Post Method to add a track if it's not already in our record and update our user
    """
    if request.method != 'POST':
        return Response("Incorrect Method", status=405)


    #TODO authorize userID against header authorization token

    try:
        track_info = validate_track(request.data.get('track_info'))
    except HttpResponseBadRequest:
        return Response("Cannot validate track", status=400)

    # TODO need to validate that track info exists

    # update our profile track id
    try:
        redirect_url = track_info.get("redirect_url")
        user = User.objects.get(pk=userID)
        if user and user.profile.is_live():
            user.profile.last_track_url = redirect_url if redirect_url else user.profile.last_track_url
            user.profile.save(update_fields=['last_track_url'])
        else:
            return Response("user is not live, cannot update", status=400)
    except:
        return Response("failed to find/update user", status=400)


    # see if we need to add the track
    try:
        #attempt to retrieve track (if it fails, create the track in except)
        Track.objects.get(retrieval_id=track_info.get("retrieval_id"))
        return Response("Track already exists, no need to create", status=200)

    except Track.DoesNotExist:
        print("attempting to serialize object")
        serializer = TrackSerializer(data=track_info)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            print(track_info)
            return Response(serializer.data, status=400)
        # return HttpResponse("something went wrong trying to add track", status=400)


# helper functions
def validate_track(track_info: dict):
    return track_info



"""
V.0 Proof of concept stage (authorization takes place on Web App)
"""

# TODO Max soon to be deprecated once we get the spoor track posted
def retrieve_track_from_spotify(host: User):
    """
       This will use the Spotify API to retrieve the currently-playing-track of the user used stored Credentials
    """
    print('attempting to retrieve url')

    #retrieve Credential record
    try:
        credentials = Credential.objects.get(profile=host.profile.id)
    except Credential.DoesNotExist:
        # TODO eventually remove, hypothetically, we shouldn't ever get here
        print('no credentials found, authorize first')

        return Response('made it as far as token info')

    refreshed_token = None

    # if updated longer than one hour, refresh, otherwise, use access token
    print("checking if one hour has elapsed")
    print((datetime.now() - credentials.updated_at.replace(tzinfo=None)).total_seconds() // 3600 > 0)
    if (datetime.now() - credentials.updated_at.replace(tzinfo=None)).total_seconds() // 3600 > 0:
        # This function will update our credentials record if they are expired
        refreshed_token = refresh_token(credentials)
        print(f'just to check, new encrypted token is now {refreshed_token}')


    SPOTIFY_ACCESS_TOKEN = credentials.encrypted_token
    print(f'compared with the encypted token from credentials should be the same {SPOTIFY_ACCESS_TOKEN}')

    print(refreshed_token==SPOTIFY_ACCESS_TOKEN)

    if not SPOTIFY_ACCESS_TOKEN:
        return Response('Unable to retrieve access token')

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
        host.profile.last_track_url = current_track_info["track_url"]
        host.profile.save(update_fields=['last_track_url'])
    else:
        print("no track playing")
        return Response('no track playing')


def refresh_token(credentials):
    """
        This function uses the stored refresh token in Credential to request a reauthorized token for the Spotify API
        This new token will be saved over
    """
    print('refreshing token')
    #retrieving client id and secret from env and passing into Spotify Request Access Token API
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
        #refresh token not guaranteed to be returned
        credentials.encrypted_refresh = response.json().get('refresh_token', credentials.encrypted_refresh)
        credentials.save()
    except:
        print('failed to refresh tokens')
    return credentials.encrypted_token

