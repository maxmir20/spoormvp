from rest_framework import serializers
from spoor.models import Playlist, Track, Profile


class PlaylistSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ('user_id', 'name', 'retrieval_id', 'retrieval_url')

    def get_user_id(self, playlist):
        return ProfileSerializer(playlist.user_id).data


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('title', 'artist', 'retrieval_id', 'redirect_url')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'last_track_url', 'live')



