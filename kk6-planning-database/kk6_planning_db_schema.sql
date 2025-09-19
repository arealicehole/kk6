-- KK6 Planning Database Schema
-- Separate database for Kanna Kickback 6 event planning data management

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS planning_items CASCADE;
DROP TABLE IF EXISTS sources CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS extraction_sessions CASCADE;

-- Categories table: Hierarchical structure for organizing planning items
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sources table: Track all information sources (transcripts, manual entry, screenshots, etc.)
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,           -- 'transcript', 'manual_entry', 'screenshot', 'document'
    reference VARCHAR(255) NOT NULL,     -- filename, session_id, document_name
    metadata JSONB DEFAULT '{}',         -- flexible metadata about the source
    processed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Extraction sessions: Track when data was extracted and processed
CREATE TABLE extraction_sessions (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    extraction_method VARCHAR(100),      -- 'manual', 'llm_analysis', 'ocr', 'api'
    extracted_by VARCHAR(100),           -- user/system identifier
    session_notes TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'in_progress' -- 'in_progress', 'completed', 'failed'
);

-- Planning items: Core table for all planning information
CREATE TABLE planning_items (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    item_key VARCHAR(100),               -- unique identifier within category
    title VARCHAR(255) NOT NULL,        -- human readable summary
    content TEXT,                        -- full description/details
    
    -- Multiple value types for flexibility
    value_text VARCHAR(500),             -- text values (names, descriptions)
    value_numeric DECIMAL,               -- numeric values (attendance, budget)
    value_date DATE,                     -- date values
    value_boolean BOOLEAN,               -- yes/no values
    value_json JSONB,                    -- complex structured data
    
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 10),
    priority_level INTEGER DEFAULT 3 CHECK (priority_level >= 1 AND priority_level <= 5), -- 1=low, 5=critical
    
    -- Source tracking
    source_id INTEGER REFERENCES sources(id),
    extraction_session_id INTEGER REFERENCES extraction_sessions(id),
    
    -- Versioning and status
    superseded_by INTEGER REFERENCES planning_items(id),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'superseded', 'needs_verification', 'rejected'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Tags for flexible categorization
    tags TEXT[], -- array of tag strings
    
    UNIQUE(category_id, item_key) -- prevent duplicate keys within same category
);

-- Insert base categories based on the planning skeleton
INSERT INTO categories (name, description, sort_order) VALUES
('Event Overview', 'Basic event information and overview', 1),
('Date & Time Planning', 'Timeline, scheduling, and temporal considerations', 2),
('Venue & Location', 'Venue requirements, location planning, and logistics', 3),
('Food & Catering', 'Food service, catering, and beverage planning', 4),
('Cannabis & Supplies', 'Cannabis products, supplies, and compliance', 5),
('Partners & Vendors', 'Business partnerships and vendor relationships', 6),
('Budget & Finance', 'Financial planning, revenue, and expense tracking', 7),
('Staffing & Volunteers', 'Personnel management and volunteer coordination', 8),
('Marketing & Promotion', 'Promotional activities and marketing campaigns', 9),
('Activities & Entertainment', 'Event programming and entertainment planning', 10),
('Legal & Compliance', 'Permits, regulations, and legal requirements', 11),
('Charity Component', 'Charitable activities and fundraising', 12),
('Logistics & Operations', 'Day-of-event operations and logistics', 13),
('Success Metrics', 'Performance measurement and evaluation criteria', 14),
('Risk Management', 'Risk assessment and contingency planning', 15);

-- Insert subcategories for key areas
INSERT INTO categories (name, parent_id, description, sort_order) VALUES
-- Event Overview subcategories
('Basic Information', 1, 'Core event details', 1),
('Event Type & Purpose', 1, 'Event classification and objectives', 2),

-- Date & Time Planning subcategories  
('Timeline', 2, 'Event scheduling and timeline', 1),
('Schedule Conflicts', 2, 'Potential scheduling issues', 2),

