import React, { useState, useEffect } from 'react';
import axios from 'axios';

import LeftPanel from './LeftPanel';
import MiddlePanel from './MiddlePanel';
import RightPanel from './RightPanel';
import NewNote from './NewNote';
import './Home.css';
import drnotes from '../assets/DrNotes-logo.png';
import testaudio from '../assets/test-audio.mp3'
//import tedaudio from '../assets/MattCutts_2011U.wav'

import { Grid} from '@material-ui/core';
import {ButtonGroup, Button} from 'semantic-ui-react'
import ReactAudioPlayer from 'react-audio-player';




function Home() {
    // Declare a new state variable, which we'll call "count"
    const [left, setLeft] = useState(true);
    const [middle, setMiddle] = useState(true);
    const [right, setRight] = useState(true);
    const [modal, setModal] = useState(true);

    const [allInfo, setAllInfo] = useState({});
    const [script, setScript] = useState([]);

    const [dragged, setDragged] = useState('');

    const [min, setMin] = useState(0);
    const [max, setMax] = useState(0);


    useEffect(() => {
        console.log(allInfo)
        setScript(allInfo['script'])
        console.log(script)
    }, [allInfo, script])

    useEffect(() => {
        console.log("MIN AND MAX CHANGED")
        console.log(min, max)
    }, [min, max])
  
    const toServer = (input) => {
        const finalResult = input;
        axios.post(`http://52.156.155.214:8887/`, {
            sentence: finalResult,
        })
            .then((res) => {
            console.log(res);
            console.log(res.data);
        });
    }

    const getContents = (data) => {
        setAllInfo(data)
        console.log("At Home.js", data)
        
    }

    const getDragged = (data) => {
        setDragged(data)
        console.log(data)
        //send to server to get summary
    }
    

    return (
        <div className="main-page">
            <NewNote getContents={getContents} setMin={setMin} setMax={setMax}></NewNote>
            <img src={drnotes} style={{position: 'absolute', width: '160px', left: '5px', top: '10px'}} /> 
            <div style={{height: "10vh", paddingTop: "2.5vh", float: "right", paddingRight: "20px"}}>
                
                <Button.Group variant="contained" disableElevation>
                    <Button onClick={() => setLeft(!left)} color={left ? 'blue': ''}>Recording 🎙️</Button>
                    <Button onClick={() => setMiddle(!middle)} color={middle ? 'blue': ''}>Summarization</Button>
                    <Button onClick={() => setRight(!right)} color={right ? 'blue': ''}>My Notes 📝</Button>
                </Button.Group>
                <Button onClick={() => toServer("POST TO SERVER")} color='green' style={{marginLeft: '10px'}}>Export ↗️</Button>
                
            </div>
            <Grid container justify="center" spacing={1} style={{padding: '0px 10px'}}>
                {
                    left &&
                    <Grid item xs={4}>
                        <LeftPanel contents={allInfo['script']} getDragged={getDragged}></LeftPanel>
                    </Grid>
                }  
            
                {
                    middle &&
                    <Grid item xs={4}>
                        <MiddlePanel contents={allInfo['summary']}></MiddlePanel>
                    </Grid>
                }
            
                {
                    right &&
                    <Grid item xs={4}>
                        <RightPanel contents={allInfo['user_note']}></RightPanel>
                    </Grid>
                }
            </Grid>
            {/*
            <ReactAudioPlayer
                src={tedaudio}
                autoPlay
                controls
                volume={0.3}
                style={{marginTop: "2vh"}}
            />*/}
        </div>

    );
}

export default Home;