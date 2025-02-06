CREATE DATABASE ArtiklarDB;
USE ArtiklarDB;

CREATE TABLE news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    summary TEXT,
    link TEXT,
    published DATETIME,
    topic TEXT
);

ALTER TABLE news
ADD COLUMN politik TINYINT DEFAULT 0,
ADD COLUMN utbildning TINYINT DEFAULT 0,
ADD COLUMN religion TINYINT DEFAULT 0,
ADD COLUMN miljo TINYINT DEFAULT 0,
ADD COLUMN ekonomi TINYINT DEFAULT 0,
ADD COLUMN livsstilfritt TINYINT DEFAULT 0,
ADD COLUMN samhallekonflikter TINYINT DEFAULT 0,
ADD COLUMN halsa TINYINT DEFAULT 0,
ADD COLUMN idrott TINYINT DEFAULT 0,
ADD COLUMN vetenskapteknik TINYINT DEFAULT 0;
-------------------------------------------------------------------
---
SELECT * FROM news;
TRUNCATE TABLE news;

--- Kolla tomma rader i topic---
SELECT 
    CASE 
        WHEN topic IS NULL OR topic = '' THEN 'Tomma värden' 
        ELSE 'Fyllda värden' 
    END AS topic_status,
    COUNT(*) AS count
FROM news
GROUP BY topic_status;

