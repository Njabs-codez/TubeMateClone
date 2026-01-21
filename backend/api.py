from pytubefix import YouTube
from pathlib import Path
from fastapi import FastAPI, Response, status
from fastapi.responses import StreamingResponse
from tubeMate import merge_audio_to_video, MergeError
from fastapi.middleware.cors import CORSMiddleware
import os


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "in"
OUTPUT_DIR = BASE_DIR / "out"

app = FastAPI()
origins = [os.getenv('FRONTEND_URL', 
                     'http://localhost:5173'),
            "http://localhost:3000",
            "http://frontend:3000"]


app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

def validate_url(url):
    if "https://www.youtube.com/watch?v" in url or "https://youtu.be/" in url:
        return True
    return False

@app.get('/api')
def hello_world():
    return {"greetings" : "Hello, World!"}

@app.get("/api/get-video-info", status_code=200)
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

def download_and_merge(url, qual) -> str:
    yt = YouTube(url)
    try:
        yt.check_availability()
        
        video = yt.streams.filter(res=qual, mime_type="video/mp4", adaptive=True).first()
        audio = yt.streams.filter(only_audio=True, mime_type="audio/mp4", adaptive=True).order_by("abr").desc().first()
        
        outName = f"{yt.title}({qual})"
        in_dir = INPUT_DIR / outName
        print(video)
        video.download(str(in_dir))
        print("video download complete!!")
        
        print(audio)
        audio.download(str(in_dir))
        print("Audio download complete!!")
    
        files = []
        for file in in_dir.iterdir():
            if file.is_file():
                files.append(str(file))

        merge_audio_to_video(files[0], files[1], outName)

        return outName

    except MergeError as e:
        print("An error occured")
        raise e

def outFile_generator(fileName:str):
    file_dir = OUTPUT_DIR / fileName
    try:
        for file in file_dir.iterdir():
            with open(str(file), mode="rb") as out:
                while chunk := out.read(1024*1024):
                    yield chunk

    finally:
        for item in file_dir.iterdir():
            if item.is_file():
                item.unlink()
        file_dir.rmdir()

@app.get("/api/get-video", status_code=200)
def send_video(url:str, qual:str, res:Response):
    if not validate_url(url):
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message" : 
            "Invalid URL. Please ensure your URL is the formats:\n\t-https://www.youtube.com/watch?v=id\n\t-https://youtu.be/id"
        }
    
    try:
        # this will create the video, which will be found in the out file
        fileName = download_and_merge(url, qual) 
        
        # uses the generator function to stream the file to 
        return StreamingResponse(outFile_generator(fileName), 
                                media_type="video/mp4", 
                                headers={
                                    "Content-Disposition" : f'attachment; filename="{fileName}"',
                                    "Accept-Ranges" : "bytes"
                                })
    except MergeError as e:
        print("Check merge_audio_to_video twinnem")
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message" : "something went wrong while retrieving your video"
        }
    
    

    


