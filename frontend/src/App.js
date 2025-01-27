import React, { useState } from "react";
import Grid from "./components/Grid";
import Solution from "./components/Solution";
import Header from "./components/Header";
import { solveSudoku } from "./api";
import "./styles/App.css";

const App = () => {
  const [grid, setGrid] = useState(Array(9).fill(Array(9).fill("")));
  const [solution, setSolution] = useState(null);
  const [error, setError] = useState("");

  const handleSolve = async () => {
    try {
      const response = await solveSudoku(grid);
      setSolution(response.solvedBoard);
      setError("");
    } catch (err) {
      setError(err.message || "Something went wrong.");
    }
  };

  const handleReset = () => {
    setGrid(Array(9).fill(Array(9).fill("")));
    setSolution(null);
    setError("");
  };

  return (
    <div className="App">
      <Header />
      <div className="content">
        <Grid grid={grid} setGrid={setGrid} />
        <button className="solve-button" onClick={handleSolve}>
          Solve Sudoku
        </button>
        <button className="reset-button" onClick={handleReset}>
          Reset
        </button>
        {error && <div className="error">{error}</div>}
        {solution && <Solution solution={solution} />}
      </div>
    </div>
  );
};

export default App;
