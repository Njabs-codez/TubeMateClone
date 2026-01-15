from pytubefix import YouTube
import subprocess
from pathlib import Path
from fastapi.responses import FileResponse, StreamingResponse

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "in"
OUTPUT_DIR = BASE_DIR / "out"

class MergeError(Exception):
    pass


def clearInDir(in_dir: Path):
    for item in in_dir.iterdir():
        if item.is_file():
            item.unlink()
    in_dir.rmdir()

def merge_audio_to_video(vid, aud, outname):
    out = OUTPUT_DIR / outname / f"{outname}.mp4"

    command = [
        'ffmpeg.exe', '-i', vid,
        '-i', aud, '-c:v', 'libx264', '-pix_fmt',
        'yuv420p','-c:a', 'copy', str(out)
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("Something went wrong with FFmpeg function")
        raise subprocess.CalledProcessError()
    except:
        print("Likely file not found twin")
        raise MergeError("Something went wrong with the merge_audio_to_video function.")
    finally:
        to_clear: Path = INPUT_DIR / outname
        clearInDir(to_clear)


def main():
    print("==========================TubeMate Clone==============================")

    while True:
        print("Please enter the URL below: ")
        url = input()

        while "https://www.youtube.com/watch" not in url and "https://youtu.be/" not in url:
            print("invalid url, please try again: ")
            url = input()

        yt = YouTube(url)
        try:
            yt.check_availability()
            print("Is this your video?")
            print(f"Title\t: {yt.title}")
            vidName = yt.title
            seconds = yt.length # video length in seconds

            outStr = ""
            if seconds >= 60:
                preMinutes = seconds / 60 # divide by 60 to get minutes
                dec = preMinutes - int(preMinutes) # subtract whole number to get decimal part (if any)
                rSeconds = dec * 60 # convert decimal into seconds
                sec = int(rSeconds) 

                outStr = f"{int(preMinutes)} minutes {sec} seconds"
            else:
                outStr = f"{str(seconds)} seconds" 

            print(f"Length\t: {outStr}")
            print(f"Channel\t: {yt.author}")

            
            confirmation = input("Confirm (y/n): ")

            if confirmation.lower() == 'y':
                print("Available resolutions: ")
                resolutions = ["1080p","720p", "480p", "360p", "240p", "144p"]
                for i, q in enumerate(resolutions, 1):
                    print(f"{i} : {q}")

                quality = input("please enter the number of the desired resolution: ")
                while not quality.isnumeric() and (int(quality) > 5 or int(quality) < 1) :
                    print("invalid input, please try again: ")
                    quality = input()

                index = int(quality) - 1
                video = yt.streams.filter(res=resolutions[index], mime_type="video/mp4", adaptive=True).first()
                audio = yt.streams.filter(only_audio=True, mime_type="audio/mp4", adaptive=True).order_by("abr").desc().first()
                
                outName = f"{vidName}({resolutions[index]})"
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
                break

            else:
                continue

        except:
            print("An error occured")

if "__name__" == "__main__":
    main()