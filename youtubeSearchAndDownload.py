# -*- coding: utf-8 -*-
import sys
import googleapiclient.discovery
import googleapiclient.errors
import os
import time
import hashlib
import requests
import json
import re
from pytube import YouTube
from concurrent.futures import ThreadPoolExecutor

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

DEVELOPER_KEY = 'AIzaSyBm16oaahziz3T814KWn4Y9cSMvypLleMY'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
interface = "https://service.iiilab.com/video/download"
clientID = "1866fa63122100dg"
clientSecretKey = "2d22b92f4d910d73c9ce48ed331a53b6"
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}

try:
    keyword = sys.argv[1]
except IndexError:
    print("命令错误")
    exit(0)
video_dir = "videoSrc"
save_path = os.path.join(os.path.dirname(__file__), video_dir)
save_path = os.path.join(save_path, keyword)


def filename_check(filename: str):
    pattern = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]')
    chinese = re.sub(pattern, '', filename)
    return chinese


def downloadVideo(videoUrl):
    timestamp = int(round(time.time() * 1000))
    tempStr = videoUrl + str(timestamp) + clientSecretKey
    sign = hashlib.md5(tempStr.encode('utf-8')).hexdigest()
    payload = dict(link=videoUrl, timestamp=timestamp, sign=sign, client=clientID)
    parse = requests.post(url=interface, headers=HEADERS, data=payload)
    dictObject = json.loads(parse.text)
    data = dictObject['data']['formats']
    filename = dictObject['data']['text']
    filename = filename_check(filename)
    it = iter(data)
    videoUrl = ""
    for x in it:
        if x['quality'] > 720:
            continue
        else:
            videoUrl = x['video']
            break
    temp = os.path.join(save_path, filename+'.mp4')
    cmd = "wget -O " + "\"" + temp + "\" " + "\"" + videoUrl + "\""
    if not os.path.exists(temp):
        os.popen(cmd)
    else:
        print("exists")


def download_by_pytube(videoUrl):
    yt = YouTube(videoUrl)
    yt.streams\
        .filter(progressive=True, file_extension='mp4')\
        .order_by('resolution')\
        .desc()\
        .first()\
        .download()


def searchByKeyword():

    os.environ['http_proxy'] = 'http://127.0.0.1:1080'
    os.environ['https_proxy'] = 'http://127.0.0.1:1080'
    youtube = googleapiclient.discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                              developerKey=DEVELOPER_KEY)
    search_response = youtube.search().list(
        q=keyword,
        part='snippet',
        maxResults=10,
        type='video',
        videoDuration='medium',
        order='viewCount'
    ).execute()
    videoUrlList = []
    for i in range(len(search_response['items'])):
        videoUrl = "https://www.youtube.com/watch?v=" + search_response['items'][i]['id']['videoId']
        # print(videoUrl)
        videoUrlList.append(videoUrl)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        pool.map(downloadVideo, videoUrlList)
        # pool.map(download_by_pytube, videoUrlList)


if __name__ == "__main__":
    searchByKeyword()
