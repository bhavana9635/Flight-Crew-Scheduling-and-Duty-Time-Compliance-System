-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS CrewManagement;
USE CrewManagement;

-- Create Admin Table
CREATE TABLE IF NOT EXISTS Admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    password VARCHAR(256)  -- Store hashed password
);

-- Create Airport Table
CREATE TABLE IF NOT EXISTS Airport (
    airport_code VARCHAR(10) PRIMARY KEY,
    airport_name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50)
);

-- Create CrewMember Table
CREATE TABLE IF NOT EXISTS CrewMember (
    crew_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    crew_role VARCHAR(50),
    hire_date DATE,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(15),
    duty_hours_completed DECIMAL(5,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Active'
);

-- Create Flight Table
CREATE TABLE IF NOT EXISTS Flight (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_number VARCHAR(10),
    departure_airport VARCHAR(10),
    arrival_airport VARCHAR(10),
    departure_time DATETIME,
    arrival_time DATETIME,
    status VARCHAR(20),
    FOREIGN KEY (departure_airport) REFERENCES Airport(airport_code),
    FOREIGN KEY (arrival_airport) REFERENCES Airport(airport_code)
);

-- Create CrewAssignment Table
CREATE TABLE IF NOT EXISTS CrewAssignment (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    crew_id INT,
    flight_id INT,
    assigned_role VARCHAR(50),
    assignment_date DATE,
    duty_start_time DATETIME,
    duty_end_time DATETIME,
    FOREIGN KEY (crew_id) REFERENCES CrewMember(crew_id),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id)
);

-- Create DutyLog Table
CREATE TABLE IF NOT EXISTS DutyLog (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    crew_id INT,
    log_date DATE,
    duty_hours DECIMAL(5,2),
    duty_compliance VARCHAR(10),
    FOREIGN KEY (crew_id) REFERENCES CrewMember(crew_id)
);

-- Create Regulation Table
CREATE TABLE IF NOT EXISTS Regulation (
    regulation_id INT PRIMARY KEY AUTO_INCREMENT,
    max_duty_hours_per_day DECIMAL(5,2),
    max_duty_hours_per_week DECIMAL(5,2),
    rest_period DECIMAL(5,2)
);

-- Create the GetTotalDutyHours Function
DELIMITER //
CREATE FUNCTION GetTotalDutyHours(p_crew_id INT) 
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_hours DECIMAL(5,2);
    SELECT SUM(duty_hours) INTO total_hours FROM DutyLog WHERE crew_id = p_crew_id;
    RETURN IFNULL(total_hours, 0);
END;
//
DELIMITER ;

-- Create a Trigger to Update Duty Hours when a new log is added
DELIMITER //
CREATE TRIGGER UpdateDutyHours
AFTER INSERT ON DutyLog
FOR EACH ROW
BEGIN
    UPDATE CrewMember 
    SET duty_hours_completed = duty_hours_completed + NEW.duty_hours
    WHERE crew_id = NEW.crew_id;
END;
//
DELIMITER ;

-- Create a Trigger to Update Duty Hours when a log is deleted
DELIMITER //
CREATE TRIGGER DecrementDutyHours
AFTER DELETE ON DutyLog
FOR EACH ROW
BEGIN
    UPDATE CrewMember 
    SET duty_hours_completed = duty_hours_completed - OLD.duty_hours
    WHERE crew_id = OLD.crew_id;
END;
//
DELIMITER ;

-- Create a Stored Procedure to Add a New Crew Member
DELIMITER //
CREATE PROCEDURE AddCrewMember(
    IN p_first_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_date_of_birth DATE,
    IN p_crew_role VARCHAR(50),
    IN p_hire_date DATE,
    IN p_email VARCHAR(100),
    IN p_phone_number VARCHAR(15)
)
BEGIN
    INSERT INTO CrewMember (first_name, last_name, date_of_birth, crew_role, hire_date, email, phone_number, status)
    VALUES (p_first_name, p_last_name, p_date_of_birth, p_crew_role, p_hire_date, p_email, p_phone_number, 'Active');
END;
//
DELIMITER ;

-- Example query to get crew members with their total duty hours
SELECT 
    cm.crew_id, 
    CONCAT(cm.first_name, ' ', cm.last_name) AS full_name, 
    GetTotalDutyHours(cm.crew_id) AS total_duty_hours
FROM 
    CrewMember cm;

-- Example query to retrieve all admins
SELECT * FROM Admin;

-- Example query to retrieve all flights with their departure and arrival airports
SELECT 
    f.flight_id,
    f.flight_number,
    a1.airport_name AS departure_airport,
    a2.airport_name AS arrival_airport,
    f.departure_time,
    f.arrival_time,
    f.status
FROM 
    Flight f
JOIN 
    Airport a1 ON f.departure_airport = a1.airport_code
JOIN 
    Airport a2 ON f.arrival_airport = a2.airport_code;

ALTER TABLE CrewMember ADD COLUMN password VARCHAR(255);
