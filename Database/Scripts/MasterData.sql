SELECT current_database();


CREATE TABLE roles(role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                                                    roleName VARCHAR(50) NOT NULL,
                                                                         createdAt TIMESTAMP NOT NULL DEFAULT NOW())
CREATE TABLE users(user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                                                    fullName VARCHAR(100) NOT NULL,
                                                                          email VARCHAR(100) NOT NULL UNIQUE,
                                                                                                      hashedPassword VARCHAR(150) NULL,
                                                                                                                                  refUID VARCHAR(50) NULL,
                                                                                                                                                     passwordResetAt TIMESTAMP NULL,
                                                                                                                                                                               createdAt TIMESTAMP NOT NULL DEFAULT NOW())
CREATE TABLE user_roles
    (user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                                                      role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
                                                                                                       assignedAt TIMESTAMP NOT NULL DEFAULT NOW(),
                                                                                                                                             PRIMARY KEY (user_id,
                                                                                                                                                          role_id))
INSERT INTO users("user_id",
                  "fullName",
                  "email",
                  "hashedPassword",
                  "refUID")
VALUES (gen_random_uuid(),'Super Admin', 'admin@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', gen_random_uuid());

INSERT INTO users("user_id",
                  "fullName",
                  "email",
                  "hashedPassword",
                  "refUID")
VALUES (gen_random_uuid(),'BD-Executive', 'dbexecutive@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', gen_random_uuid());

INSERT INTO users("user_id",
                  "fullName",
                  "email",
                  "hashedPassword",
                  "refUID")
VALUES (gen_random_uuid(),'BD-Manager', 'dbmanager@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', gen_random_uuid());

UPDATE users
SET "role_id" = '5fe18fa3-cd91-45c7-8e22-4a1cc39d1837'
WHERE "email" ='admin@example.com'

UPDATE users
SET "role_id" = '9f8da996-211b-4891-a33e-517eec17eb8e'
WHERE "email" ='dbexecutive@example.com'

UPDATE users
SET "role_id" = 'd30a585c-4872-4e9e-880f-a33dd8267af0'
WHERE "email" ='dbmanager@example.com'


INSERT INTO users("user_id", "fullName", "email", "hashedPassword", "refUID")
VALUES (gen_random_uuid(), 'Nandakishor', 'test@test.com', 'password', 'REF001');


INSERT INTO roles("role_id","roleName")
VALUES(gen_random_uuid(),'Super Admin')

INSERT INTO roles("role_id","roleName")
VALUES(gen_random_uuid(),'BD-Executive') 

INSERT INTO roles("role_id","roleName")
VALUES(gen_random_uuid(),'BD-Manager') 

INSERT INTO roles("role_id","roleName")
VALUES(gen_random_uuid(),'Team Lead') 

INSERT INTO roles("role_id","roleName")
VALUES(gen_random_uuid(),'Manager') 

INSERT INTO menus("menu_id","name","description")
VALUES 
(gen_random_uuid(),'AI Discovery','AI Descovery screen'),
(gen_random_uuid(),'KPI Dashboard','Menu items responsible to show all the kpi'),
(gen_random_uuid(),'Opportunity Pipeline','Opportunity pipelines'),
(gen_random_uuid(),'User Profiles','User Profile details '),
(gen_random_uuid(),'Projects','List of unique projects'),
(gen_random_uuid(),'Team Hierarchy','Menu item responsible to see Team Hierarchy'),
(gen_random_uuid(),'Dashboard','Menu Item for dashboard Screen'),
(gen_random_uuid(),'Settings','Menu Item for Settings')

