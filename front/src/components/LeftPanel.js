import React, { useState, useEffect } from 'react';
import './Panel.css';

import {ButtonGroup, Button, Input, TextArea, Form} from 'semantic-ui-react'

function LeftPanel(props) {
    //Const over here
    //const [oneScript, setOneScript] = useState(props.contents)
    const [edit, setEdit] = useState(false)

    const [showButton, setShowButton] = useState(false)
    const [curridx, setCurridx] = useState(0)


    const [editValue, setEditValue] = useState('')
    const [editIdx, setEditIdx] = useState(0)
  

    useEffect(() => {
        //console.log("CURR IDX", curridx)
    }, [curridx])

    useEffect(() => {
        //console.log("new script", props.contents)
    }, [props.contents])

    useEffect(() => {

    }, [editValue, editIdx])

    const handleChange = (index, e) => {
        setEditValue(e.target.value)
        setEditIdx(index)
    }

    const sendEditInfo = () => {
        props.changeScript(editValue, editIdx)
        setEdit(!edit)
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
        //console.log(window.getSelection().toString())
        props.getDragged(window.getSelection().toString(), curridx)
    }

    return (
      <div className="panels">
        <h3 className="title">Transcribed Lecture Recording 🎙️</h3>
        { !edit
            ? <Button content="edit" size="tiny" onClick={() => {setEdit(!edit)}}></Button>
            : <Button content="done" size="tiny" onClick={() => {sendEditInfo()}}></Button>
        }
        
        <div style={{width: '92%', height: '85%', margin: "5px auto 0px", overflowY: 'scroll'}}>
        {   props.contents &&
            props.contents.map((script, index) => (
                <div style={{marginBottom: '10px', minHeight: '200px', border: '1px solid lightgrey'}}>
                    { !edit 
                    ? <div>
                        <div style={{color: 'gray', marginBottom: '3px'}}><b>{props.timestamp[index]} ~ {props.timestamp[index]+50} seconds</b></div>
                        
                        <div onMouseUp={() => detectDragged(index)}>{script}</div>
                        {
                            showButton && (index === curridx)
                            ? <Button content="summarize?" size="mini" color="blue" onClick={sendDragged}></Button>
                            : null
                        }
                    </div>
                    : <Form >
                        <TextArea 
                            onChange={(e) => handleChange(index, e)}
                            defaultValue={script}
                            
                            style={{minHeight: '200px'}}
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

