import React, { useState, useEffect } from 'react';
import './Panel.css';

import {ButtonGroup, Button} from 'semantic-ui-react'

function MiddlePanel(props) {
    //Const over here
    const [allSummary, setAllSummary] = useState(props.contents)
    const [threshold, setThreshold] = useState(0.0)

    const [on, setOn] = useState([true, false, false]);
    const [middle, setMiddle] = useState(true);
    const [right, setRight] = useState(true);

    useEffect(() => {
        setAllSummary(props.contents)
    }, [props.contents])

    useEffect(() => {
        console.log('middle changed!')
    }, [props.contents, props.drag, props.newSummary])
  
    return (
      <div className='panels'>
        <h3 className="title">Summarization</h3>
        <Button.Group size="tiny">
            <Button onClick={() => {setThreshold(0.0); setOn([true, false, false])}} color={on[0] ? 'blue': ''}>Low</Button>
            <Button onClick={() => {setThreshold(0.5); setOn([false, true, false])}} color={on[1] ? 'blue': ''}>Middle</Button>
            <Button onClick={() => {setThreshold(1.0); setOn([false, false, true])}} color={on[2] ? 'blue': ''}>High</Button>
        </Button.Group>
        <div style={{width: '92%', height: '85%', margin: '5px auto 0px', overflowY: 'scroll'}}>
            { !props.drag
            ? <div>
            {
                allSummary &&
                allSummary.map((summary, index) => (
                    
                    <div style={{marginBottom: '10px', minHeight: '200px', border: '1px solid lightgrey'}}>
                    { props.score[index] >= threshold
                    ? <div>
                        <div style={{color: 'gray', marginBottom: '3px'}}><b>{props.timestamp[index]} ~ {props.timestamp[index]+50} seconds</b></div>
                        {
                            summary.split(' .').map((bullet) => (
                                <div style={{display: 'flex', width: '100%'}}>
                                <li style={{textAlign: 'left', margin: '0px 0px 5px 15px', alignContent: 'flex-start', width: '100%'}}>{bullet}</li>
                                <Button onClick={() => props.addNotes(bullet, index)} size='mini' color='grey' style={{alignContent: 'flex-end', padding: '0px 5px', margin: '0px 0 0px 0px', height: '15px', marginRight: '0'}}>+</Button>
                                </div>
                            ))
                        }
                    </div>
                    : <div>
                        <div style={{color: 'gray', marginBottom: '3px'}}><b>{props.timestamp[index]} ~ {props.timestamp[index]+50} seconds</b></div>
                        <div style={{margin: '0 10px'}}>No summary available at this threshold 🥲</div>
                    </div>
                    }
                    
                </div>
                ))
            } </div>
            : <div>
                <div style={{marginBottom: '10px', minHeight: '200px', border: '1px solid lightgrey'}}>
                    <div>{props.newSummary[2]}</div>
                    <div style={{margin: "10px 0"}}>⬇️</div>
                    <div>{props.newSummary[0]}</div>
                </div>
                <Button color='green' onClick={() => {props.addNotes(props.newSummary[0], props.newSummary[1])}} size="tiny" content="Add this summary?"></Button>
                <div style={{height: '10px'}}> </div>
                <Button color='red' onClick={() => {props.setDrag(false)}} size="tiny" content="Ignore this summary and go back"></Button>
            </div>
            }
        </div>
        
      </div>
    );
  }
export default MiddlePanel;