INSERT INTO menu_roles("menu_id","role_id")
VALUES
    ('67db1b3a-127b-4e8d-b95e-3bf1cf366f8c','9f8da996-211b-4891-a33e-517eec17eb8e'),
    ('22ca63cf-658a-4a45-ae69-f12105e7565d','9f8da996-211b-4891-a33e-517eec17eb8e'),
    ('b607d9e3-a094-4e93-84f2-6e574690f2cb','9f8da996-211b-4891-a33e-517eec17eb8e'),
    ('1e758089-97cb-4715-b4a2-1c43608165cc','9f8da996-211b-4891-a33e-517eec17eb8e'),
    ('76e08585-a0f2-4957-891b-4b4727bffc8f','9f8da996-211b-4891-a33e-517eec17eb8e'),
    ('b4734c23-575f-454d-881c-34ca43f0c3a2','9f8da996-211b-4891-a33e-517eec17eb8e'),

    ('a41d891c-c743-4bf3-b2b1-66c46cbf5b23','d30a585c-4872-4e9e-880f-a33dd8267af0'),
    ('b607d9e3-a094-4e93-84f2-6e574690f2cb','d30a585c-4872-4e9e-880f-a33dd8267af0'),
    ('1e758089-97cb-4715-b4a2-1c43608165cc','d30a585c-4872-4e9e-880f-a33dd8267af0'),
    ('76e08585-a0f2-4957-891b-4b4727bffc8f','d30a585c-4872-4e9e-880f-a33dd8267af0'),
    ('b4734c23-575f-454d-881c-34ca43f0c3a2','d30a585c-4872-4e9e-880f-a33dd8267af0'),

    ('22ca63cf-658a-4a45-ae69-f12105e7565d','5fe18fa3-cd91-45c7-8e22-4a1cc39d1837'),
    ('b607d9e3-a094-4e93-84f2-6e574690f2cb','5fe18fa3-cd91-45c7-8e22-4a1cc39d1837'),
    ('1e758089-97cb-4715-b4a2-1c43608165cc','5fe18fa3-cd91-45c7-8e22-4a1cc39d1837'),
    ('76e08585-a0f2-4957-891b-4b4727bffc8f','5fe18fa3-cd91-45c7-8e22-4a1cc39d1837'),
    ('b4734c23-575f-454d-881c-34ca43f0c3a2','5fe18fa3-cd91-45c7-8e22-4a1cc39d1837'),
    ('4019faad-b4ea-497c-a624-cd86b826cb4d','5fe18fa3-cd91-45c7-8e22-4a1cc39d1837'),

    ('a41d891c-c743-4bf3-b2b1-66c46cbf5b23','b9cc9bb6-c537-415d-a549-88c11c89bc32'),
    ('b607d9e3-a094-4e93-84f2-6e574690f2cb','b9cc9bb6-c537-415d-a549-88c11c89bc32'),
    ('1e758089-97cb-4715-b4a2-1c43608165cc','b9cc9bb6-c537-415d-a549-88c11c89bc32'),
    ('76e08585-a0f2-4957-891b-4b4727bffc8f','b9cc9bb6-c537-415d-a549-88c11c89bc32'),
    ('b4734c23-575f-454d-881c-34ca43f0c3a2','b9cc9bb6-c537-415d-a549-88c11c89bc32'),

    ('a41d891c-c743-4bf3-b2b1-66c46cbf5b23','0dd52864-a8a4-4d29-be02-09d4297d1e93'),
    ('b607d9e3-a094-4e93-84f2-6e574690f2cb','0dd52864-a8a4-4d29-be02-09d4297d1e93'),
    ('1e758089-97cb-4715-b4a2-1c43608165cc','0dd52864-a8a4-4d29-be02-09d4297d1e93'),
    ('76e08585-a0f2-4957-891b-4b4727bffc8f','0dd52864-a8a4-4d29-be02-09d4297d1e93'),
    ('b4734c23-575f-454d-881c-34ca43f0c3a2','0dd52864-a8a4-4d29-be02-09d4297d1e93')


SELECT
    email,
    "hashedPassword"
FROM users
WHERE email = 'dbmanager@example.com';



INSERT INTO users("user_id",
                  "fullName",
                  "email",
                  "hashedPassword",
                  "refUID",
                  "reporting_to")
VALUES (gen_random_uuid(),'User 1', 'user1@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', gen_random_uuid(),'c9506ced-0ed1-4a50-b2e5-ae37983196a5');

INSERT INTO users("user_id",
                  "fullName",
                  "email",
                  "hashedPassword",
                  "refUID",
                  "reporting_to")
VALUES (gen_random_uuid(),'User 2', 'user2@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', gen_random_uuid(),'c9506ced-0ed1-4a50-b2e5-ae37983196a5');