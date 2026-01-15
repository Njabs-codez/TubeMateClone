from pytubefix import YouTube
from pathlib import Path
from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from tubeMate import merge_audio_to_video

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "in"
OUTPUT_DIR = BASE_DIR / "out"

app = FastAPI()

def validate_url(url):
    if "https://www.youtube.com/watch?v" in url or "https://youtu.be/" in url:
        return True
    return False

def download_and_merge(url, qual):
    yt = YouTube(url)
    try:
        yt.check_availability()
        
        video = yt.streams.filter(res=qual, mime_type="video/mp4", adaptive=True).first()
        audio = yt.streams.filter(only_audio=True, mime_type="audio/mp4", adaptive=True).order_by("abr").desc().first()
        
        print(video)
        video.download(str(INPUT_DIR))
        print("video download complete!!")
        
        print(audio)
        audio.download(str(INPUT_DIR))
        print("Audio download complete!!")
    
        files = []
        for file in INPUT_DIR.iterdir():
            if file.is_file():
                files.append(str(file))
        
        outName = f"{yt.title}({qual})"

        merge_audio_to_video(files[0], files[1], outName)

    except:
        print("An error occured")

@app.get("/get-video-info", status_code=200)
def video_info(url:str, res:Response):
    print(url)
    if not validate_url(url):
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message" : 
            "Invalid URL. Please ensure your URL is the formats:\n\t-https://www.youtube.com/watch?v=id\n\t-https://youtu.be/id"
        }
        
    yt = YouTube(url)
    return {
        "title" : yt.title,
        "channel" : yt.author,
        "thumbnail" : yt.thumbnail_url
    }


@app.get("/get-video", status_code=200)
def send_video(url:str, qual:str, res:Response):
    if not validate_url(url):
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message" : 
            "Invalid URL. Please ensure your URL is the formats:\n\t-https://www.youtube.com/watch?v=id\n\t-https://youtu.be/id"
        }
    
    # this will create the video, which will be found in the out file
    download_and_merge(url, qual) 



