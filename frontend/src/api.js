import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000"; // Flask backend URL

export const solveSudoku = async (grid) => {
  const response = await axios.post(`${API_BASE_URL}/solve-sudoku`, { board: grid });
  return response.data;
};
