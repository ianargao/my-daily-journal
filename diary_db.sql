CREATE DATABASE IF NOT EXISTS diary_db;

USE diary_db;


-- USERS TABLE

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- DIARY ENTRIES TABLE

CREATE TABLE IF NOT EXISTS diary_entries (
    entry_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    entry_date DATE NOT NULL,
    title VARCHAR(100) NOT NULL,
    mood VARCHAR(30) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- VIEW ALL USERS AND THEIR DIARY ENTRIES

SELECT
    users.username,
    diary_entries.entry_id,
    diary_entries.entry_date,
    diary_entries.title,
    diary_entries.mood,
    diary_entries.content
FROM users
JOIN diary_entries
    ON users.user_id = diary_entries.user_id;

-- Optional sample account:
-- The password is not inserted here because Flask hashes passwords.
-- Register through the website first.
