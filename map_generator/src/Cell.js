import { useState } from "react";
import "./Cell.css";

function Cell({ start = false, end = false, free, setObstacle }) {
  return (
    <div
      className={"cell"}
      onClick={setObstacle}
      style={{
        backgroundColor: start
          ? "lightblue"
          : end
          ? "LIGHTgreen"
          : free
          ? "white"
          : "grey",
      }}
    >
      {free ? 0 : 1}
    </div>
  );
}

export default Cell;
