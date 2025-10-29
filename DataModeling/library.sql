CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE readers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    reader_id INTEGER NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    returned BOOLEAN DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
    FOREIGN KEY (reader_id) REFERENCES readers (id) ON DELETE CASCADE
);

INSERT INTO books (title, author, genre) VALUES
('Clean Code', 'Robert C. Martin', 'Software Engineering'),
('Harry Potter', 'J.K. Rowling', 'Fantasy'),
('The Pragmatic Programmer', 'Andrew Hunt', 'Programming'),
('Deep Work', 'Cal Newport', 'Productivity'),
('Atomic Habits', 'James Clear', 'Self-help');

INSERT INTO readers (name, email) VALUES
('Nguyễn Đình Bình', 'binh@uet.com'),
('Trịnh Quang Hưng', 'hung@uet.com'),
('Nguyễn Văn A', 'a@uet.com'),
('Trần Thị B', 'b@uet.com');

INSERT INTO loans (book_id, reader_id, borrow_date, due_date, returned) VALUES
(1, 1, '2025-10-01', '2025-10-20', 0),
(2, 1, '2025-10-05', '2025-10-25', 1),
(3, 2, '2025-10-10', '2025-10-30', 0);
