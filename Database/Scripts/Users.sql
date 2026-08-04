INSERT INTO roles ("role_id", "roleName", "createdAt") VALUES
(1, 'Super Admin', '2026-07-30 10:44:29.202403'),
(2, 'BD-Executive', '2026-07-30 10:44:32.940045'),
(3, 'Team Lead', '2026-07-30 11:10:51.95888'),
(4, 'Manager', '2026-07-31 05:18:35.978669'),
(5, 'User', '2026-07-31 05:19:40.055191');

INSERT INTO menus ("menu_id", "name", "description", "createdAt") VALUES
(1, 'AI Discovery', 'AI Descovery screen', '2026-07-30 11:00:36.420747'),
(2, 'KPI Dashboard', 'Menu items responsible to show all the kpi', '2026-07-30 11:00:36.420747'),
(3, 'Opportunity Pipeline', 'Opportunity pipelines', '2026-07-30 11:00:36.420747'),
(4, 'User Profiles', 'User Profile details ', '2026-07-30 11:00:36.420747'),
(5, 'Projects', 'List of unique projects', '2026-07-30 11:00:36.420747'),
(6, 'Team Hierarchy', 'Menu item responsible to see Team Hierarchy', '2026-07-30 11:00:36.420747'),
(7, 'Dashboard', 'Menu Item for dashboard Screen', '2026-07-30 11:00:36.420747'),
(8, 'Settings', 'Menu Item for Settings', '2026-07-30 11:00:36.420747');


INSERT INTO users ("user_id", "fullName", "email", "hashedPassword", "refUID", "passwordResetAt", "createdAt", "role_id", "reporting_to", "specialization") VALUES
('a9c9a698-5a06-442f-a725-f308a4a548c7', 'Super Admin', 'admin@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF001', NULL, '2026-07-30 10:37:35.358398', 1, NULL, NULL),
('a52b5432-e5a1-4cb2-bb54-972b80f59cf2', 'BD-Executive', 'bdexecutive@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF002', NULL, '2026-07-30 10:41:17.307275', 2, 'a9c9a698-5a06-442f-a725-f308a4a548c7', NULL),
('231a8e9a-4f30-41aa-b7d2-a2cbf1f05bd0', 'Monika', 'monika@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF003', NULL, '2026-07-31 05:33:29.539994', 4, 'a9c9a698-5a06-442f-a725-f308a4a548c7', 'Project Management'),
('e0b0c1e1-8d4d-4350-9823-fb74a311fa9b', 'Abdul', 'abdul@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF004', NULL, '2026-07-31 05:35:22.189162', 4, 'a9c9a698-5a06-442f-a725-f308a4a548c7', 'Project Management'),
('8cc08100-220c-4feb-9991-3d0b584df2c0', 'Shubhajit Kotal', 'shubhajitkotal@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF005', NULL, '2026-07-31 05:38:12.654747', 3, '231a8e9a-4f30-41aa-b7d2-a2cbf1f05bd0', 'AI Engineer'),
('53f9a2cb-870c-4857-a659-ae02a148f9aa', 'Vasanth Sethu', 'vasanthsetu@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF006', NULL, '2026-07-31 05:40:32.313952', 5, '8cc08100-220c-4feb-9991-3d0b584df2c0', 'AI Developer'),
('5a116636-7388-460d-b1bf-132b11217353', 'Mridul Guptha', 'mridulguptha@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF007', NULL, '2026-07-31 05:40:39.090831', 5, '8cc08100-220c-4feb-9991-3d0b584df2c0', 'AI Developer'),
('d910c917-f57b-45e9-982a-7c61d8d647cc', 'Harshan', 'harshan@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF008', NULL, '2026-07-31 05:45:11.049114', 5, 'e0b0c1e1-8d4d-4350-9823-fb74a311fa9b', 'UI/UX Developer'),
('d1dda25f-457b-4621-973f-2274526be4e6', 'Nandakishor S R', 'nandakishor@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF009', NULL, '2026-07-31 05:45:20.044416', 3, 'e0b0c1e1-8d4d-4350-9823-fb74a311fa9b', 'Backend Developer'),
('f0543711-e595-4617-9c4d-0bec4729fbb5', 'Pragadesh', 'pragadesh@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF010', NULL, '2026-07-31 05:47:13.119291', 5, 'd1dda25f-457b-4621-973f-2274526be4e6', 'Python Developer'),
('9fd298c7-126a-4bc0-a90e-383949972b57', 'Ranjith', 'ranjith@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF011', NULL, '2026-07-31 05:47:19.049515', 5, 'd1dda25f-457b-4621-973f-2274526be4e6', 'Python Developer'),
('2fe5d3d7-49fa-4633-ae4e-1e0ca07bd0f4', 'User 2', 'user2@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF012', NULL, '2026-07-31 04:13:33.085051', 5, 'a52b5432-e5a1-4cb2-bb54-972b80f59cf2', NULL),
('7ac72bd6-59cf-42c4-a374-63dccf022393', 'User 1', 'user1@example.com', '$argon2id$v=19$m=65536,t=3,p=4$tRYCIGQs5byX0tq79x7DWA$jR8u1xzeXVgn/ny0Ms/uaXfprXGfgWwrzZIUeMND8+o', 'REF013', NULL, '2026-07-31 04:13:18.157695', 5, 'a52b5432-e5a1-4cb2-bb54-972b80f59cf2', NULL);


