DROP TABLE IF EXISTS works;
CREATE TABLE works (
    product_id TEXT PRIMARY KEY,
    work_name TEXT,
    circle_name TEXT,
    price INTEGER,
    release_date TEXT,
    days_elapsed INTEGER,
    age_rating TEXT,
    category TEXT,
    file_format TEXT,
    genres TEXT,
    other TEXT,
    file_size TEXT,
    sales INTEGER,
    average_rating REAL,
    favorites INTEGER,
    reviews INTEGER,
    product_link TEXT,
    circle_link TEXT
);
