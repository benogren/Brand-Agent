-- Migration 002: Create events table

CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    author VARCHAR(50) NOT NULL CHECK (author IN ('user', 'agent')),
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL,
    metadata JSONB,
    CONSTRAINT fk_events_session
        FOREIGN KEY (session_id)
        REFERENCES sessions(session_id)
        ON DELETE CASCADE
);
