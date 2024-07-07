-- Create questions table
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_id INTEGER,
    question_image TEXT,
    answer_text TEXT,
    solution_image TEXT,
    subject TEXT,
    topic TEXT
);

-- Create user points table
CREATE TABLE IF NOT EXISTS user_points (
    username TEXT,
    user_id INTEGER PRIMARY KEY,
    doubts_solved INTEGER,
    questions_attempted INTEGER,
    questions_solved INTEGER,
    questions_skipped INTEGER,
    points REAL,
    total_time_taken TEXT
);

-- Create set counter table
CREATE TABLE IF NOT EXISTS set_counter (
    current_set_id INTEGER,
    question_count INTEGER
);

-- Initialize set counter if empty
INSERT INTO set_counter (current_set_id, question_count)
SELECT 1, 0
WHERE NOT EXISTS (SELECT 1 FROM set_counter);

-- Create trigger for set id increment
CREATE TRIGGER IF NOT EXISTS set_id_trigger
AFTER INSERT ON questions
FOR EACH ROW
BEGIN
    -- Update the set counter table
    UPDATE set_counter
    SET question_count = question_count + 1;

    -- If the count reaches 10, reset it and increment the set id
    UPDATE set_counter
    SET current_set_id = current_set_id + 1, question_count = 0
    WHERE question_count > 10;

    -- Update the new question's set id
    UPDATE questions
    SET set_id = (SELECT current_set_id FROM set_counter)
    WHERE question_id = NEW.question_id;
END;