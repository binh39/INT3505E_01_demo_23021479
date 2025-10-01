import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Header from "./components/Header";
import LibraryPage from "./pages/LibraryPage";
import MyBookshieldPage from "./pages/MyBookshieldPage";

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Navigate to="/library" />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/mybookshield" element={<MyBookshieldPage />} />
      </Routes>
    </Router>
  );
}

export default App;
