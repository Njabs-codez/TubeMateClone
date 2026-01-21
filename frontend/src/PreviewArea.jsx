import { useEffect, useState } from "react"
import serverErrorImage from './assets/download.jpg'
import userErrorImage from './assets/MJNoNoNo.jpg'
 
const API_URL = import.meta.VITE_API_URL || "http://localhost:8000";

function PreviewArea(props){

    const [selectValue, setSelectValue] = useState("360p");
    const [videoInfo, setVideoInfo] = useState({});
    const [dataAvailable, setDataAvailable] = useState(false);
    const [err, setErr] = useState(false);
    
    useEffect(() => {
        const cont = new AbortController();
        async function getVidInfo() {
            if(props.url === '') return;
            try{
                let res = await fetch(`${API_URL}/api/get-video-info?url=${props.url}`, {
                    signal : cont.signal
                });
                
                if(!res.ok){
                    let errData = await res.json();
                    switch(res.status){
                        case 400:
                            throw new Error(`Bad Request. Reason: ${errData.message}`);
                        case 500:
                            throw new Error(`Internal Server Error. Reason: ${errData.message}`);
                    }
                }
                // successful request
                let data = await res.json();
                console.log(data);
                setVideoInfo(data);
                setDataAvailable(true);
                setErr(false);
            }
            catch(err){
                let fake = null;
                console.log(err.message);
                if(err.message.includes("Bad Request")){
                    fake = {
                        thumbnail : userErrorImage,
                        title : "Please ensure your URL is correct",
                        channel : "User Error"
                    }
                }
                else if(err.message.includes("Internal Server Error")){
                    fake = {
                        thumbnail : serverErrorImage,
                        title : "Something went wrong on our end",
                        channel : "App Error"
                    }
                }
                else{
                    fake = {
                        thumbnail : serverErrorImage,
                        title : "Not sure what went wrong",
                        channel : "App Error"
                    }
                }

                setVideoInfo(fake);
                setDataAvailable(true);
                setErr(true);
            }
        }
        getVidInfo();
        return () => cont.abort();

    }, [props.url])

    function handleDownload(){
        if(selectValue === "") return;

        fetch(`${API_URL}/api/get-video?url=${props.url}&qual=${selectValue}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Download failed");
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${videoInfo.title}(${selectValue}).mp4`; // filename fallback
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            setDataAvailable(false);
        })
        .catch(err => {
            console.log(err.message);
            let fake = {
                thumbnail : serverErrorImage,
                title : "Could not download. Something likely went wrong on our end",
                channel : "App Error"
            };
            setVideoInfo(fake);
            setDataAvailable(true);
            setErr(true);
                    
        });


    }


    let downloadControls = <div className="download-controls">
                    <div className="select-wrapper">
                        <select value={selectValue} onChange={(e) => setSelectValue(e.target.value)} 
                        className="select">

                        <option value="1080p">1080p</option>
                        <option value="720p">720p</option>
                        <option value="480p">480p</option>
                        <option value="360p">360p</option>
                        <option value="240p">240p</option>
                        </select>
                    </div>

                    <button onClick={handleDownload} id="DownloadButton">
                        Download
                    </button>
                </div>

    // rendering part, data available render content else nothing (or fragment)
    if(dataAvailable){
        return (
            <div className="previewArea">
                <img src={videoInfo.thumbnail} className="thumbnail" alt="video thumbnail"/>

                <div className="videoText">
                    <p>Title: {videoInfo.title}</p>
                    <p>Channel: {videoInfo.channel}</p>
                </div>

                {!err ? downloadControls : null}
                
            </div>
        )
    }

    return <></>;
    
}

export default PreviewArea