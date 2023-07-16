from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponseBadRequest
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from spoor.models import Playlist
from spoor.serializers import PlaylistSerializer


@api_view(['POST'])
def add_playlist(request: Request, userID):
    """
    API Post Method to add a playlist to our ORM
    """
    if request.method != 'POST':
        return Response("Incorrect Method", status=405)

    # TODO authorize userID against header authorization token

    try:
        playlist_info = validate_playlist(request.data.get('playlist'))
    except HttpResponseBadRequest:
        return Response("Cannot validate playlist", status=400)

    # TODO need to validate playlist info

    print(playlist_info)

    # confirm playlist doesn't already exist
    try:
        #attempt to retrieve track (if it fails, create the track in except)
        Playlist.objects.get(retrieval_id=playlist_info.get("retrieval_id"))
        return Response("Playlist already exists", status=400)

    except Playlist.DoesNotExist:

        #retrieve user for serializer
        host = User.objects.get(pk=userID)
        user = host.profile
        print(user)
        print(model_to_dict(user))
        payload = {
            "user_id": user,
            **playlist_info
        }
        print("attempting to serialize object")
        serializer = PlaylistSerializer(data=payload)
        print(serializer)
        if serializer.is_valid():
            print("serializer is valid!")
            serializer.save(user=user)
            return Response(serializer.data, status=201)
        else:
            print("serializer is not valid!")
            print(playlist_info)
            return Response(serializer.data, status=400)
        pass
        # return HttpResponse("something went wrong trying to add track", status=400)


# TODO Delete Playlist



# helper functions
def validate_playlist(playlist_info: dict):
    return playlist_info
