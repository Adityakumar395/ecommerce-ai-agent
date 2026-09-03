-- Database dump for E-commerce AI Agent
CREATE DATABASE IF NOT EXISTS ecommerce_ai;
USE ecommerce_ai;

CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(255) NOT NULL,
  `customer_name` varchar(100) DEFAULT NULL,
  `review_text` text NOT NULL,
  `sentiment` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (1, 'Smartwatch X', 'Rahul', 'The display is good but battery drains very fast.', 'positive', '2026-08-28 21:52:05') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (2, 'Smartwatch X', 'Priya', 'Awesome design and very fast delivery!', 'positive', '2026-08-28 21:52:05') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (3, 'Bluetooth Speaker', 'Amit', 'Sound quality is very bad, completely waste of money.', 'negative', '2026-08-28 21:52:05') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (4, 'Galaxy Smartphone', 'Vikash', 'Camera is fantastic, but the battery drains very fast if you use 5G.', 'positive', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (5, 'Galaxy Smartphone', 'Neha', 'Perfect display and very smooth performance. Highly recommended!', 'positive', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (6, 'Probook Laptop', 'Ravi', 'Keyboard quality is poor, keys stopped working after a week.', 'negative', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (7, 'Probook Laptop', 'Sanjay', 'Good for coding and office work. SSD makes it very fast.', 'positive', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (8, 'Noise Cancelling Headphones', 'Simran', 'Bass is too heavy, mids are completely lost. Not for classical music.', 'neutral', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (9, 'Noise Cancelling Headphones', 'Karan', 'Active noise cancellation is top notch. Best for flights.', 'positive', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (10, 'Smart Coffee Maker', 'Anjali', 'App connectivity drops frequently. Very frustrating to use.', 'neutral', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (11, 'Smart Coffee Maker', 'Mohit', 'Brews the perfect cup of coffee every morning. Love the scheduling feature.', 'positive', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (12, 'Robot Vacuum', 'Sonia', 'It gets stuck under the sofa every single day. Waste of money.', 'negative', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (13, 'Robot Vacuum', 'Rahul', 'Cleans animal hair perfectly. A lifesaver for pet owners.', 'neutral', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (14, 'Fast Charging Powerbank', 'Pooja', 'Bulky and heavy to carry, but charges my phone 4 times.', 'neutral', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (15, 'Fast Charging Powerbank', 'Deepak', 'Stopped working completely after 10 days. Need a refund.', 'negative', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);
INSERT INTO reviews (id, product_name, customer_name, review_text, sentiment, created_at) VALUES (16, 'RGB Mechanical Keyboard', 'Aman', 'Switches are loud but the typing feel is amazing for programmers.', 'positive', '2026-09-02 22:00:55') ON DUPLICATE KEY UPDATE product_name=VALUES(product_name);