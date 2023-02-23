import "./App.css";
import React, { useState, useEffect } from "react";
import Cell from "./Cell";
import Row from "./Row";

function App() {
  const [width, setWidth] = useState(10);
  const [height, setHeight] = useState(10);
  const [start, setStart] = useState("0,0");
  const [goal, setGoal] = useState(`${height - 1}, ${width - 1}`);
  const [usermap, setMap] = useState(
    [...Array(width)].map((_, y) => [...Array(height)].map(() => 0))
  );

  const startPos = start.split(",").map((x) => parseInt(x));
  const goalPos = goal.split(",").map((x) => parseInt(x));

  const copyMapDetails = () => {
    var csv = usermap.map((row) => "[" + row.join(",") + "],").join("\n");

    navigator.clipboard.writeText(
      "maze = [" + csv + "]" + "\nstart = (" + start + ")\nend = (" + goal + ")"
    );
  };

  useEffect(() => {
    let newMap = [];
    for (let i = 0; i < height; i++) {
      newMap.push([]);
      for (let j = 0; j < width; j++) {
        try {
          newMap[i].push(usermap[i][j] || 0);
        }
        catch {
          newMap[i].push(0);
        }
      }
    }
    setMap(newMap);
  }, [width, height])

  const toggleCell = (row, col) => {
    var newMap = usermap.map((_, y2) => {
      return usermap[row].map((_, x2) => {
        if (row === y2 && col === x2) {
          console.log(usermap[row][col])
          return (usermap[row][col] === 0) ? 1 : 0;
        }
        return usermap[y2][x2]
      })
    })
    console.log(newMap);
    setMap(newMap);
  }

  return (
    <div className="App">
      <div
        style={{
          display: "flex",
          gap: "10px",
          width: "100%",
          height: "50px",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <p>Enter Width</p>
        <input
          type={"number"}
          value={width}
          onChange={(e) => setWidth(parseInt(e.target.value))}
        />
        <p>Enter Height</p>
        <input
          type={"number"}
          value={height}
          onChange={(e) => setHeight(parseInt(e.target.value))}
        />
      </div>
      <div
        style={{
          display: "flex",
          gap: "10px",
          width: "100%",
          height: "50px",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <p>Enter start</p>
        <input value={start} onChange={(e) => setStart(e.target.value)} />
        <p>Enter goal</p>
        <input value={goal} onChange={(e) => setGoal(e.target.value)} />
      </div>

      <div
        style={{
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          paddingTop: "40px",
        }}
      >
        {usermap.map((map_row, row) => {
          return <Row>
            {map_row.map((val, col) => {
              return (
                <Cell
                  start={startPos[0] === col && startPos[1] === row}
                  end={goalPos[0] === col && goalPos[1] === row}
                  free={usermap[row][col] === 0}
                  setObstacle={() => toggleCell(row, col)}
                />
              );
            })}
          </Row>
        })}
      </div>

      <button
        style={{ marginTop: "20px", padding: "5px" }}
        onClick={copyMapDetails}
      >
        Copy Maze Details
      </button>
    </div>
  );
}

export default App;