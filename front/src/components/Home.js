import React, { useState } from 'react';
import axios from 'axios';

import LeftPanel from './LeftPanel';
import MiddlePanel from './MiddlePanel';
import RightPanel from './RightPanel';
import './Home.css';
import drnotes from '../assets/DrNotes-logo.png';
import testaudio from '../assets/test-audio.mp3'

import { Grid} from '@material-ui/core';
import {ButtonGroup, Button} from 'semantic-ui-react'
import ReactAudioPlayer from 'react-audio-player';




function Home() {
    // Declare a new state variable, which we'll call "count"
    const [left, setLeft] = useState(true);
    const [middle, setMiddle] = useState(true);
    const [right, setRight] = useState(true);
  
    const toServer = (input) => {
        const finalResult = input;
        axios.post(`http://127.0.0.1:5000/tryout`, {
            sentence: finalResult,
        })
            .then((res) => {
            console.log(res);
            console.log(res.data);
        });
    }


    return (
        <div className="main-page">
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
                        <LeftPanel></LeftPanel>
                    </Grid>
                }  
            
                {
                    middle &&
                    <Grid item xs={4}>
                        <MiddlePanel></MiddlePanel>
                    </Grid>
                }
            
                {
                    right &&
                    <Grid item xs={4}>
                        <RightPanel></RightPanel>
                    </Grid>
                }
            </Grid>
            <ReactAudioPlayer
                src={testaudio}
                autoPlay
                controls
                style={{marginTop: "2vh"}}
            />
        </div>

    );
}

export default Home;