INSERT INTO menu_roles ("menu_id", "role_id", "assignedAt") VALUES
(1, 2, '2026-07-30 11:22:26.814051'),
(2, 2, '2026-07-30 11:22:26.814051'),
(3, 2, '2026-07-30 11:22:26.814051'),
(4, 2, '2026-07-30 11:22:26.814051'),
(5, 2, '2026-07-30 11:22:26.814051'),
(6, 2, '2026-07-30 11:22:26.814051'),
(2, 1, '2026-07-30 11:22:26.814051'),
(3, 1, '2026-07-30 11:22:26.814051'),
(4, 1, '2026-07-30 11:22:26.814051'),
(5, 1, '2026-07-30 11:22:26.814051'),
(6, 1, '2026-07-30 11:22:26.814051'),
(8, 1, '2026-07-30 11:22:26.814051'),
(7, 3, '2026-07-30 11:22:26.814051'),
(3, 3, '2026-07-30 11:22:26.814051'),
(4, 3, '2026-07-30 11:22:26.814051'),
(5, 3, '2026-07-30 11:22:26.814051'),
(6, 3, '2026-07-30 11:22:26.814051'),
(7, 4, '2026-07-31 05:25:06.428817'),
(3, 4, '2026-07-31 05:25:06.428817'),
(4, 4, '2026-07-31 05:25:06.428817'),
(5, 4, '2026-07-31 05:25:06.428817'),
(6, 4, '2026-07-31 05:25:06.428817'),
(7, 5, '2026-07-31 05:29:23.511344'),
(3, 5, '2026-07-31 05:29:23.511344'),
(4, 5, '2026-07-31 05:29:23.511344');

