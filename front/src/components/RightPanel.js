import React, { useState, useEffect } from 'react';
import './Panel.css';

import {Form, TextArea, Button} from 'semantic-ui-react'


function RightPanel(props) {
    //Const over here
    const [edit, setEdit] = useState(false)

    const [editValue, setEditValue] = useState('')
    const [editIdx, setEditIdx] = useState(0)
    const [editIdxtwo, setEditIdxtwo] = useState(0)

    useEffect(() => {
        console.log('right changed!')
        
    }, [props.contents])

    useEffect(() => {

    }, [editValue, editIdx])

    const handleChange = (index, idx, e) => {
        //console.log(e.target.value)
        //console.log(index, idx)
        setEditValue(e.target.value)
        setEditIdx(index)
        setEditIdxtwo(idx)
    }
    const sendEditInfo = () => {
        console.log(editValue, editIdx, editIdxtwo)
        props.changeNotes(editValue, editIdx, editIdxtwo)
        setEdit(!edit)
    }

    return (
        <div className='panels'>
            <h3 className="title">My Notes 📝</h3>
            { !edit
                ? <Button content="edit" size="tiny" onClick={() => {setEdit(!edit)}}></Button>
                : <Button content="done" size="tiny" onClick={() => {sendEditInfo()}}></Button>
            }

            <div style={{width: '92%', height: '85%', margin: '5px auto 0px', overflowY: 'scroll'}}>
            {
                props.contents ? 
                props.contents.map((notes, index) => (
                    <div style={{marginBottom: '10px', height: '250px', border: '1px solid lightgrey'}}>
                    { !edit
                    ? <div>
                        <div style={{color: 'gray', marginBottom: '3px'}}><b>{props.timestamp[index]} ~ {props.timestamp[index]+50} seconds</b></div>
                        {
                            notes.length > 0 
                            ? 
                            notes.map((note) => (
                                <li style={{textAlign: 'left', margin: '0px 0px 5px 15px'}}>{note}</li>
                            ))
                            : null
                        }
                        
                    </div>
                    : <Form >
                        
                        {
                            notes.length > 0 
                            ? 
                            notes.map((note, idx) => (
                                <TextArea 
                                    style={{height: '30px'}}
                                    onChange={(e) => handleChange(index, idx, e)}
                                    defaultValue={note}
                                ></TextArea>
                            ))
                            : null
                        }
                        {/*<TextArea 
                            onChange={(e) => handleChange(index, e)}
                            defaultValue={notes.map((note) => ("* " + note + "\n"))}
                            
                            style={{height: '250px'}}
                        >
                            
                        </TextArea>*/}
                    </Form>

                    }
                </div>
                ))
                : null
            }
        </div>
        </div>
    );
  }
export default RightPanel;