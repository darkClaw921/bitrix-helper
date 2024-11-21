from pytube import YouTube
from pydub import AudioSegment
import ssl
from pprint import pprint

# Создание контекста SSL без проверки сертификатов
ssl._create_default_https_context = ssl._create_unverified_context
from pytube import YouTube 
import os
import re
from moviepy.editor import VideoFileClip, AudioFileClip
# where to save 
SAVE_PATH = "video/" #to_do 

class YouTubeDownloader:
    def __init__(self, url, output_path='downloads'):
        self.url = url
        self.output_path = output_path
        self.video_path = None
        self.audio_path = None
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
    def sanitize_filename(self, filename):
        return re.sub(r'[\\/*?:"<>|]', "", filename)
    def download_video(self):
        yt = YouTube(self.url)
        title = self.sanitize_filename(yt.title)
        video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
        self.video_path = os.path.join(self.output_path, f"{title}_video.mp4")
        video_stream.download(output_path=self.output_path, filename=f"{title}_video.mp4")
        print(f"Video downloaded to {self.video_path}")

    def download_audio(self):
        yt = YouTube(self.url)
        title = self.sanitize_filename(yt.title)
        audio_stream = yt.streams.filter(only_audio=True).first()
        self.audio_path = os.path.join(self.output_path, f"{title}_audio.mp4")
        audio_stream.download(output_path=self.output_path, filename=f"{title}_audio.mp4")
        print(f"Audio downloaded to {self.audio_path}")
    def combine_video_audio(self):
        if self.video_path and self.audio_path:
            video_clip = VideoFileClip(self.video_path)
            audio_clip = AudioFileClip(self.audio_path)

            final_clip = video_clip.set_audio(audio_clip)
            final_output_path = os.path.join(self.output_path, f"{os.path.splitext(os.path.basename(self.video_path))[0]}_final.mp4")
            final_clip.write_videofile(final_output_path, codec='libx264', audio_codec='aac')
            print(f"Final video with audio saved to {final_output_path}")

            os.remove(self.video_path)
            os.remove(self.audio_path)
            print("Temporary files removed.")
        else:
            print("Video or audio file is missing. Please download both before combining.")
    def download_and_combine(self):
        self.download_video()
        self.download_audio()
        self.combine_video_audio()
if __name__ == '__main__':
    url = input('Enter the link you want to download: ')
    downloader = YouTubeDownloader(url)
    downloader.download_and_combine()