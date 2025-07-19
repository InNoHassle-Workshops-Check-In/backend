-- Initialize WorkshopsAPI Database
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create additional databases if needed
-- CREATE DATABASE workshops_test_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE workshops_db TO workshops_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO workshops_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO workshops_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO workshops_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO workshops_user; 