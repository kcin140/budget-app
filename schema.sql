-- Users table
CREATE TABLE users (
  id VARCHAR(36) NOT NULL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
  id INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1),
  name VARCHAR(255),
  planned_amount DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT CURRENT TIMESTAMP,
  PRIMARY KEY (id)
);

-- Transactions table
CREATE TABLE transactions (
  id INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1),
  user_id VARCHAR(36) NOT NULL,
  category_id INTEGER,
  amount DECIMAL(10, 2),
  vendor VARCHAR(255),
  notes VARCHAR(1000),
  timestamp TIMESTAMP DEFAULT CURRENT TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Categorization rules table
CREATE TABLE categorization_rules (
  id INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1),
  vendor_pattern VARCHAR(255),
  keyword_pattern VARCHAR(255),
  category_id INTEGER,
  PRIMARY KEY (id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Seed Categories
INSERT INTO categories (name, planned_amount) VALUES
('Grocery (Costco)', 500),
('Grocery (Aldi)', 300),
('Eating Out', 200),
('Gas', 150),
('Rent', 1500),
('Utilities', 200),
('Entertainment', 100),
('Miscellaneous', 100);
