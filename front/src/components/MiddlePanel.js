import React, { useState, useEffect } from 'react';
import './Panel.css';

import {ButtonGroup, Button} from 'semantic-ui-react'

function MiddlePanel(props) {
    //Const over here
    const [drag, setDrag] = useState(false)
  
    return (
      <div className='panels'>
        <h3 className="title">Summarization</h3>
        <div style={{width: '92%', height: '85%', margin: '13% auto 0px', overflowY: 'scroll'}}>
            {
                props.contents &&
                props.contents.map((summary, index) => (
                    <div style={{marginBottom: '10px', height: '200px', border: '1px solid lightgrey'}}>
                    { !drag 
                    ? <div>
                        <div style={{color: 'gray', marginBottom: '3px'}}><b>{index*50} ~ {(index+1)*50} seconds</b></div>
                        {
                            summary.split('.').map((bullet) => (
                                <div style={{display: 'flex', width: '100%'}}>
                                <li style={{textAlign: 'left', margin: '0px 0px 5px 15px', alignContent: 'flex-start'}}>{bullet}</li>
                                <Button size='mini' color='grey' style={{alignContent: 'flex-end', padding: '0px 5px', margin: '0px 0px 0px 0', height: '15px'}}>+</Button>
                                </div>
                            ))
                        }
                    </div>
                    : <div>
                        dragged content!!
                    </div>
                    }
                </div>
                ))
            }
        </div>
        
      </div>
    );
  }
export default MiddlePanel;