INSERT INTO opportunities ("opportunityID", "title", "company", "location", "employment_type", "experience", "salary", "description", "responsibilities", "requirements", "benefits", "apply_url", "ai_job_summary", "required_proposal_questions", "createdAt", "updatedAt", "industry", "role", "duration", "level", "posted_date", "required_skills", "preferred_skills", "client_information", "company_profile", "additional_fields", "createdBy", "updatedBy") VALUES
(1, 'Web Developer - Web Development', NULL, 'Worldwide', 'Full-Time', '1-3+ years', '$6.00 - $15.00 Hourly', 
'We are looking for a talented and passionate MERN Stack Developer to join our development team. The ideal candidate will be responsible for designing, developing, testing, and maintaining scalable web applications using the MERN stack (MongoDB, Express.js, React.js, and Node.js). You will work closely with designers, developers, and stakeholders to deliver high-quality software solutions.', 
'{"Designing, developing, testing, and maintaining scalable web applications using the MERN stack.","Working closely with designers, developers, and stakeholders to deliver high-quality software solutions.","Managing multiple tasks independently.","Learning new technologies and adapting to changing requirements."}', 
'{"Bachelor''s degree in Computer Science, Software Engineering, or a related field (or equivalent practical experience).","1–3+ years of experience in MERN Stack development.","Strong problem-solving and analytical skills.","Excellent communication and teamwork abilities.","Ability to work independently and manage multiple tasks.","Willingness to learn new technologies and adapt to changing requirements."}', 
'{"Contract-to-hire opportunity"}', NULL, 
'This role is a **MERN Stack Developer** position focused on building and maintaining scalable web applications. The client is looking for a developer with 1-3 years of experience who is comfortable working across the full stack, specifically using **MongoDB**, **Express.js**, **React.js**, and **Node.js**. 

While the core requirements are standard for a MERN developer, the client highly values candidates who can demonstrate proficiency with modern tooling like **Next.js**, **TypeScript**, and **Docker**. This is a **contract-to-hire** opportunity, suggesting a potential path to long-term employment for the right candidate. Candidates should be prepared to showcase a strong portfolio or GitHub profile, as this is explicitly mentioned as a plus.', 
'{}', '2026-07-31 09:27:16.561454', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'a9c9a698-5a06-442f-a725-f308a4a548c7', 'a9c9a698-5a06-442f-a725-f308a4a548c7'),

(2, 'Web Developer', NULL, 'Worldwide', 'Full-Time', '1–3+ years', '$6.00 - $15.00 Hourly', 
'We are looking for a talented and passionate MERN Stack Developer to join our development team. The ideal candidate will be responsible for designing, developing, testing, and maintaining scalable web applications using the MERN stack (MongoDB, Express.js, React.js, and Node.js). You will work closely with designers, developers, and stakeholders to deliver high-quality software solutions.', 
'{"Designing, developing, testing, and maintaining scalable web applications using the MERN stack.","Working closely with designers, developers, and stakeholders to deliver high-quality software solutions."}', 
'{"Bachelor''s degree in Computer Science, Software Engineering, or a related field (or equivalent practical experience).","1–3+ years of experience in MERN Stack development.","A strong portfolio or GitHub profile showcasing relevant projects is a plus.","Strong problem-solving and analytical skills.","Excellent communication and teamwork abilities.","Ability to work independently and manage multiple tasks.","Willingness to learn new technologies and adapt to changing requirements."}', 
'{"Contract-to-hire opportunity"}', NULL, 
'This is an entry-level **MERN Stack Developer** role focused on building and maintaining scalable web applications. The client is looking for a developer with 1-3 years of experience who is comfortable working across the full stack, specifically using **MongoDB**, **Express.js**, **React.js**, and **Node.js**. 

While the core requirements are standard, the client highly values candidates who can demonstrate proficiency with modern tooling like **Next.js**, **TypeScript**, and **Docker**. This is a **contract-to-hire** position, offering a potential path to full-time employment. Candidates should be prepared to showcase a strong portfolio or GitHub profile, as this is explicitly mentioned as a differentiator. Note that this is a budget-conscious project, so clear communication regarding your ability to deliver high-quality code within the specified hourly range is essential.', 
'{}', '2026-07-31 09:35:25.628301', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'a9c9a698-5a06-442f-a725-f308a4a548c7', 'a9c9a698-5a06-442f-a725-f308a4a548c7'),

