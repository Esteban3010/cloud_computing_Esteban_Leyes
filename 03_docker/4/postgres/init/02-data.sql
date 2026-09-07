INSERT INTO academia.students (name, email) VALUES
('Ana', 'ana@example.com'),
('Luis', 'luis@example.com'),
('Marta', 'marta@example.com');

INSERT INTO academia.courses (name, credits) VALUES
('Cloud Computing', 3),
('Internet of Things', 4);


INSERT INTO academia.teachers (name, email) VALUES
('Carlos', 'carlos@example.com'),
('Laura', 'laura@example.com');

INSERT INTO academia.enrollments (student_id, course_id) VALUES
(1, 1),
(2, 1),
(3, 2);
