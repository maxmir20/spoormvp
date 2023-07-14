from rest_framework import serializers
from spoor.models import Playlist, Track, Profile


class PlaylistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Playlist
        fields = ('user', 'name', 'type', 'retrieval_id', 'retrieval_url', 'created_at')


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('title', 'artist', 'retrieval_id', 'redirect_url')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'last_track_url', 'live')


