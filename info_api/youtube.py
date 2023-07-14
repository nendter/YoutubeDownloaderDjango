from pytube import YouTube, Playlist


def download(url):
    yt = YouTube(url)
    selectedStream = selectStream(yt)
    return (yt, selectedStream)


def selectStream(yt):
    audioStreams = yt.streams.filter(only_audio=True)
    if len(audioStreams) == 0:
        raise Exception('No Audio-Streams available')

    selectedStream = audioStreams[0]
    for stream in audioStreams:
        if int(stream.abr[:-4]) > int(selectedStream.abr[:-4]):
            selectedStream = stream

    return selectedStream


def downloadPlaylist(url):
    pl = Playlist(url)
    return pl.videos


from pydub import AudioSegment
import ffmpeg
import os

def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension[1:]

def any_to_mp3(input_file, output_file):
    audio = AudioSegment.from_file(input_file, format=get_file_extension(input_file))
    audio.export(output_file, format='mp3')


from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
import requests

def add_metadata_to_mp3(file_path, title, artist, album, image_url):
    # Open the MP3 file and load the existing metadata (if any)
    audio = ID3(file_path)

    # Set the title, artist, and album metadata tags
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["TALB"] = TALB(encoding=3, text=album)

    response = requests.get(image_url)
    if response.status_code != 200:
        print('Failed to download the image:', response.status_code)
        return

    # Set the cover image (APIC) metadata tag
    image_data = response.content
    audio['APIC'] = APIC(
        encoding=3,
        mime='image/jpeg',  # Adjust mime type as per your image format
        type=3,  # 3 is for album front cover
        desc='Cover',
        data=image_data
    )

    # Save the updated metadata to the MP3 file
    audio.save()
