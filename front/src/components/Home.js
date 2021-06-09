import React, { useState, useEffect } from 'react';
import axios from 'axios';

import LeftPanel from './LeftPanel';
import MiddlePanel from './MiddlePanel';
import RightPanel from './RightPanel';
import NewNote from './NewNote';
import './Home.css';
import drnotes from '../assets/DrNotes-logo.png';
import testaudio from '../assets/test-audio.mp3'
import tedaudio from '../assets/MattCutts_2011U.wav'

import { Grid} from '@material-ui/core';
import {ButtonGroup, Button} from 'semantic-ui-react'
import ReactAudioPlayer from 'react-audio-player';

import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';



function Home() {
    // Declare a new state variable, which we'll call "count"
    const [left, setLeft] = useState(true);
    const [middle, setMiddle] = useState(true);
    const [right, setRight] = useState(true);
    const [modal, setModal] = useState(true);

    const [allInfo, setAllInfo] = useState({});
    const [script, setScript] = useState([]);
    const [summary, setSummary] = useState([]);
    const [notes, setNotes] = useState([]);

    const [dragged, setDragged] = useState('');
    const [newSummary, setNewSummary] = useState(["summary", 0, "initial"]);

    const [min, setMin] = useState(0);
    const [max, setMax] = useState(0);

    const [drag, setDrag] = useState(false)
    
    const [audio, setAudio] = useState('')


    useEffect(() => {
        console.log("NEW CONTENT", allInfo)
        
        setScript(allInfo['script'])
        setSummary(allInfo['summary'])
        setNotes(allInfo['user_note'])

        
        //console.log(script)
    }, [allInfo])

    useEffect(() => {
        console.log("script, summary, and user note changed")
    }, [script, summary, notes])

    useEffect(() => {
        console.log("MIN AND MAX CHANGED")
        console.log(min, max)
    }, [min, max])

    useEffect(() => {
        console.log(newSummary)
    }, [newSummary])

    useEffect(() => {
        console.log("new audio", audio)
    }, [setAudio])
  
    const toServer = (input) => {
        const finalResult = input;
        axios.post(`http://52.156.155.214:8886/`, {
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

    const getDragged = (data, idx) => {
        setDragged(data)
        console.log(data)
        const dragInfo = {
            max_length: max,
            min_length: min,
            drag_text: data,
            chunk_index: idx
        }
        console.log(dragInfo)
        //send to server to get summary
        fetch(`http://52.156.155.214:8886/drag`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dragInfo),

        }).then(res => {
            if(res.status !== 200) {
                throw new Error(res.statusText);
            }
            return res.json();
        }).then(data => {
            console.log(data)
            setNewSummary([data['summary'], data['chunk_index'], data['drag_text']])
            setDrag(true)
        });
    }

    const addNotes = (data, idx) => {
        //console.log(data, idx)
        //console.log(allInfo['user_note'])
        var newInfo = {...allInfo}
        newInfo['user_note'][idx].push(data)
        console.log(allInfo)
        setAllInfo(newInfo)
        
    }

    const changeScript = (data, idx) => {
        var newInfo = {...allInfo}
        newInfo['script'][idx] = data
        setAllInfo(newInfo)

        const sendDict = {
            dict: newInfo,
            min_length: min,
            max_length: max
        }

        fetch(`http://52.156.155.214:8886/revise`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sendDict),

        }).then(res => {
            if(res.status !== 200) {
                throw new Error(res.statusText);
            }
            return res.json();
        }).then(data => {
            console.log(data)
            setAllInfo(data)
            alert("Summary changed!")
        });
    }

    const changeNotes = (data, idx, idx2) => {
        var newInfo = {...allInfo}
        newInfo['user_note'][idx][idx2] = data
        setAllInfo(newInfo)

        
    }

    const removeNote = (data, idx, idx2) => {
        var newInfo = {...allInfo}
        
        var newChunk = newInfo['user_note'][idx]
        newChunk.splice(idx2, 1)
        newInfo['user_note'][idx] = newChunk
        setAllInfo(newInfo)
    }

    const exportpdf = () => {
        /*
        html2canvas(document.querySelector("#export"), {
            onpreloaded: (canvas) => {document.querySelector("#export").style.overflowY="visible";},
            onpreloaded: function(canvas){}
        }).then(canvas => {
            //document.body.appendChild(canvas);  // if you want see your screenshot in body.
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF();
            pdf.addImage(imgData, 'PNG', 0, 0);
            pdf.save("download.pdf"); 
        })
        */
        console.log(notes)
        console.log(allInfo['script_start_time'])

        var newString = ''

        for (var i in notes){
            const endTime = allInfo['script_start_time'][i]+50
            newString += allInfo['script_start_time'][i] + " ~ " + endTime + ' seconds\n' 
            for (var j in notes[i]) {
                newString += "* " + notes[i][j] + '\n'
            }
            newString += '\n'
        }
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(newString));
        element.setAttribute('download', 'NewNote.txt');

        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);

        /*
        html2canvas(document.querySelector("#export")).then(function(canvas) {
            var imgData = canvas.toDataURL('image/png');
            var imgWidth = 210;
            var pageHeight = imgWidth * 1.414;
            var imgHeight = canvas.height * imgWidth / canvas.width;

            var doc = new jsPDF({
            'orientation': 'p',
            'unit': 'mm',
            'format': 'a4'
            });

            doc.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
            doc.save('sample_A4.pdf');
            console.log('Reached here?');
        });
        */

    }
    

    return (
        <div className="main-page">
            <NewNote getContents={getContents} setMin={setMin} setMax={setMax} setAudio={setAudio}></NewNote>
            <img src={drnotes} style={{position: 'absolute', width: '160px', left: '5px', top: '10px'}} /> 
            <div style={{height: "10vh", paddingTop: "2.5vh", float: "right", paddingRight: "20px"}}>
                
                <Button.Group variant="contained" disableElevation>
                    <Button onClick={() => setLeft(!left)} color={left ? 'blue': ''}>Recording 🎙️</Button>
                    <Button onClick={() => setMiddle(!middle)} color={middle ? 'blue': ''}>Summarization</Button>
                    <Button onClick={() => setRight(!right)} color={right ? 'blue': ''}>My Notes 📝</Button>
                </Button.Group>
                <Button onClick={() => exportpdf()} color='green' style={{marginLeft: '10px'}}>Export ↗️</Button>
                
            </div>
            <Grid container justify="center" spacing={1} style={{padding: '0px 10px'}}>
                {
                    left &&
                    <Grid item xs={4}>
                        <LeftPanel 
                            contents={script} 
                            timestamp={allInfo['script_start_time']}
                            getDragged={getDragged}
                            changeScript={changeScript}
                        ></LeftPanel>
                    </Grid>
                }  
            
                {
                    middle &&
                    <Grid item xs={4}>
                        <MiddlePanel 
                        contents={summary} 
                        score={allInfo['score']}
                        timestamp={allInfo['script_start_time']}
                        addNotes={addNotes} 
                        newSummary={newSummary}
                        drag={drag}
                        setDrag={setDrag}
                        ></MiddlePanel>
                    </Grid>
                }
            
                {
                    right &&
                    <Grid item xs={4}>
                        <RightPanel 
                            contents={notes}
                            timestamp={allInfo['script_start_time']}
                            changeNotes={changeNotes}
                            removeNote={removeNote}
                        ></RightPanel>
                    </Grid>
                }
            </Grid>
            {
            <ReactAudioPlayer
                src={audio.path}
                
                controls
                volume={0.3}
                style={{marginTop: "2vh"}}
            />}
        </div>

    );
}

export default Home;