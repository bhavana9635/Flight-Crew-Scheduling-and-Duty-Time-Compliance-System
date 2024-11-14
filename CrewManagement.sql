-- Create the database
DROP DATABASE IF EXISTS CrewManagement;
CREATE DATABASE CrewManagement;
USE CrewManagement;

-- Create Admin table
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(64) NOT NULL  -- For storing SHA-256 hashed passwords
);

-- Create CrewMember table
CREATE TABLE CrewMember (
    crew_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    crew_role VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    status VARCHAR(20) DEFAULT 'Active',
    password VARCHAR(64) NOT NULL  -- For storing SHA-256 hashed passwords
);

-- Create Flight table
CREATE TABLE Flight (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_number VARCHAR(20) UNIQUE NOT NULL,
    departure VARCHAR(100) NOT NULL,
    arrival VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL
);

-- Create Airport table
CREATE TABLE Airport (
    airport_id INT PRIMARY KEY AUTO_INCREMENT,
    airport_code VARCHAR(10) UNIQUE NOT NULL,
    airport_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

-- Create CrewAssignment table
CREATE TABLE CrewAssignment (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    crew_id INT NOT NULL,
    flight_id INT NOT NULL,
    assignment_date DATE NOT NULL,
    FOREIGN KEY (crew_id) REFERENCES CrewMember(crew_id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id) ON DELETE CASCADE
);

-- Create CrewLeave table
CREATE TABLE CrewLeave (
    leave_id INT PRIMARY KEY AUTO_INCREMENT,
    crew_id INT NOT NULL,
    leave_start DATE NOT NULL,
    leave_end DATE NOT NULL,
    FOREIGN KEY (crew_id) REFERENCES CrewMember(crew_id) ON DELETE CASCADE
);

-- Create DutyLog table
CREATE TABLE DutyLog (
    duty_log_id INT PRIMARY KEY AUTO_INCREMENT,
    crew_id INT NOT NULL,
    flight_id INT NOT NULL,
    duty_date DATE NOT NULL,
    duty_status VARCHAR(20) NOT NULL,
    FOREIGN KEY (crew_id) REFERENCES CrewMember(crew_id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id) ON DELETE CASCADE
);

-- Create Regulation table
CREATE TABLE Regulation (
    regulation_id INT PRIMARY KEY AUTO_INCREMENT,
    regulation_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL
);

-- Add indexes for better query performance
CREATE INDEX idx_crew_email ON CrewMember(email);
CREATE INDEX idx_flight_number ON Flight(flight_number);
CREATE INDEX idx_airport_code ON Airport(airport_code);
CREATE INDEX idx_assignment_date ON CrewAssignment(assignment_date);
CREATE INDEX idx_leave_dates ON CrewLeave(leave_start, leave_end);
CREATE INDEX idx_duty_date ON DutyLog(duty_date);

-- Insert sample data
-- Add Admin
INSERT INTO Admin (name, email, phone, password) 
VALUES ('Admin User', 'admin@airline.com', '1234567890', SHA2('admin123', 256));

-- Add Airports
INSERT INTO Airport (airport_code, airport_name, location) VALUES
('LHR', 'Heathrow Airport', 'London, UK'),
('JFK', 'John F Kennedy Airport', 'New York, USA'),
('DXB', 'Dubai International Airport', 'Dubai, UAE');

-- Add Flights
INSERT INTO Flight (flight_number, departure, arrival, status) VALUES
('FL001', 'LHR', 'JFK', 'Scheduled'),
('FL002', 'JFK', 'LHR', 'Scheduled'),
('FL003', 'LHR', 'DXB', 'Scheduled');

-- Add Crew Members
INSERT INTO CrewMember 
(first_name, last_name, date_of_birth, crew_role, hire_date, email, phone_number, password) VALUES
('John', 'Smith', '1990-05-15', 'Pilot', '2020-01-01', 'john.smith@airline.com', '1234567890', SHA2('pass123', 256)),
('Sarah', 'Johnson', '1992-08-22', 'Flight Attendant', '2021-03-15', 'sarah.j@airline.com', '2345678901', SHA2('pass456', 256)),
('Mike', 'Wilson', '1988-12-10', 'Co-Pilot', '2019-06-01', 'mike.w@airline.com', '3456789012', SHA2('pass789', 256));

-- Add Crew Assignments
INSERT INTO CrewAssignment (crew_id, flight_id, assignment_date) VALUES
(1, 1, '2024-11-15'),
(2, 1, '2024-11-15'),
(3, 2, '2024-11-16');

-- Add Crew Leave records
INSERT INTO CrewLeave (crew_id, leave_start, leave_end) VALUES
(1, '2024-12-20', '2024-12-27'),
(2, '2024-12-25', '2024-12-31');

-- Add Duty Logs
INSERT INTO DutyLog (crew_id, flight_id, duty_date, duty_status) VALUES
(1, 1, '2024-11-15', 'Completed'),
(2, 1, '2024-11-15', 'Completed'),
(3, 2, '2024-11-16', 'Scheduled');

-- Add Regulations
INSERT INTO Regulation (regulation_name, description)
VALUES 
('Flight Time Limitation', 'Maximum flight time of 100 hours in any 28 consecutive days'),
('Rest Period', 'Minimum rest period of 12 hours between duty periods'),
('Duty Period', 'Maximum duty period of 14 hours in any 24 consecutive hours');

-- Create Trigger
DELIMITER //
CREATE TRIGGER after_crew_status_change
AFTER UPDATE ON CrewMember
FOR EACH ROW
BEGIN
    IF NEW.status != OLD.status THEN
        INSERT INTO DutyLog (crew_id, flight_id, duty_date, duty_status)
        VALUES (NEW.crew_id, 
               (SELECT flight_id FROM CrewAssignment WHERE crew_id = NEW.crew_id ORDER BY assignment_date DESC LIMIT 1), 
               CURDATE(), 
               CONCAT('Status changed from ', OLD.status, ' to ', NEW.status));
    END IF;
END;
//
DELIMITER ;

-- Create Procedures
DELIMITER //
CREATE PROCEDURE AssignCrewToFlight(
    IN p_crew_id INT,
    IN p_flight_id INT,
    IN p_assignment_date DATE
)
BEGIN
    -- Check if crew_id exists
    IF NOT EXISTS (SELECT 1 FROM CrewMember WHERE crew_id = p_crew_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid crew_id';
    END IF;
    
    -- Check if flight_id exists
    IF NOT EXISTS (SELECT 1 FROM Flight WHERE flight_id = p_flight_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid flight_id';
    END IF;
    
    -- Check if crew member is on leave
    IF EXISTS (
        SELECT 1 FROM CrewLeave 
        WHERE crew_id = p_crew_id 
        AND p_assignment_date BETWEEN leave_start AND leave_end
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Crew member is on leave for the specified date';
    ELSE
        INSERT INTO CrewAssignment (crew_id, flight_id, assignment_date)
        VALUES (p_crew_id, p_flight_id, p_assignment_date);
        
        -- Also log the duty
        INSERT INTO DutyLog (crew_id, flight_id, duty_date, duty_status)
        VALUES (p_crew_id, p_flight_id, p_assignment_date, 'Scheduled');
        
        SELECT 'Crew assigned successfully' AS message;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CheckCrewFlightHours(
    IN p_crew_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    -- Check if crew_id exists
    IF NOT EXISTS (SELECT 1 FROM CrewMember WHERE crew_id = p_crew_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid crew_id';
    ELSE
        SELECT 
            cm.first_name,
            cm.last_name,
            COUNT(ca.flight_id) as total_flights,
            COUNT(ca.flight_id) * 2 as estimated_flight_hours
        FROM CrewMember cm
        LEFT JOIN CrewAssignment ca ON cm.crew_id = ca.crew_id
        WHERE cm.crew_id = p_crew_id
        AND ca.assignment_date BETWEEN p_start_date AND p_end_date
        GROUP BY cm.crew_id, cm.first_name, cm.last_name;
    END IF;
END //
DELIMITER ;

-- Example Queries:
-- 1. Nested Query (Find crew members who worked on London flights)
SELECT DISTINCT cm.first_name, cm.last_name
FROM CrewMember cm
WHERE cm.crew_id IN (
    SELECT ca.crew_id 
    FROM CrewAssignment ca
    WHERE ca.flight_id IN (
        SELECT f.flight_id 
        FROM Flight f 
        WHERE f.departure = 'LHR' OR f.arrival = 'LHR'
    )
);

-- 2. JOIN Query (Get all crew assignments with details)
SELECT 
    cm.first_name,
    cm.last_name,
    f.flight_number,
    f.departure,
    f.arrival,
    ca.assignment_date
FROM CrewMember cm
INNER JOIN CrewAssignment ca ON cm.crew_id = ca.crew_id
INNER JOIN Flight f ON ca.flight_id = f.flight_id
ORDER BY ca.assignment_date;

-- 3. Aggregation Query (Get total flights per crew member in last month)
SELECT 
    cm.first_name,
    cm.last_name,
    COUNT(ca.flight_id) as total_flights
FROM CrewMember cm
LEFT JOIN CrewAssignment ca ON cm.crew_id = ca.crew_id
WHERE ca.assignment_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY cm.crew_id, cm.first_name, cm.last_name
HAVING total_flights > 0;

-- Example procedure calls
CALL AssignCrewToFlight(1, 3, '2024-11-20');
CALL CheckCrewFlightHours(1, '2024-11-01', '2024-11-30');