-- Venue & Location subcategories
('Venue Requirements', 3, 'Space and facility requirements', 1),
('Venue Options', 3, 'Potential venue candidates', 2),

-- Food & Catering subcategories
('Food Planning', 4, 'Menu and food service planning', 1),
('Beverage Planning', 4, 'Drink service and bar planning', 2),

-- Cannabis & Supplies subcategories
('Cannabis Products', 5, 'Product planning and inventory', 1),
('Supply Chain', 5, 'Sourcing and logistics', 2),

-- Partners & Vendors subcategories
('Confirmed Partners', 6, 'Established partnership agreements', 1),
('Potential Partners', 6, 'Prospective partnerships', 2),

-- Budget & Finance subcategories
('Revenue Streams', 7, 'Income sources and projections', 1),
('Expenses', 7, 'Cost tracking and budgeting', 2),

-- Add more subcategories as needed...
('Staffing Roles', 8, 'Key positions and responsibilities', 1),
('Volunteer Management', 8, 'Volunteer coordination and tasks', 2);

-- Create indexes for performance
CREATE INDEX idx_planning_items_category ON planning_items(category_id);
CREATE INDEX idx_planning_items_status ON planning_items(status);
CREATE INDEX idx_planning_items_source ON planning_items(source_id);
CREATE INDEX idx_planning_items_superseded ON planning_items(superseded_by);
CREATE INDEX idx_planning_items_created ON planning_items(created_at);
CREATE INDEX idx_categories_parent ON categories(parent_id);

-- Create views for easier querying
CREATE VIEW active_planning_items AS
SELECT 
    pi.*,
    c.name as category_name,
    pc.name as parent_category_name,
    s.type as source_type,
    s.reference as source_reference
FROM planning_items pi
JOIN categories c ON pi.category_id = c.id
LEFT JOIN categories pc ON c.parent_id = pc.id
LEFT JOIN sources s ON pi.source_id = s.id
WHERE pi.status = 'active';

CREATE VIEW planning_summary AS
SELECT 
    c.name as category,
    COUNT(pi.id) as total_items,
    COUNT(CASE WHEN pi.status = 'active' THEN 1 END) as active_items,
    COUNT(CASE WHEN pi.status = 'needs_verification' THEN 1 END) as needs_verification,
    AVG(pi.confidence_level) as avg_confidence
FROM categories c
LEFT JOIN planning_items pi ON c.id = pi.category_id
GROUP BY c.id, c.name, c.sort_order
ORDER BY c.sort_order;

-- Functions for data management
CREATE OR REPLACE FUNCTION update_planning_item_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_planning_items_timestamp
    BEFORE UPDATE ON planning_items
    FOR EACH ROW
    EXECUTE FUNCTION update_planning_item_timestamp();

-- Function to supersede an item with a new one
CREATE OR REPLACE FUNCTION supersede_planning_item(old_item_id INTEGER, new_item_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE planning_items 
    SET superseded_by = new_item_id, status = 'superseded', updated_at = NOW()
    WHERE id = old_item_id;
END;
$$ LANGUAGE plpgsql;

-- Sample data for testing (commented out for now)
/*
INSERT INTO sources (type, reference, metadata) VALUES
('transcript', '2025-08-07 11-54-37 transcript.txt', '{"transcript_date": "2025-08-07", "speaker": "Gilbert"}'),
('manual_entry', 'planning_session_2025_09_17', '{"entered_by": "event_coordinator", "session_type": "initial_planning"}');

INSERT INTO planning_items (category_id, item_key, title, content, value_numeric, confidence_level, source_id, status) VALUES
(1, 'expected_attendance', 'Expected Attendance', 'Approximately 200+ people expected, with minimum 100 for charity purposes', 200, 8, 1, 'active'),
(4, 'sushi_chef_needed', 'Sushi Chef Required', 'Professional sushi chef needed, deadline by December', NULL, 9, 1, 'active');
*/