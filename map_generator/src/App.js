import './App.css';
import React, {useState} from "react"
import Cell from './Cell';
import Row from './Row';

const rotateMatrix = (matrix) => {
  return matrix[0].map((val, index) => matrix.map(row => row[index]))
}

function App() {
  const [width, setWidth] = useState(10);
  const [height, setHeight] = useState(10);
  const [start, setStart] = useState("0,0");
  const [goal, setGoal] = useState(`${height - 1}, ${width-1}`);
  const [usermap, setMap] = useState([...Array(width)].map((_, y) => [...Array(height)].map(() => 1)))

  const startPos = start.split(",").map((x) => parseInt(x));
  const goalPos = goal.split(",").map((x) => parseInt(x));

  // console.log(usermap);

  const copyMapDetails = () => {
    const map = rotateMatrix(usermap);
    var csv = map
      .map((item) => {
       
        // Here item refers to a row in that 2D array
        var row = item;
         
        // Now join the elements of row with "," using join function
        return "[" + row.join(",") + "],";
      }) // At this point we have an array of strings
      .join("\n");
    navigator.clipboard.writeText("maze=[" + csv + "]" + "\nstart=" + start + "\ngoal=" + goal)
  }

  return (
    <div className="App">
      
      <div style={{display: "flex", gap: "10px", width: "100%", height: "50px", alignItems: "center", justifyContent: "center"}}>
        <p>Enter Width</p>
        <input type={"number"} value={width} onChange={(e) => setWidth(parseInt(e.target.value))} />
        <p>Enter Height</p>
        <input type={"number"} value={height} onChange={(e) => setHeight(parseInt(e.target.value))} />
      </div>
      <div style={{display: "flex", gap: "10px", width: "100%", height: "50px", alignItems: "center", justifyContent: "center"}}>
        <p>Enter start</p>
        <input value={start} onChange={(e) => setStart(e.target.value)} />
        <p>Enter goal</p>
        <input value={goal} onChange={(e) => setGoal(e.target.value)} />
      </div>

      
      <div style={{width: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", paddingTop: "40px"}}>
        {usermap?.map((_, y) => 
          <Row>
            {usermap[y].map((val, x) => {
              return <Cell 
              start={startPos[0] === x && startPos[1] === y} 
              end={goalPos[0] === x && goalPos[1] === y} 
              obstacle={usermap[x][y] === 0} 
              setObstacle={() => {
                let newMap = []
                for (let i = 0; i < height; i++) {
                  newMap.push([]);
                  for (let j = 0; j < width; j++) {
                    if (i === x && j === y) {
                      if (usermap[i][j] === 0) {
                        newMap[i].push(1)
                      } else {
                        newMap[i].push(0)
                      };
                    } else {
                      newMap[i].push(usermap[i][j]);
                    }
                  }
                }
                console.log(newMap);
                setMap(() => newMap);
              }
              }
              />
            })}
          </Row>
        )
        }
      </div>

      <button style={{marginTop: "20px", padding: "5px"}} onClick={copyMapDetails}>Generate Maze</button>
    </div>
  );
}

export default App;