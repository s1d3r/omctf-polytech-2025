DROP TABLE IF EXISTS event_history CASCADE;
DROP TABLE IF EXISTS event_tasks CASCADE;
DROP TABLE IF EXISTS event_orgs CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS users CASCADE;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    email VARCHAR(120),
    first_name VARCHAR(50),
    second_name VARCHAR(50),
    role VARCHAR(20),
    avatar TEXT,
    created_at TIMESTAMP
);


CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    owner_id INT NOT NULL,
    invitecode TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50),
    date DATE,
    time TIME,
    location_name VARCHAR(255),
    location_address VARCHAR(255),
    location_room VARCHAR(255),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE event_orgs (
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    PRIMARY KEY(event_id, user_id)
);


CREATE TABLE event_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    text TEXT,
    completed BOOLEAN,
    assigned_to VARCHAR(255),
    priority VARCHAR(20),
    deadline DATE
);


CREATE TABLE event_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    action TEXT,
    timestamp TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER prevent_owner_invite_update
BEFORE UPDATE ON events
FOR EACH ROW
BEGIN
    IF OLD.owner_id <> NEW.owner_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'You cannot change the owner_id of an event';
    END IF;

    IF OLD.invitecode <> NEW.invitecode THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'You cannot change the invitecode of an event';
    END IF;

    IF OLD.title <> NEW.title THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'You cannot change the title of an event';
    END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER prevent_username_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    IF OLD.username <> NEW.username THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'You cannot change username';
    END IF;

END$$
DELIMITER ;


DELIMITER $$
CREATE TRIGGER log_event_insert
AFTER INSERT ON events
FOR EACH ROW
BEGIN
    INSERT INTO event_history (event_id, action, timestamp)
    VALUES (
        NEW.id,
        CONCAT('Event created: ', NEW.title),
        NOW()
    );
END$$
DELIMITER ;



DELIMITER $$

CREATE TRIGGER log_event_update
AFTER UPDATE ON events
FOR EACH ROW
BEGIN
    DECLARE changes TEXT DEFAULT '';

    -- Проверяем статус
    IF OLD.status <> NEW.status THEN
        SET changes = CONCAT(changes, 'Status: "', OLD.status, '" → "', NEW.status, '"; ');
    END IF;

    -- Проверяем описание
    IF OLD.description <> NEW.description THEN
        SET changes = CONCAT(changes, 'Description: "', OLD.description, '" → "', NEW.description, '"; ');
    END IF;

    -- Проверяем дату
    IF OLD.date <> NEW.date THEN
        SET changes = CONCAT(changes, 'Date: "', OLD.date, '" → "', NEW.date, '"; ');
    END IF;

    -- Проверяем время
    IF OLD.time <> NEW.time THEN
        SET changes = CONCAT(changes, 'Time: "', OLD.time, '" → "', NEW.time, '"; ');
    END IF;

    -- Проверяем адрес
    IF OLD.location_address <> NEW.location_address THEN
        SET changes = CONCAT(changes, 'Location_address: "', OLD.location_address, '" → "', NEW.location_address, '"; ');
    END IF;

    -- Если есть изменения, записываем их в историю
    IF changes <> '' THEN
        INSERT INTO event_history (event_id, action, timestamp)
        VALUES (NEW.id, changes, NOW());
    END IF;

END$$

DELIMITER ;


DELIMITER $$

CREATE TRIGGER trg_event_orgs_insert
AFTER INSERT ON event_orgs
FOR EACH ROW
BEGIN
    DECLARE uname VARCHAR(255);


    INSERT INTO event_history (event_id, action, timestamp)
    VALUES (
        NEW.event_id,
        CONCAT('User ', uname, ' was added as organizer'),
        NOW()
    );
END$$
DELIMITER ;

DELIMITER $$

CREATE TRIGGER log_task_insert
AFTER INSERT ON event_tasks
FOR EACH ROW
BEGIN
    INSERT INTO event_history (event_id, action, timestamp)
    VALUES (
        NEW.event_id,
        CONCAT('Task added: "', NEW.text, '" assigned to ', NEW.assigned_to, ' with priority ', NEW.priority),
        NOW()
    );
END$$

DELIMITER ;
