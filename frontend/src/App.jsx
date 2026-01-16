import { useState, useRef } from 'react'
import PreviewArea from './PreviewArea'


function App() {
    const inputRef = useRef(null);
    const [url, setURL] = useState("");

    function handleGET(){
        setURL(inputRef.current.value);
        inputRef.current.value = "";
    }
    
    return (
        <div className='app-container'>
            <header>
                <h2>
                    YourTube 
                </h2>
            </header>

            <h2>YouTube Video Downloader</h2>

            <div className='input-container'>
                <input ref={inputRef} placeholder='Enter URL here'/>
                <button onClick={handleGET} id='GETButton'>
                    GET
                </button>
            </div>

            <PreviewArea url={url}/>

            {/* <footer>
                <p>YourTube {new Date().getFullYear()}</p>
            </footer> */}

        </div>
    );
}

export default App
