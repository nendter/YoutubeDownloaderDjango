from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .youtube import download, any_to_mp3, add_metadata_to_mp3, downloadPlaylist, selectStream
from .serializers import InfoSerializer
from .data import data
from django.http import FileResponse
import os
from contextlib import contextmanager


class InfoAPI(APIView):
    def get(self, request, *args, **kwargs):
        url = request.query_params.get('url')
        playlist = request.query_params.get('playlist')
        if playlist == 'true':
            return Response(self.getPlaylistVideos(url))
        else:
            return Response([self.getVideo(url)])

    def getPlaylistVideos(self, url):
        yts = downloadPlaylist(url)
        videos = []
        for yt in yts:
            videos.append(self.getResFromYt(yt.watch_url, yt, selectStream(yt)))
        return videos;

    def getVideo(self, url):
        if url in data:
            yt, selectedStream = data[url]
        else:
            yt, selectedStream = download(url)
        return self.getResFromYt(url, yt, selectedStream)

    def getResFromYt(self, url, yt, selectedStream):
        data[url] = [yt, selectedStream]
        res = {
            'url': url,
            'id': yt.video_id,
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'artist': yt.author
        }
        return res


class PlaylistAPI(APIView):
    def get(self, request, *args, **kwargs):
        url = request.query_params.get('url')


class DownloadAPI(APIView):
    def get(self, request, *args, **kwargs):
        url = request.query_params.get('url')

        if url not in data:
            yt, selectedStream = download(url)
            data[url] = [yt, selectedStream]

        yt, selectedStream = data[url]

        file = selectedStream.download()
        target_name = yt.video_id + '.mp3'
        target_dir = 'out/' + target_name

        any_to_mp3(file, target_dir)
        os.remove(file)

        add_metadata_to_mp3(target_dir, yt.title, yt.author, yt.title, yt.thumbnail_url);

        response = FileResponse(open(target_dir, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="' + target_name + '"'

        with self.delete_file(target_dir):
            return response

    @contextmanager
    def delete_file(self, file_path):
        try:
            yield
        finally:
            os.remove(file_path)
