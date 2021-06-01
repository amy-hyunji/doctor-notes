import React, { useState } from 'react';

import './App.css';
import 'semantic-ui-css/semantic.min.css'

import drnotes from './assets/DrNotes-logo.png';

import { Button, Form, TextArea, Input } from 'semantic-ui-react'
import ReactPlayer from 'react-player'


function App() {
  const [note, setNote] = useState('');
  const [lastidx, setLastidx] = useState(0);
  const [video, setVideo] = useState('');
  const [videoUrl, setVideoUrl] = useState('');

  const downloadTxtFile = (filename, text) => {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      var splitNote = note.split("\n")
      
      if (splitNote[splitNote.length-1].indexOf(":\t") !== -1) {
        splitNote[splitNote.length-1] = lastidx + ":\t" + splitNote[splitNote.length-1]// .split(': ')[-1]
      }
      splitNote[splitNote.length-1] = lastidx + ":\t" + splitNote[splitNote.length-1]// .split(': ')[-1]
      setNote(splitNote.join("\n"))
    }

    
    
  }

  const handleChange = (e) => {
    setNote(e.target.value)
    
    var splitNote = note.split("\n")
    if (splitNote[splitNote.length-1] == '') {
      setLastidx(parseInt(reactPlayer.current.getCurrentTime()))
      //console.log("starting time:", lastidx)
    }
  }

  const handleChange2 = (e) => {
    setVideo(e.target.value)
  }


  const reactPlayer = React.useRef();

  return (
    <div className="App">
      <div>
        <img src={drnotes} style={{position: 'absolute', width: '160px', left: '5px', top: '10px'}} /> 
        <Button color='green' onClick={() => downloadTxtFile('myNotes.txt', note)} style={{position: 'absolute', right: '20px', top: '20px'}}>Export ↗️</Button>
      </div>
      <Input 
        action={{icon: 'search', onClick: () => setVideoUrl(video)}} 
        placeholder='Enter a YouTube URL...' 
        style={{margin: '6% auto 2%', width: '50%'}} 
        onChange={handleChange2}
        value={video}
        fluid
      />
      <ReactPlayer 
        url={videoUrl} 
        volume={0.3}
        ref={reactPlayer}

        style={{margin: '0 auto 2%', backgroundColor: 'lightgray'}}
      />
      {/*<Button onClick={() => console.log(reactPlayer.current.getCurrentTime())}>Get current time</Button>*/}

      <Form>
        <TextArea 
          placeholder='Write your notes here!'
          onKeyDown={handleKeyDown}
          onChange={handleChange}
          value={note}

          style={{width: '80%', height: '180px'}}
        >
        </TextArea>
      </Form>

    </div>
  );
}

export default App;
