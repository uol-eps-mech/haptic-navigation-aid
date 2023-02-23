import { useState } from "react";
import './Cell.css';

function Cell({start = false, end = false, obstacle, setObstacle}) {

  return (
    <div className={"cell"} onClick={setObstacle} style={{backgroundColor: start ? "lightblue" : end ? "LIGHTgreen" : obstacle ? "grey" : "white"}}>
        {obstacle ? 0 : 1}
    </div>
  );
}

export default Cell;
