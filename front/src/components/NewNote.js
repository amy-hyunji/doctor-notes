import React, { useState, useCallback, useEffect } from 'react';

import drnotes from '../assets/DrNotes-logo.png';
import './NewNote.css';
import axios from 'axios'
import qs from 'qs';
import sampleDict from '../assets/short_info.csv'

import { Button, Header, Image, Modal, ModalActions, Input, Form } from 'semantic-ui-react';
import { useDropzone } from 'react-dropzone'

function NewNote(props) {
    //Const over here
    const [modal, setModal] = useState(true);
    const [min, setMin] = useState('');
    const [max, setMax] = useState(''); 
    const [isLoading, setIsLoading] = useState(false);

    const [showInst, setShowInst] = useState(false);
    const [showEx, setShowEx] = useState(false);

    useEffect(() => {

    }, [props.audio])

    const {
        acceptedFiles,
        fileRejections,
        getRootProps,
        getInputProps
    } = useDropzone({
        accept: '.txt, .wav',
        maxFiles: 2,
    });

    const acceptedFileItems = acceptedFiles.map(file => (
        <li key={file.path}>
          {file.path} - {file.size} bytes
        </li>
    ));
    /*
    const fileRejectionItems = fileRejections.map(({ file, errors }) => (
        <li key={file.path}>
            {file.path} - {file.size} bytes
            <ul>
            {errors.map(e => (
                <li key={e.code}>{e.message}</li>
            ))}
            </ul>
        </li>
    ));
    */



    const sendToServer = () => {
        
        const formData = new FormData()
        
        console.log(acceptedFiles)
        for (var f in acceptedFiles){
            console.log(acceptedFiles[f])
            if (acceptedFiles[f].name.indexOf('.txt') > -1) {
                formData.append('user_note', acceptedFiles[f])
            }
            else {
                formData.append('audio_file', acceptedFiles[f])
                props.setAudio(acceptedFiles[f])
            }
        }


        setIsLoading(true)
        fetch(`http://52.156.155.214:8886/files`, {
            method: 'POST',

            body: formData,
            //mode:'no-cors'
        }).then(res => {
            setIsLoading(false)
            //console.log("res", res)
            //console.log("status", res.status)
            //console.log('res json', res.json())
            if(res.status !== 200) {
                throw new Error(res.statusText);
            }
            return res.json();
        }).then(data => {
            console.log(data)
            sendMinMax(data)
        });
        

    }

    const sendMinMax = (data) => {
        data['min_length'] = parseInt(min)
        data['max_length'] = parseInt(max)
        props.setMin(parseInt(min))
        props.setMax(parseInt(max))
        
        setIsLoading(true)
        console.log(data)
        fetch(`http://52.156.155.214:8886/upload`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            //mode:'cors'
        }).then(res => {
            setIsLoading(false)
            //console.log("status", res.status)
            if(res.status !== 200) {
                
                throw new Error(res.statusText);
            }
            return res.json();
        }).then(data => {
            console.log(data)
            setModal(false)
            props.getContents(data)
        });
        
    }

    
    
    const handleChange = (e) => {
        setMin(e.target.value)
    }
    const handleChange2 = (e) => {
        setMax(e.target.value)
    }

    const clickButton = () => {
        const sampleDict = {
            score: [1.0, 0.5, 0.5, 0.0, 0.5],
            script: ["cnn's kelly wallace completed 30-day challengescnn's kelly wallace completed 30-day challengesNews from your life. News from your life. News from your life. News from your life. News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b"],
            script_start_time: [0, 50, 100, 150, 200],
            summary: ["cnn's kelly wallace completed 30-day challenges . she hiked up the highest mountain in africa last year . the challenge helped her becom", "engineer, matt cutts the stalking his powerful visual download the video at ted.com . 30 days is just about the right amount of time to ad", "cnn's kelly wallace completed 30-day challenges . she hiked up the highest mountain in africa last year . the challenge helped her becom", "engineer, matt cutts the stalking his powerful visual download the video at ted.com . 30 days is just about the right amount of time to ad", "cnn's kelly wallace completed 30-day challenges . she hiked up the highest mountain in africa last year . the challenge helped her becom"],
            user_note: [["hello", "this", "is", "testing"], ["is"], ["user note", "lol"], [], ["last one"]]

        }
        setModal(false)
        //console.log(sampleDict)
        props.setMin(5)
        props.setMax(10)
        props.getContents(sampleDict)

        for (var f in acceptedFiles){
            console.log(acceptedFiles[f])
            if (acceptedFiles[f].name.indexOf('.txt') > -1) {
                //formData.append('user_note', acceptedFiles[f])
            }
            else {
                //formData.append('audio_file', acceptedFiles[f])
                console.log("ddd")
                props.setAudio(acceptedFiles[f])
            }
        }
    }

    return (
      <div>
        <Modal
            open={modal}
            
          >
            <Modal.Header>Welcome to <img src={drnotes} style={{width: '120px'}}/></Modal.Header>
            <Modal.Content>
              <Modal.Description>
                <span style={{lineHeight: '1.8', fontSize: '15px',}}>
                    This is a system to help students review their notes by re-organizing the lecture recordings. <br/>
                    Please read the following instruction before using our system:  <Button color="primary" size="tiny" compact onClick={() => setShowInst(!showInst)}>Click to see/hide instruction</Button> <br/>
                </span>
                { showInst
                ? <span style={{fontSize: '95%', marginLeft: "0", lineHeight: '1.5'}}>
                    1. Before you start, <b style={{color:'blue'}}>please make sure you get the credential</b> by visiting <a href="https://52.156.155.214:8886">our server</a> and accepting the credential issue. <br/>
                    2. Some helpful websites for our service: <br/>
                        - Convert audio file to .wav form: <a href='https://convertio.co/kr/'>https://convertio.co/kr</a> <br/>
                        - Get user note with time recorder: <a href='https://drnotes-notetaking.web.app/'>https://drnotes-notetaking.web.app</a> <br/>
                    3. Drop the lecture recordings (.wav) and typed user notes (.txt) and write the length range of your summarization results. <br/>
                    4. Get the transcribed script and modify them if necessary.<br/>
                    5. Explore the recommended level by moving the recommendation threshold bar. Default is 'Low'.<br/>
                    6. Fill in your notes (third column) by suggested notes in the summarization panel and additional summarization by draging the script. <br/>
                    7. Show / hide different panels clicking the three buttons on the top: Recording, Summarization, My Notes.<br/>
                    8. Click the export button to save your notes.<br/> <br/>
                </span>
                : null
                }               
                <hr></hr>
                <span style={{fontSize: '15px', marginBottom: '10px'}}>
                    Please drop your lecture recording (in .wav form) and notes from <a href="https://drnotes-notetaking.web.app/">this site</a> (in .txt form). <br/>
                    You need to select two files <b style={{color: "blue"}}>at once</b> to drop two files.
                </span><br/>
                

                <section className="container">
                    <div {...getRootProps({ className: 'dropzone' })}>
                        <input {...getInputProps()} />
                        <p>Drag 'n' drop some files here, or click to select files</p>
                        <em>(Only *.wav and *.txt images will be accepted)</em>
                    </div>
                    <aside>
                        <h4>Accepted files</h4>
                        <ul>{acceptedFileItems}</ul>
                    </aside>
                </section>
                <hr/>
                <span style={{lineHeight: '1.8', fontSize: '16px'}}>
                    Please input the minimum and maximum length of the summarization you wish to see. <br/>
                    Here are example input and outputs for your reference: <Button color="primary" size="tiny" compact onClick={() => setShowEx(!showEx)}>Click to see/hide example</Button><br/>
                </span>
                { showEx
                ?    <span style={{fontSize: '90%', lineHeight: '1.8'}}>
                        
                        <b>Input:</b> 30 days is just about the right amount of time to add a new habit or subtract a habit from your life . 
                        a few things i learned while doing these 30-day challenges . the first was, instead of the months flying by, 
                        forgotten, the time was much more memorable . as i started doing more and harder challenges, my self-confidence grew, 
                        i went from desk-dwelling computer nerd to the kind of guy who bikes to work. <br/>
                        <b>Output (min: 5, max: 20):</b> 30 days is just about the right amount of time to add a new habit or subtract <br/>
                        <b>Output (min: 5, max: 200):</b> 30 days is just about the right amount of time to add a new habit or subtract a habit from your life . a few things i learned while doing these 30-day challenges . 
                        the first was, instead of the months flying by, the time was much more memorable .  <br/>
                        <b>Output (min: 100, max: 170):</b> 30 days is just about the right amount of time to add a new habit or subtract a habit from your life . 
                        a few things i learned while doing these 30-day challenges . the first was, instead of the months flying by, forgotten, the time was much more memorable . 
                        as i started doing more and harder challenges, my self-confidence grew, i went from desk-dwelling computer nerd to the kind of guy who bikes to work . 
                    </span>
                : null
                }
                <hr></hr>
                <Form>
                    <Form.Group widths='equal'>
                        <Form.Input label='Minimum length' placeholder='Minimum length' value={min} onChange={handleChange} />
                        <Form.Input label='Maximum length' placeholder='Maximum length' value={max} onChange={handleChange2} />
                    </Form.Group>
                    
                </Form>

              </Modal.Description>
              
            </Modal.Content>
            <Modal.Actions>
                <div style={{paddingBottom: '5px'}}>It normally takes around 3~5 minutes to send the files! Please wait 🙏</div>
                <Button content="Dummy Data" onClick={clickButton} disabled></Button>
                <Button
                    onClick={(acceptedFiles) => sendToServer(acceptedFiles)}
                    labelPosition='right'
                    icon='arrow right'
                    content='Begin Loading'
                    loading={isLoading}
                />
            </Modal.Actions>
          </Modal>
      </div>
    );
  }
export default NewNote;
