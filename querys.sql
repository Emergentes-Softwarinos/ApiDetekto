CREATE DATABASE IF NOT EXISTS ferreteria;

USE ferreteria;

CREATE TABLE martillos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

INSERT INTO martillos (nombre, cantidad, precio) VALUES
('Martillo de carpintero', 25, 29.90),
('Martillo de bola', 15, 35.00),
('Martillo demoledor', 10, 59.99),
('Martillo de goma', 20, 22.50),
('Martillo eléctrico', 5, 199.90),
('Martillo perforador', 8, 139.00),
('Martillo combinado', 6, 149.90),
('Martillo de latonero', 18, 33.50),
('Martillo de encofrador', 12, 41.80),
('Martillo de tapicero', 9, 26.00);