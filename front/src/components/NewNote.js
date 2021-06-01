import React, { useState, useCallback } from 'react';

import drnotes from '../assets/DrNotes-logo.png';
import './NewNote.css';
import axios from 'axios'


import { Button, Header, Image, Modal, ModalActions, Input, Form } from 'semantic-ui-react';
import { useDropzone } from 'react-dropzone'

function NewNote() {
    //Const over here
    const [modal, setModal] = useState(true);
    const [min, setMin] = useState('');
    const [max, setMax] = useState(''); 

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
        var formData = new FormData()
        
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
        formData.append("min_length", min)
        formData.append("max_length", max)
        console.log(formData.getAll('user_note'))
        console.log(formData.getAll('audio_file'))
        console.log(formData.getAll('min_length'), formData.getAll('max_length'))
        axios.post('http://52.156.155.214:8887/upload', {
            data: formData
        }).then((response) => {
            console.log(response);
        }, (error) => {
            console.log(error);
        });

        /*
        axios.post('http://52.156.155.214:8887/upload', {
            data: "text"
        }).then((response) => {
            console.log(response);
        }, (error) => {
            console.log(error);
        });
        */
    }

    
    const handleChange = (e) => {
        setMin(e.target.value)
    }
    const handleChange2 = (e) => {
        setMax(e.target.value)
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
              <Button
                onClick={(acceptedFiles) => sendToServer(acceptedFiles)}
                labelPosition='right'
                icon='arrow right'
                content='Begin Loading'
              />
            </Modal.Actions>
          </Modal>
      </div>
    );
  }
export default NewNote;
