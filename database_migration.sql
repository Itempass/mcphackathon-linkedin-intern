-- Migration script to update messages table with composite primary key
-- This fixes the issue where multiple users can have the same message IDs

-- Step 1: Drop the existing primary key constraint
ALTER TABLE messages DROP PRIMARY KEY;

-- Step 2: Add the new composite primary key
ALTER TABLE messages ADD PRIMARY KEY (id, user_id);

-- Verify the change
SHOW CREATE TABLE messages; 