(3, 'Web Developer - Web Development', NULL, 'Worldwide', 'Full-Time', '1–3+ years', '$6.00 - $15.00 Hourly', 
'We are looking for a talented and passionate MERN Stack Developer to join our development team. The ideal candidate will be responsible for designing, developing, testing, and maintaining scalable web applications using the MERN stack (MongoDB, Express.js, React.js, and Node.js). You will work closely with designers, developers, and stakeholders to deliver high-quality software solutions.', 
'{"Designing, developing, testing, and maintaining scalable web applications using the MERN stack.","Working closely with designers, developers, and stakeholders to deliver high-quality software solutions."}', 
'{"Bachelor''s degree in Computer Science, Software Engineering, or a related field (or equivalent practical experience).","1–3+ years of experience in MERN Stack development.","A strong portfolio or GitHub profile showcasing relevant projects is a plus.","Strong problem-solving and analytical skills.","Excellent communication and teamwork abilities.","Ability to work independently and manage multiple tasks.","Willingness to learn new technologies and adapt to changing requirements."}', 
'{"Contract-to-hire opportunity"}', NULL, 
'This is a **contract-to-hire** opportunity for a **Junior-level MERN Stack Developer** looking to build a portfolio. The client is seeking someone proficient in the core **MERN stack (MongoDB, Express.js, React.js, Node.js)** to handle end-to-end web application development. While the core requirements focus on standard web development tools, the client highly values candidates with experience in **Next.js**, **TypeScript**, and cloud deployment tools like **AWS** or **Docker**.

Candidates should be prepared for a fast-paced, complex project environment. The role emphasizes both technical proficiency and soft skills, specifically the ability to work independently and adapt to changing requirements. Given the hourly rate range, this role is best suited for developers early in their career who are eager to gain experience and potentially transition into a long-term, full-time position.', 
'{}', '2026-07-31 09:30:05.021206', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'a9c9a698-5a06-442f-a725-f308a4a548c7', 'a9c9a698-5a06-442f-a725-f308a4a548c7'),

(4, 'Web Developer - Web Development', NULL, 'Worldwide', 'Full-Time', '1–3+ years', '$6.00 - $15.00 Hourly', 
'We are looking for a talented and passionate MERN Stack Developer to join our development team. The ideal candidate will be responsible for designing, developing, testing, and maintaining scalable web applications using the MERN stack (MongoDB, Express.js, React.js, and Node.js). You will work closely with designers, developers, and stakeholders to deliver high-quality software solutions.', 
'{"Designing, developing, testing, and maintaining scalable web applications using the MERN stack.","Working closely with designers, developers, and stakeholders to deliver high-quality software solutions."}', 
'{"Bachelor''s degree in Computer Science, Software Engineering, or a related field (or equivalent practical experience).","1–3+ years of experience in MERN Stack development.","A strong portfolio or GitHub profile showcasing relevant projects is a plus.","Strong problem-solving and analytical skills.","Excellent communication and teamwork abilities.","Ability to work independently and manage multiple tasks.","Willingness to learn new technologies and adapt to changing requirements."}', 
'{"Contract-to-hire opportunity"}', NULL, 
'This is a **contract-to-hire** opportunity for a **MERN Stack Developer** looking to build scalable web applications. The client is seeking a developer with **1-3 years of experience** who is comfortable working across the full stack, specifically with **MongoDB, Express.js, React.js, and Node.js**. 

While the core requirements focus on standard web development tools like **JavaScript (ES6+)**, **HTML5/CSS3**, and **Git**, the client highly values candidates who can bring extra expertise in **Next.js**, **TypeScript**, and cloud deployment tools like **AWS** or **Docker**. This role is ideal for a developer who is eager to learn and adapt, as the project is described as complex. Note that the client is looking for competitive rates, so demonstrating a strong portfolio or **GitHub** profile will be critical to standing out.', 
'{}', '2026-07-31 09:43:52.582271', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'a9c9a698-5a06-442f-a725-f308a4a548c7', 'a9c9a698-5a06-442f-a725-f308a4a548c7'),

