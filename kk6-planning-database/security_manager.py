#!/usr/bin/env python3
"""
KK6 Enhanced Security Manager - Phase 1.2 Implementation
Provides security-by-design with least-privilege database access, prompt injection protection,
and comprehensive audit logging.
"""

import re
import json
import hashlib
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from pathlib import Path

import asyncpg
from pydantic import BaseModel, Field

# Configure security logging
security_logger = logging.getLogger("kk6.security")
security_logger.setLevel(logging.INFO)

# Security event types
class SecurityEventType(str, Enum):
    PROMPT_INJECTION_DETECTED = "prompt_injection_detected"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_QUERY = "suspicious_query"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DATA_EXFILTRATION_ATTEMPT = "data_exfiltration_attempt"

class SecurityLevel(str, Enum):
    READ_ONLY = "read_only"
    LIMITED_WRITE = "limited_write"
    ADMIN = "admin"

class SecurityAuditEvent(BaseModel):
    """Security audit event model"""
    event_id: str = Field(default_factory=lambda: f"sec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now()) % 10000:04d}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: SecurityEventType
    severity: str = Field(default="medium")  # low, medium, high, critical
    source_ip: Optional[str] = None
    user_context: Optional[str] = None
    query_content: Optional[str] = None
    detection_method: str
    risk_score: float = Field(default=0.5)
    additional_data: Dict[str, Any] = Field(default_factory=dict)

class DatabaseRole:
    """Database role configuration for least-privilege access"""
    
    def __init__(self, role_name: str, permissions: Set[str], tables: Set[str]):
        self.role_name = role_name
        self.permissions = permissions
        self.tables = tables
        
    @classmethod
    def read_only_role(cls):
        return cls(
            role_name="kk6_readonly",
            permissions={"SELECT"},
            tables={"chunks", "extraction_results", "sessions", "processing_metadata"}
        )
    
    @classmethod
    def query_agent_role(cls):
        return cls(
            role_name="kk6_query_agent", 
            permissions={"SELECT", "INSERT"},
            tables={"chunks", "extraction_results", "query_logs", "sessions"}
        )
    
    @classmethod
    def pipeline_role(cls):
        return cls(
            role_name="kk6_pipeline",
            permissions={"SELECT", "INSERT", "UPDATE"},
            tables={"chunks", "extraction_results", "sessions", "processing_metadata", "approval_decisions"}
        )

class PromptInjectionDetector:
    """Advanced prompt injection detection system"""
    
    def __init__(self):
        # Common prompt injection patterns
        self.injection_patterns = [
            # Direct instruction attempts
            r'(?i)\b(ignore|forget|disregard)\s+(previous|above|all|your)\s+(instructions?|prompts?|rules?)',
            r'(?i)\b(act\s+as|pretend\s+to\s+be|roleplay\s+as)\s+(?!.*planning)',
            r'(?i)\b(system|admin|root|sudo)\s*:',
            r'(?i)\b(execute|run|eval)\s*\(',
            
            # SQL injection attempts  
            r'(?i)\b(union\s+select|drop\s+table|delete\s+from|truncate\s+table)',
            r'(?i)(\'\s*;\s*--)|(\'\s*or\s+1\s*=\s*1)',
            r'(?i)\b(exec|execute|sp_|xp_)\s*\(',
            
            # System command attempts
            r'(?i)\b(rm\s+-rf|del\s+/|format\s+c:)',
            r'(?i)\b(wget|curl|powershell|cmd\.exe)',
            r'(?i)(__import__|eval|exec)\s*\(',
            
            # Data exfiltration attempts
            r'(?i)\b(show\s+all|dump\s+database|export\s+all)',
            r'(?i)\b(password|secret|token|key)\s*[:=]\s*[\'"]',
            
            # Jailbreaking attempts
            r'(?i)\b(jailbreak|DAN|do\s+anything\s+now)',
            r'(?i)developer\s+mode|debug\s+mode',
            
            # LLM-specific bypasses
            r'(?i)certainly[,!]?\s+(here|i)\s+(can|will)',
            r'(?i)as\s+an?\s+ai\s+(language\s+)?model'
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern) for pattern in self.injection_patterns]
        
        # Keywords that increase suspicion
        self.suspicious_keywords = {
            'admin', 'root', 'password', 'secret', 'token', 'bypass', 'override',
            'execute', 'system', 'command', 'shell', 'eval', 'import', 'delete',
            'drop', 'truncate', 'union', 'inject', 'hack', 'exploit'
        }
    
    def analyze_prompt(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Analyze text for prompt injection attempts.
        
        Returns:
            (is_malicious, risk_score, detected_patterns)
        """
        if not text or len(text.strip()) == 0:
            return False, 0.0, []
        
        text_lower = text.lower()
        detected_patterns = []
        risk_score = 0.0
        
        # Check against injection patterns
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text)
            if matches:
                detected_patterns.append(f"Pattern_{i+1}: {self.injection_patterns[i][:50]}...")
                risk_score += 0.3  # Each pattern match increases risk
        
        # Check for suspicious keyword density
        words = text_lower.split()
        suspicious_count = sum(1 for word in words if word in self.suspicious_keywords)
        if suspicious_count > 0:
            keyword_density = suspicious_count / len(words)
            if keyword_density > 0.1:  # More than 10% suspicious keywords
                detected_patterns.append(f"High_suspicious_keyword_density: {keyword_density:.2f}")
                risk_score += keyword_density * 0.5
        
        # Check for excessive special characters (potential encoding attacks)
        special_char_ratio = sum(1 for char in text if not char.isalnum() and not char.isspace()) / len(text)
        if special_char_ratio > 0.3:
            detected_patterns.append(f"High_special_character_ratio: {special_char_ratio:.2f}")
            risk_score += 0.2
        
        # Check for extremely long inputs (potential DoS)
        if len(text) > 10000:
            detected_patterns.append(f"Excessive_length: {len(text)} characters")
            risk_score += 0.3
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        is_malicious = risk_score > 0.5 or len(detected_patterns) >= 2
        
        return is_malicious, risk_score, detected_patterns

class SecurityManager:
    """Main security manager for KK6 system"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.prompt_detector = PromptInjectionDetector()
        self.audit_events: List[SecurityAuditEvent] = []
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Connection pools for different security levels
        self.pools: Dict[SecurityLevel, Optional[asyncpg.Pool]] = {
            SecurityLevel.READ_ONLY: None,
            SecurityLevel.LIMITED_WRITE: None,
            SecurityLevel.ADMIN: None
        }
    
    async def initialize(self):
        """Initialize security manager with database roles"""
        security_logger.info("Initializing KK6 Security Manager")
        
        # Create security audit table if not exists
        await self._ensure_audit_table()
        
        # Initialize connection pools (in production, use separate role credentials)
        try:
            # For demo, using same credentials but would be different roles in production
            self.pools[SecurityLevel.READ_ONLY] = await asyncpg.create_pool(
                self.database_url, min_size=2, max_size=5
            )
            self.pools[SecurityLevel.LIMITED_WRITE] = await asyncpg.create_pool(
                self.database_url, min_size=2, max_size=5  
            )
            self.pools[SecurityLevel.ADMIN] = await asyncpg.create_pool(
                self.database_url, min_size=1, max_size=3
            )
            security_logger.info("Database connection pools initialized")
        except Exception as e:
            security_logger.error(f"Failed to initialize database pools: {e}")
            raise
    
    async def _ensure_audit_table(self):
        """Ensure security audit table exists"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS security_audit_log (
            event_id TEXT PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            source_ip TEXT,
            user_context TEXT,
            query_content TEXT,
            detection_method TEXT NOT NULL,
            risk_score FLOAT NOT NULL,
            additional_data JSONB
        );
        
        CREATE INDEX IF NOT EXISTS idx_security_audit_timestamp ON security_audit_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_security_audit_type ON security_audit_log(event_type);
        CREATE INDEX IF NOT EXISTS idx_security_audit_severity ON security_audit_log(severity);
        """
        
        try:
            # Use admin pool for table creation
            if self.pools[SecurityLevel.ADMIN]:
                async with self.pools[SecurityLevel.ADMIN].acquire() as conn:
                    await conn.execute(create_table_sql)
            else:
                # Fallback during initialization
                conn = await asyncpg.connect(self.database_url)
                try:
                    await conn.execute(create_table_sql)
                finally:
                    await conn.close()
        except Exception as e:
            security_logger.error(f"Failed to create audit table: {e}")
    
    async def validate_query(self, query: str, context: Dict[str, Any] = None) -> Tuple[bool, Optional[SecurityAuditEvent]]:
        """
        Validate a query for security issues.
        
        Returns:
            (is_safe, audit_event_if_unsafe)
        """
        if not query:
            return True, None
        
        # Check for prompt injection
        is_malicious, risk_score, patterns = self.prompt_detector.analyze_prompt(query)
        
        if is_malicious:
            # Create security audit event
            audit_event = SecurityAuditEvent(
                event_type=SecurityEventType.PROMPT_INJECTION_DETECTED,
                severity="high" if risk_score > 0.8 else "medium",
                source_ip=context.get("source_ip") if context else None,
                user_context=context.get("user_context") if context else None,
                query_content=query[:500],  # Truncate for storage
                detection_method="pattern_analysis",
                risk_score=risk_score,
                additional_data={
                    "detected_patterns": patterns,
                    "query_length": len(query)
                }
            )
            
            # Log the event
            await self._log_security_event(audit_event)
            
            security_logger.warning(f"Prompt injection detected: risk_score={risk_score:.2f}, patterns={len(patterns)}")
            return False, audit_event
        
        return True, None
    
    async def get_secure_connection(self, security_level: SecurityLevel) -> asyncpg.Connection:
        """Get a database connection with appropriate security level"""
        pool = self.pools.get(security_level)
        if not pool:
            raise RuntimeError(f"No connection pool available for security level: {security_level}")
        
        return await pool.acquire()
    
    async def _log_security_event(self, event: SecurityAuditEvent):
        """Log security event to audit table"""
        try:
            pool = self.pools.get(SecurityLevel.ADMIN)
            if not pool:
                return
                
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO security_audit_log 
                    (event_id, timestamp, event_type, severity, source_ip, user_context, 
                     query_content, detection_method, risk_score, additional_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                event.event_id, event.timestamp, event.event_type.value, event.severity,
                event.source_ip, event.user_context, event.query_content, 
                event.detection_method, event.risk_score, json.dumps(event.additional_data)
                )
                
            # Also keep in memory for quick access
            self.audit_events.append(event)
            
            # Limit memory storage to last 1000 events
            if len(self.audit_events) > 1000:
                self.audit_events = self.audit_events[-1000:]
                
        except Exception as e:
            security_logger.error(f"Failed to log security event: {e}")
    
    async def check_rate_limit(self, identifier: str, max_requests: int = 100, window_minutes: int = 5) -> bool:
        """Check if identifier has exceeded rate limit"""
        now = datetime.now(timezone.utc)
        window_start = now.replace(minute=now.minute - (now.minute % window_minutes), second=0, microsecond=0)
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Clean old requests outside the window
        self.rate_limits[identifier] = [
            req_time for req_time in self.rate_limits[identifier] 
            if req_time >= window_start
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[identifier]) >= max_requests:
            # Log rate limit event
            audit_event = SecurityAuditEvent(
                event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                severity="medium",
                user_context=identifier,
                detection_method="rate_limiting",
                risk_score=0.6,
                additional_data={
                    "requests_in_window": len(self.rate_limits[identifier]),
                    "max_allowed": max_requests,
                    "window_minutes": window_minutes
                }
            )
            await self._log_security_event(audit_event)
            return False
        
        # Record this request
        self.rate_limits[identifier].append(now)
        return True
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and statistics"""
        try:
            pool = self.pools.get(SecurityLevel.READ_ONLY)
            if not pool:
                return {"error": "No read pool available"}
            
            async with pool.acquire() as conn:
                # Get recent security events
                recent_events = await conn.fetch("""
                    SELECT event_type, severity, COUNT(*) as count
                    FROM security_audit_log 
                    WHERE timestamp >= NOW() - INTERVAL '24 hours'
                    GROUP BY event_type, severity
                    ORDER BY count DESC
                """)
                
                # Get risk score distribution
                risk_distribution = await conn.fetch("""
                    SELECT 
                        CASE 
                            WHEN risk_score < 0.3 THEN 'low'
                            WHEN risk_score < 0.7 THEN 'medium'
                            ELSE 'high'
                        END as risk_level,
                        COUNT(*) as count
                    FROM security_audit_log
                    WHERE timestamp >= NOW() - INTERVAL '24 hours'
                    GROUP BY 1
                """)
                
                return {
                    "recent_events": [dict(row) for row in recent_events],
                    "risk_distribution": [dict(row) for row in risk_distribution],
                    "total_events_24h": sum(row['count'] for row in recent_events),
                    "security_status": "active",
                    "pools_active": len([pool for pool in self.pools.values() if pool is not None])
                }
                
        except Exception as e:
            security_logger.error(f"Failed to get security metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        security_logger.info("Cleaning up Security Manager")
        for pool in self.pools.values():
            if pool:
                await pool.close()

# Global security manager instance
security_manager: Optional[SecurityManager] = None

async def get_security_manager() -> SecurityManager:
    """Get global security manager instance"""
    global security_manager
    if security_manager is None:
        raise RuntimeError("Security manager not initialized")
    return security_manager

async def initialize_security(database_url: str) -> SecurityManager:
    """Initialize global security manager"""
    global security_manager
    security_manager = SecurityManager(database_url)
    await security_manager.initialize()
    return security_manager