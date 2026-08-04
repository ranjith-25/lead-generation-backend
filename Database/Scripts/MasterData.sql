SELECT current_database();


CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    roleName VARCHAR(50) NOT NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    fullName VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashedPassword VARCHAR(150) NULL,
    refUID VARCHAR(50) NULL,
    passwordResetAt TIMESTAMP NULL,
    role_id INT REFERENCES roles(role_id) ON DELETE SET NULL,
    reporting_to INT REFERENCES users(user_id) ON DELETE SET NULL,
    specialization VARCHAR(100) NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    role_id INT REFERENCES roles(role_id) ON DELETE CASCADE,
    assignedAt TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE menus (
    menu_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE menu_roles (
    menu_id INT REFERENCES menus(menu_id) ON DELETE CASCADE,
    role_id INT REFERENCES roles(role_id) ON DELETE CASCADE,
    assignedAt TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (menu_id, role_id)
);

INSERT INTO roles("roleName") VALUES
('Super Admin'),
('BD-Executive'),
('BD-Manager'),
('Team Lead'),
('Manager');

INSERT INTO users("fullName", "email", "hashedPassword", "refUID", "role_id") VALUES
('Super Admin', 'admin@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF001', 1),
('BD-Executive', 'dbexecutive@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF002', 2),
('BD-Manager', 'dbmanager@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF003', 3),
('Nandakishor', 'test@test.com', 'password', 'REF004', 1);

INSERT INTO menus("name", "description") VALUES 
('AI Discovery', 'AI Descovery screen'),
('KPI Dashboard', 'Menu items responsible to show all the kpi'),
('Opportunity Pipeline', 'Opportunity pipelines'),
('User Profiles', 'User Profile details '),
('Projects', 'List of unique projects'),
('Team Hierarchy', 'Menu item responsible to see Team Hierarchy'),
('Dashboard', 'Menu Item for dashboard Screen'),
('Settings', 'Menu Item for Settings');

INSERT INTO menu_roles("menu_id", "role_id") VALUES
(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
(1, 3), (3, 3), (4, 3), (5, 3), (6, 3),
(2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
(1, 4), (3, 4), (4, 4), (5, 4), (6, 4),
(1, 5), (3, 5), (4, 5), (5, 5), (6, 5);

INSERT INTO users("fullName", "email", "hashedPassword", "refUID", "reporting_to") VALUES
('User 1', 'user1@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF005', 3),
('User 2', 'user2@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF006', 3);