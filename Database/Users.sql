SELECT current_database();


CREATE TABLE roles(
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roleName VARCHAR(50) NOT NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT NOW()
)
CREATE TABLE users(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fullName VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashedPassword VARCHAR(150) NULL,
    refUID VARCHAR(50) NULL,
    passwordResetAt TIMESTAMP NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT NOW())


CREATE TABLE user_roles(
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    assignedAt TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id,role_id)
)

INSERT INTO users(fullName,email,hashedPassword,refUID)
VALUES ('Super_Admin', 'admin@example.com', '$argon2id$v=19$m=65536,t=3,p=4$...', gen_random_uuid());


INSERT INTO roles(roleName)
VALUES('superadmin') INSERT INTO user_roles(user_id,role_id) VALUES ('7d09480d-d1df-4b7f-8576-837b574750bb','4177e7cd-ae7b-4331-a8ea-778cf7f3a321')