from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from spoor.models import Track
from spoor.serializers import TrackSerializer


@api_view(['POST'])
def add_track(request: Request, userID):
    """
    API Post Method to add a track if it's not already in our record and update our user
    """
    if request.method != 'POST':
        return Response("Incorrect Method", status=405)

    try:
        track_info = validate_track(request.data.get('track_info'))
    except HttpResponseBadRequest:
        return Response("Cannot validate track", status=400)

    #need to validate that track info exists


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
        return Response(status=200)

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



