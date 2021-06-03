import React, { useState, useEffect } from 'react';
import './Panel.css';

function RightPanel(props) {
    //Const over here
  
    return (
        <div className='panels'>
            <h3 className="title">My Notes 📝</h3>
            <div style={{width: '92%', height: '85%', margin: '13% auto 0px', overflowY: 'scroll'}}>
            {
                props.contents &&
                props.contents.map((notes, index) => (
                    <div style={{marginBottom: '10px', height: '200px', border: '1px solid lightgrey'}}>
                    {
                    <div>
                        <div style={{color: 'gray', marginBottom: '3px'}}><b>{index*50} ~ {(index+1)*50} seconds</b></div>
                        {
                            notes.length > 0 
                            ? 
                            notes.map((note) => (
                                <li style={{textAlign: 'left', margin: '0px 0px 5px 15px'}}>{note}</li>
                            ))
                            : null
                        }
                        
                    </div>

                    }
                </div>
                ))
            }
        </div>
        </div>
    );
  }
export default RightPanel;