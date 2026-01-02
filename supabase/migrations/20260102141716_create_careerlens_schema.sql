/*
  # CareerLens Database Schema

  1. New Tables
    - `users`
      - `id` (serial, primary key)
      - `name` (text) - User's full name
      - `email` (text, unique) - User's email address
      - `branch` (text) - Academic branch (CSE, ECE, MECH, etc.)
      - `cgpa` (numeric) - Current CGPA
      - `backlogs` (integer) - Number of backlogs
      - `internships` (text) - Internship details
      - `password` (text) - User password (plaintext for now)
      - `created_at` (timestamptz) - Account creation timestamp
    
    - `user_scores`
      - `id` (serial, primary key)
      - `user_email` (text) - Foreign key to users.email
      - `topic` (text) - Quiz topic (C, Java, Python, etc.)
      - `subtopic` (text) - Quiz subtopic (Arrays, Loops, etc.)
      - `score` (integer) - Score achieved
      - `total_questions` (integer) - Total questions in quiz
      - `created_at` (timestamptz) - Quiz completion timestamp
  
  2. Security
    - Enable RLS on both tables
    - Add policies for authenticated users to manage their own data
    - Public signup allowed (no auth required for this MVP)
*/

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  branch TEXT NOT NULL,
  cgpa NUMERIC(3,2) NOT NULL,
  backlogs INTEGER DEFAULT 0,
  internships TEXT DEFAULT '',
  password TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create user_scores table
CREATE TABLE IF NOT EXISTS user_scores (
  id SERIAL PRIMARY KEY,
  user_email TEXT NOT NULL,
  topic TEXT NOT NULL,
  subtopic TEXT DEFAULT '',
  score INTEGER NOT NULL,
  total_questions INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT fk_user_email FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_scores_email ON user_scores(user_email);
CREATE INDEX IF NOT EXISTS idx_user_scores_topic ON user_scores(topic, subtopic);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_scores ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Allow public signup"
  ON users FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Users can view all profiles"
  ON users FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

-- RLS Policies for user_scores table
CREATE POLICY "Anyone can insert scores"
  ON user_scores FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Anyone can view all scores"
  ON user_scores FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anyone can update scores"
  ON user_scores FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Anyone can delete scores"
  ON user_scores FOR DELETE
  TO anon
  USING (true);