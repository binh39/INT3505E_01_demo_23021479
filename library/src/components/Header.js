import React from "react";
import { Link } from "react-router-dom";
import "../style/Header.css";

function Header() {
  return (
    <header className="header">
      <div className="logo">MyLibrary</div>
      <nav className="menu">
        <Link to="/library">Library</Link>
        <Link to="/mybookshield">My Bookshield</Link>
      </nav>
    </header>
  );
}

export default Header;
