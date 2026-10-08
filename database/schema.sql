CREATE DATABASE IF NOT EXISTS road_monitoring;
USE road_monitoring;

DROP TABLE IF EXISTS potholes;

CREATE TABLE potholes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route VARCHAR(50),
    timestamp DATETIME,
    confidence FLOAT,
    risk_level VARCHAR(20),
    severity_score FLOAT,
    latitude FLOAT,
    longitude FLOAT
);

-- Sample data (replace with real YOLO detections later)
INSERT INTO potholes
(route, timestamp, confidence, risk_level, severity_score, latitude, longitude)
VALUES
('Route A', NOW(), 0.94, 'HIGH',   0.91, 23.2599, 77.4126),
('Route A', NOW(), 0.88, 'HIGH',   0.84, 23.2605, 77.4130),
('Route A', NOW(), 0.82, 'MEDIUM', 0.61, 23.2610, 77.4135),
('Route B', NOW(), 0.91, 'LOW',    0.32, 23.2500, 77.4000),
('Route B', NOW(), 0.89, 'MEDIUM', 0.55, 23.2510, 77.4010),
('Route C', NOW(), 0.96, 'HIGH',   0.88, 23.2700, 77.4200);
