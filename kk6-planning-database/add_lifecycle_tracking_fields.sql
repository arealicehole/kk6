-- Add lifecycle tracking fields to planning_items table
-- For temporal evolution tracking of planning items across conversations

-- Add the new lifecycle tracking columns
ALTER TABLE planning_items ADD COLUMN IF NOT EXISTS first_mentioned_date TIMESTAMP;
ALTER TABLE planning_items ADD COLUMN IF NOT EXISTS last_updated_conversation_id INTEGER REFERENCES sources(id);
ALTER TABLE planning_items ADD COLUMN IF NOT EXISTS status_history JSONB DEFAULT '[]'::jsonb;

-- Add comments to document the fields
COMMENT ON COLUMN planning_items.first_mentioned_date IS 'Timestamp when this planning concept was first mentioned in any conversation';
COMMENT ON COLUMN planning_items.last_updated_conversation_id IS 'Source ID of the most recent conversation that updated this item';
COMMENT ON COLUMN planning_items.status_history IS 'Array of status change events: [{"status": "pending", "timestamp": "...", "conversation_id": 123, "notes": "..."}]';

-- Create index for efficient querying by last update
CREATE INDEX IF NOT EXISTS idx_planning_items_last_updated ON planning_items(last_updated_conversation_id);
CREATE INDEX IF NOT EXISTS idx_planning_items_first_mentioned ON planning_items(first_mentioned_date);

-- Create a function to automatically update lifecycle tracking when items are modified
CREATE OR REPLACE FUNCTION update_planning_item_lifecycle()
RETURNS TRIGGER AS $$
BEGIN
    -- Set first_mentioned_date if it's not already set
    IF NEW.first_mentioned_date IS NULL THEN
        NEW.first_mentioned_date = COALESCE(OLD.first_mentioned_date, NOW());
    END IF;
    
    -- Update last_updated_conversation_id if source_id changed
    IF OLD IS NULL OR NEW.source_id != OLD.source_id THEN
        NEW.last_updated_conversation_id = NEW.source_id;
    END IF;
    
    -- Add status change to history if status changed
    IF OLD IS NULL OR NEW.status != OLD.status THEN
        NEW.status_history = COALESCE(NEW.status_history, '[]'::jsonb) || 
            jsonb_build_array(
                jsonb_build_object(
                    'status', NEW.status,
                    'timestamp', NOW(),
                    'conversation_id', NEW.source_id,
                    'previous_status', COALESCE(OLD.status, 'new'),
                    'notes', 'Status updated'
                )
            );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically maintain lifecycle tracking
DROP TRIGGER IF EXISTS planning_item_lifecycle_trigger ON planning_items;
CREATE TRIGGER planning_item_lifecycle_trigger
    BEFORE INSERT OR UPDATE ON planning_items
    FOR EACH ROW
    EXECUTE FUNCTION update_planning_item_lifecycle();

-- Backfill existing data with initial lifecycle values
UPDATE planning_items SET 
    first_mentioned_date = COALESCE(first_mentioned_date, created_at),
    last_updated_conversation_id = COALESCE(last_updated_conversation_id, source_id),
    status_history = COALESCE(status_history, 
        jsonb_build_array(
            jsonb_build_object(
                'status', status,
                'timestamp', created_at,
                'conversation_id', source_id,
                'previous_status', 'new',
                'notes', 'Initial creation'
            )
        )
    )
WHERE first_mentioned_date IS NULL 
   OR last_updated_conversation_id IS NULL 
   OR status_history IS NULL
   OR jsonb_array_length(status_history) = 0;