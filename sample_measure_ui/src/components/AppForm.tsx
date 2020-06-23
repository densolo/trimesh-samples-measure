
import * as React from 'react';
import { ReactReduxContext } from 'react-redux'
import { connect, useSelector } from 'react-redux'


const handleClick = () => {
    let QWebBackend = (window as any).QWebBackend;
    QWebBackend.backendEvent("{hello 2}", (rt: string) => {
        console.log("return 2: " + rt);
    });
}

const AppForm = () => {
    //const cardState = useSelector(state => state) as any;
  
    return (
        <div>
            Measures
            <button onClick={handleClick}>Open</button>
        </div>
    );
  };
  
export default AppForm;
