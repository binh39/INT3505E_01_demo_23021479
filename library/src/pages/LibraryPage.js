import React, { useState, useEffect } from "react";
import "../style/LibraryPage.css";

function LibraryPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [books, setBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);

  useEffect(() => {
    const fetchBooks = async () => {
      const res = await fetch(
        `https://openlibrary.org/search.json?title=${encodeURIComponent(
          searchTerm
        )}&limit=5`
      );

      const data = await res.json();
      setBooks(data.docs.slice(0, 5));
    };
    fetchBooks();
  }, [searchTerm]);

  const handleBorrow = async (book) => {
    // Trích xuất chỉ phần ID từ book.key (/works/OL82548W -> OL82548W)
    const bookId = book.key.split("/").pop();

    const payload = {
      book_key: bookId,
      title: book.title,
      author: book.author_name?.join(", "),
      cover_url: getCoverUrl(book.cover_i),
    };
    console.log("Borrowing book with ID:", bookId, "from key:", book.key);

    try {
      const res = await fetch("http://localhost:5001/api/books", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      alert(result.message);
    } catch (err) {
      console.error("Error borrowing book:", err);
      alert("Lỗi khi mượn sách.");
    }
  };

  const getCoverUrl = (coverId) =>
    coverId
      ? `https://covers.openlibrary.org/b/id/${coverId}-M.jpg`
      : "https://via.placeholder.com/100x150?text=No+Cover";

  return (
    <div className="library-container">
      {/* Cột trái: Search + danh sách sách */}
      <div className="library-main">
        <h2>Library</h2>
        <input
          type="text"
          placeholder="Search books..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <div className="book-list">
          {books.map((book) => (
            <div
              key={book.key}
              className="book-item"
              onClick={() => setSelectedBook(book)}
            >
              <img src={getCoverUrl(book.cover_i)} alt={book.title} />
              <div>
                <strong>{book.title}</strong>
                <p>{book.author_name?.join(", ")}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cột phải: thông tin sách */}
      <div className="library-detail">
        {selectedBook ? (
          <>
            <img
              src={getCoverUrl(selectedBook.cover_i)}
              alt={selectedBook.title}
            />
            <h3>{selectedBook.title}</h3>
            <p>
              <strong>Author:</strong> {selectedBook.author_name?.join(", ")}
            </p>
            <p>
              <strong>First Published:</strong>{" "}
              {selectedBook.first_publish_year || "N/A"}
            </p>
            <button onClick={() => handleBorrow(selectedBook)}>Borrow</button>
          </>
        ) : (
          <p>Select a book to view details...</p>
        )}
      </div>
    </div>
  );
}

export default LibraryPage;
