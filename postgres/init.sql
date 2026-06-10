CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO customers(name, age)
VALUES ('John', 30);