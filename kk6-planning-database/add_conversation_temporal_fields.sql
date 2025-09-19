-- Add conversation temporal fields to sources table
-- For proper temporal hierarchy and chronological ordering of conversations

-- Add the new conversation temporal columns
ALTER TABLE sources ADD COLUMN IF NOT EXISTS conversation_date TIMESTAMP;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS conversation_sequence INTEGER;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS participants TEXT[];
ALTER TABLE sources ADD COLUMN IF NOT EXISTS communication_method VARCHAR(50);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS conversation_duration_minutes INTEGER;

-- Add comments to document the fields
COMMENT ON COLUMN sources.conversation_date IS 'Actual date/time when the conversation took place (extracted from transcript filename)';
COMMENT ON COLUMN sources.conversation_sequence IS 'Sequential order of conversations for chronological sorting (auto-assigned based on conversation_date)';
COMMENT ON COLUMN sources.participants IS 'Array of participant names/identifiers in the conversation';
COMMENT ON COLUMN sources.communication_method IS 'Method of communication: phone, video, in-person, text, etc.';
COMMENT ON COLUMN sources.conversation_duration_minutes IS 'Duration of conversation in minutes (if available)';

-- Create indexes for efficient temporal querying
CREATE INDEX IF NOT EXISTS idx_sources_conversation_date ON sources(conversation_date);
CREATE INDEX IF NOT EXISTS idx_sources_conversation_sequence ON sources(conversation_sequence);
CREATE INDEX IF NOT EXISTS idx_sources_participants ON sources USING GIN(participants);

-- Create a function to automatically assign conversation_sequence based on conversation_date
CREATE OR REPLACE FUNCTION update_conversation_sequence()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update sequence if conversation_date was set/changed
    IF NEW.conversation_date IS NOT NULL AND (OLD IS NULL OR NEW.conversation_date != COALESCE(OLD.conversation_date, '1900-01-01'::timestamp)) THEN
        -- Get the next sequence number based on chronological order
        WITH ordered_conversations AS (
            SELECT id, conversation_date,
                   ROW_NUMBER() OVER (ORDER BY conversation_date, id) as new_sequence
            FROM sources 
            WHERE conversation_date IS NOT NULL
               OR id = NEW.id  -- Include the current record being updated
        )
        UPDATE sources 
        SET conversation_sequence = ordered_conversations.new_sequence
        FROM ordered_conversations
        WHERE sources.id = ordered_conversations.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically maintain conversation sequence
DROP TRIGGER IF EXISTS conversation_sequence_trigger ON sources;
CREATE TRIGGER conversation_sequence_trigger
    AFTER INSERT OR UPDATE OF conversation_date ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_sequence();

-- Create a view for easy chronological conversation browsing
CREATE OR REPLACE VIEW conversations_chronological AS
SELECT 
    s.id,
    s.reference,
    s.conversation_date,
    s.conversation_sequence,
    s.participants,
    s.communication_method,
    s.conversation_duration_minutes,
    s.metadata,
    s.created_at,
    -- Count of planning items from this conversation
    COUNT(pi.id) as planning_items_count,
    -- Latest planning item activity
    MAX(pi.updated_at) as latest_planning_activity
FROM sources s
LEFT JOIN planning_items pi ON s.id = pi.source_id
WHERE s.type = 'transcript'
GROUP BY s.id, s.reference, s.conversation_date, s.conversation_sequence, 
         s.participants, s.communication_method, s.conversation_duration_minutes,
         s.metadata, s.created_at
ORDER BY s.conversation_sequence NULLS LAST, s.conversation_date NULLS LAST, s.id;

-- Create a function to get conversation context for a planning item
CREATE OR REPLACE FUNCTION get_conversation_context(item_id INTEGER)
RETURNS TABLE (
    conversation_date TIMESTAMP,
    participants TEXT[],
    communication_method VARCHAR(50),
    conversation_sequence INTEGER,
    source_reference VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.conversation_date,
        s.participants,
        s.communication_method,
        s.conversation_sequence,
        s.reference
    FROM planning_items pi
    JOIN sources s ON pi.source_id = s.id
    WHERE pi.id = item_id;
END;
$$ LANGUAGE plpgsql;