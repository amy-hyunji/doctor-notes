import React, { useState, useCallback } from 'react';

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
            }
        }


        setIsLoading(true)
        fetch(`http://52.156.155.214:8887/files`, {
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
        fetch(`http://52.156.155.214:8887/upload`, {
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
            score: [0.5, 0.5, 0.5, 0.5, 0.5],
            script: ["cnn's kelly wallace completed 30-day challengescnn's kelly wallace completed 30-day challengesNews from your life. News from your life. News from your life. News from your life. News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b", "News from your life. There's a few things that I learned while doing these 30-day challenges, the first was instead of the months flying b"],
            script_start_time: [0, 50, 100, 150, 200],
            summary: ["cnn's kelly wallace completed 30-day challenges . she hiked up the highest mountain in africa last year . the challenge helped her becom", "engineer, matt cutts the stalking his powerful visual download the video at ted.com . 30 days is just about the right amount of time to ad", "cnn's kelly wallace completed 30-day challenges . she hiked up the highest mountain in africa last year . the challenge helped her becom", "engineer, matt cutts the stalking his powerful visual download the video at ted.com . 30 days is just about the right amount of time to ad", "cnn's kelly wallace completed 30-day challenges . she hiked up the highest mountain in africa last year . the challenge helped her becom"],
            user_note: [["hello", "this"], ["is"], ["user note", "lol"], [], ["last one"]]

        }
        setModal(false)
        //console.log(sampleDict)
        
        props.getContents(sampleDict)
    }

    return (
      <div>
        <Modal
            open={modal}
          >
            <Modal.Header>Welcome to <img src={drnotes} style={{width: '120px'}}/></Modal.Header>
            <Modal.Content image>
              <Modal.Description>
                <span style={{lineHeight: '1.8', fontSize: '16px'}}>
                    This is a system to help students review their notes by re-organizing the lecture recordings. <br/>
                    Please drop the lecture recording (in .wav) and your notes (in .txt) <br/> <br/>
                </span>

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

                <span style={{lineHeight: '1.8', fontSize: '16px'}}>
                    Please input the minimum and maximum length of the summarization you wish to see. <br/>
                    Some examples: blah blah
                    <br/>
                </span>

                <Form>
                    <Form.Group widths='equal'>
                        <Form.Input label='Minimum length' placeholder='Minimum length' value={min} onChange={handleChange} />
                        <Form.Input label='Maximum length' placeholder='Maximum length' value={max} onChange={handleChange2} />
                    </Form.Group>
                    
                </Form>

              </Modal.Description>
              
            </Modal.Content>
            <Modal.Actions>
                <Button content="Testing" onClick={clickButton}></Button>
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
