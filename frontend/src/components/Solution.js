import React from "react";
import "../styles/Grid.css";

const Solution = ({ solution }) => {
  return (
    <div className="solution">
      <h2>Solution</h2>
      <div className="grid">
        {solution.map((row, rowIndex) =>
          row.map((cell, colIndex) => (
            <div key={`${rowIndex}-${colIndex}`} className="cell">
              {cell}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Solution;
