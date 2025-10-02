import React, { useState, useEffect } from "react";
import "../style/MyBookshieldPage.css";

function MyBookshieldPage() {
  const [borrowedBooks, setBorrowedBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);

  const fetchBorrowedBooks = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/books");
      const data = await res.json();
      setBorrowedBooks(data);
    } catch (err) {
      console.error("Lỗi khi lấy sách đã mượn:", err);
    }
  };

  useEffect(() => {
    fetchBorrowedBooks();
  }, []);

  const handleReturn = async (bookKey) => {
    try {
      const res = await fetch(`http://localhost:5000/api/return/${bookKey}`, {
        method: "DELETE",
      });
      const result = await res.json();
      alert(result.message);
      setSelectedBook(null);
      fetchBorrowedBooks();
    } catch (err) {
      console.error("Lỗi khi trả sách:", err);
      console.error(bookKey);
    }
  };

  return (
    <div className="mybookshield-container">
      {/* Cột trái: danh sách đã mượn */}
      <div className="mybookshield-left">
        <h2>My Bookshield</h2>
        {borrowedBooks.length === 0 ? (
          <p>Chưa có sách nào được mượn.</p>
        ) : (
          <div className="book-list">
            {borrowedBooks.map((book) => (
              <div
                key={book.book_key}
                className="book-item"
                onClick={() => setSelectedBook(book)}
              >
                <img src={book.cover_url} alt={book.title} />
                <div>
                  <strong>{book.title}</strong>
                  <p>{book.author}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Cột phải: thông tin chi tiết */}
      <div className="mybookshield-right">
        {selectedBook ? (
          <>
            <img src={selectedBook.cover_url} alt={selectedBook.title} />
            <h3>{selectedBook.title}</h3>
            <p>
              <strong>Author:</strong> {selectedBook.author}
            </p>
            <button onClick={() => handleReturn(selectedBook.book_key)}>
              Trả sách
            </button>
          </>
        ) : (
          <p>Chọn sách để xem chi tiết và trả.</p>
        )}
      </div>
    </div>
  );
}

export default MyBookshieldPage;