(5, 'Web Developer - Web Development', NULL, 'Worldwide', 'Full-Time', '1-3+ years', '$6.00 - $15.00 Hourly', 
'We are looking for a talented and passionate MERN Stack Developer to join our development team. The ideal candidate will be responsible for designing, developing, testing, and maintaining scalable web applications using the MERN stack (MongoDB, Express.js, React.js, and Node.js). You will work closely with designers, developers, and stakeholders to deliver high-quality software solutions.', 
'{"Designing, developing, testing, and maintaining scalable web applications using the MERN stack.","Working closely with designers, developers, and stakeholders to deliver high-quality software solutions."}', 
'{"Bachelor''s degree in Computer Science, Software Engineering, or a related field (or equivalent practical experience).","1–3+ years of experience in MERN Stack development.","A strong portfolio or GitHub profile showcasing relevant projects is a plus.","Strong problem-solving and analytical skills.","Excellent communication and teamwork abilities.","Ability to work independently and manage multiple tasks.","Willingness to learn new technologies and adapt to changing requirements."}', 
'{"Contract-to-hire opportunity"}', NULL, 
'This is an **entry-level** opportunity for a **MERN Stack Developer** looking to build a portfolio and potentially transition into a long-term, full-time role. The client is seeking a developer proficient in the core **MERN stack** (MongoDB, Express.js, React.js, Node.js) to handle end-to-end web application development. While the core requirements focus on standard web development tools, the client highly values candidates who have experience with modern tooling like **Next.js**, **TypeScript**, and **Docker**. Success in this role requires a strong grasp of **database architecture** and the ability to integrate third-party APIs. Candidates should be prepared to work independently and demonstrate a proactive attitude toward learning new technologies.', 
'{}', '2026-07-31 09:31:26.636066', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'a9c9a698-5a06-442f-a725-f308a4a548c7', 'a9c9a698-5a06-442f-a725-f308a4a548c7');

INSERT INTO permissions ("display_name","permission_key","description") VALUES 
('Create','create','Create Access'),
('Read','read','Read Access'),
('Update','update','Update Access'),
('Delete','delete','Delete Access'),
('assign','assign','Assign Access'),
('approve','approve','Approve Access'),
('export','export','Export Access'),
('import','import','Import Access');

INSERT INTO features("feature_key","display_name","description") VALUES
('ai_discovery', 'AI Discovery', 'Menu Item - AI Descovery screen'),
('kpi_dashboard', 'KPI Dashboard', 'Menu Item - KPI Dashboard'),
('opportunity_pipeline', 'Opportunity Pipeline', 'Menu Item - Opportunity pipelines'),
('user_profiles', 'User Profiles', 'Menu Item - User Profile'),
('projects', 'Projects', 'Menu Item - Projects'),
('team_hierarchy', 'Team Hierarchy', 'Menu Item - Team Hierarchy'),
('dashboard', 'Dashboard', 'Menu Item - Dashboard'),
('settings', 'Settings', 'Menu Item - Settings');


INSERT INTO features("parent_feature_id","feature_key","display_name","description") VALUES
(1,"overview_and_analysis","Overview & Analysis","Tabs inside Opportunity pipeline screen Overview of the scraped data."),
(1,"sales_enablement","Sales Enablement","Tabs inside Opportunity pipeline screen showing Sales Enablement details"),
(1,"resource_match","Resource Match","Tabs inside Opportunity pipeline screen showing Resource Match details"),
(1,"technical_preperation","Technical Preperation","Tabs inside Opportunity pipeline screen showing Technical Preparation details")


INSERT INTO "rolePermissions" ("feature_id","role_id","permission_id")
VALUES
(1,2,2),
(2,2,2),
(3,2,2),
(4,2,2),
(5,2,2),
(6,2,2),
(2,1,2),
(3,1,2),
(4,1,2),
(5,1,2),
(6,1,2),
(8,1,2),
(7,3,2),
(3,3,2),
(4,3,2),
(5,3,2),
(6,3,2),
(7,4,2),
(3,4,2),
(4,4,2),
(5,4,2),
(6,4,2),
(7,5,2),
(3,5,2),
(4,5,2);


INSERT INTO opportunity_status (status, description, is_active) VALUES
    ('New', 'Newly scraped or created opportunity', true),
    ('Qualified', 'Opportunity has been qualified for further action', true),
    ('Shortlisted', 'Candidate has been shortlisted for this opportunity', true),
    ('Candidate Selected', 'A specific candidate has been selected', true),
    ('Interview Prepared', 'Preparation for the interview has been completed', true),
    ('Client Interview', 'Client interview stage', true),
    ('Selected', 'Successfully selected for the opportunity', true),
    ('Rejected', 'Opportunity rejected or closed', true)
ON CONFLICT (status) DO NOTHING;


INSERT INTO platforms (name, description, is_active) VALUES
    ('linkedin', 'LinkedIn Platform', true),
    ('upwork', 'Upwork Platform', true),
    ('manual', 'Manual Entry', true)
ON CONFLICT (name) DO NOTHING;