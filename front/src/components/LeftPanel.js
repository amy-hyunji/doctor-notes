import React, { useState, useEffect } from 'react';
import './Panel.css';

import {ButtonGroup, Button, Input, TextArea, Form} from 'semantic-ui-react'

function LeftPanel(props) {
    //Const over here
    const [oneScript, setOneScript] = useState(props.contents)
    const [edit, setEdit] = useState(false)

    const [showButton, setShowButton] = useState(false)
    const [curridx, setCurridx] = useState(0)
  

    useEffect(() => {
        console.log("CURR IDX", curridx)
    }, [curridx])

    const handleChange = (e) => {
        //setOneScript(e.target.value)
        console.log(e.target.value)
        console.log()
    }

    const detectDragged = (idx) => {
        if (window.getSelection().toString() !== "") {
            setShowButton(true)
            setCurridx(idx)
        }
        else {
            setShowButton(false)
        }
    }

    const sendDragged = () => {
        console.log(window.getSelection().toString())
        props.getDragged(window.getSelection().toString())
    }

    return (
      <div className="panels">
        <h3 className="title">Transcribed Lecture Recording 🎙️</h3>
        <Button content="edit" size="tiny" onClick={() => {setEdit(!edit)}}></Button>
        <div style={{width: '92%', height: '85%', margin: "0px auto", overflowY: 'scroll'}}>
        {   props.contents &&
            props.contents.map((script, index) => (
                <div style={{marginBottom: '10px', height: '200px', border: '1px solid lightgrey'}}>
                    { !edit 
                    ? <div>
                        <div style={{color: 'gray', marginBottom: '3px'}}><b>{index*50} ~ {(index+1)*50} seconds</b></div>
                        
                        <div onMouseUp={() => detectDragged(index)}>{script}</div>
                        {
                            showButton && (index === curridx)
                            ? <Button content="summarize?" size="mini" color="blue" onClick={sendDragged}></Button>
                            : null
                        }
                    </div>
                    : <Form >
                        <TextArea 
                            onChange={handleChange}
                            defaultValue={script}
                            
                            style={{height: '200px'}}
                        >
                        </TextArea>
                    </Form>
                    }
                </div>
            ))
        }
        </div>
        {/*
        <div>{props.contents}</div>
        */}
      </div>
    );
  }
export default LeftPanel;

