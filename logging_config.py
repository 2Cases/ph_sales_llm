"""
Comprehensive logging and debugging configuration for the pharmacy chatbot.
Provides structured logging with different levels and output formats.
"""

import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Add color coding to log messages for better readability."""
    
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'ENDC': '\033[0m',      # End color
        'BOLD': '\033[1m',      # Bold
    }
    
    def format(self, record):
        if hasattr(record, 'color') and record.color:
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['ENDC']
            record.levelname = f"{color}{record.levelname}{reset}"
            record.name = f"{self.COLORS['BOLD']}{record.name}{reset}"
        
        return super().format(record)

class ConversationLogger:
    """Specialized logger for conversation tracking and debugging."""
    
    def __init__(self, name: str = "pharmacy_chatbot"):
        self.logger = logging.getLogger(name)
        self.conversation_id: Optional[str] = None
        
    def set_conversation_id(self, conversation_id: str):
        """Set conversation ID for context."""
        self.conversation_id = conversation_id
    
    def log_conversation_start(self, phone_number: str, is_known: bool):
        """Log conversation initialization."""
        status = "KNOWN PHARMACY" if is_known else "NEW LEAD"
        self.logger.info(
            f"🎬 CONVERSATION START | {phone_number} | {status}",
            extra={'conversation_id': self.conversation_id}
        )
    
    def log_user_message(self, message: str, analysis: dict = None):
        """Log user message with analysis results."""
        intent = analysis.get('intent', 'unknown') if analysis else 'unknown'
        confidence = analysis.get('confidence', 0.0) if analysis else 0.0
        
        self.logger.info(
            f"👤 USER: {message[:100]}{'...' if len(message) > 100 else ''}",
            extra={
                'conversation_id': self.conversation_id,
                'intent': intent,
                'confidence': confidence
            }
        )
    
    def log_bot_response(self, response: str, strategy: dict = None):
        """Log bot response with strategy information."""
        response_type = strategy.get('response_type', 'unknown') if strategy else 'unknown'
        
        self.logger.info(
            f"🤖 BOT: {response[:100]}{'...' if len(response) > 100 else ''}",
            extra={
                'conversation_id': self.conversation_id,
                'response_type': response_type
            }
        )
    
    def log_action_execution(self, action_type: str, success: bool, details: dict = None):
        """Log action execution results."""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(
            f"⚡ ACTION: {action_type} | {status}",
            extra={
                'conversation_id': self.conversation_id,
                'action_type': action_type,
                'success': success,
                'details': details or {}
            }
        )
    
    def log_api_call(self, endpoint: str, success: bool, response_time: float = None):
        """Log API call results."""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        timing = f" | {response_time:.2f}s" if response_time else ""
        
        self.logger.debug(
            f"🌐 API: {endpoint} | {status}{timing}",
            extra={
                'conversation_id': self.conversation_id,
                'endpoint': endpoint,
                'success': success,
                'response_time': response_time
            }
        )
    
    def log_llm_call(self, model: str, tokens_used: int = None, success: bool = True):
        """Log LLM API calls."""
        token_info = f" | {tokens_used} tokens" if tokens_used else ""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        
        self.logger.debug(
            f"🧠 LLM: {model} | {status}{token_info}",
            extra={
                'conversation_id': self.conversation_id,
                'model': model,
                'tokens': tokens_used,
                'success': success
            }
        )

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_colors: bool = True,
    enable_file_logging: bool = True
) -> ConversationLogger:
    """
    Set up comprehensive logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        enable_colors: Enable colored console output
        enable_file_logging: Enable file logging
        
    Returns:
        Configured ConversationLogger instance
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if enable_file_logging:
        os.makedirs('logs', exist_ok=True)
        if not log_file:
            log_file = f"logs/pharmacy_chatbot_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    if enable_colors:
        console_format = ColoredFormatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        # Add color flag to records
        class ColoredHandler(logging.StreamHandler):
            def emit(self, record):
                record.color = True
                super().emit(record)
        
        console_handler = ColoredHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
    else:
        console_format = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # File handler (always detailed, no colors)
    if enable_file_logging and log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)  # Always detailed for files
        
        file_format = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
    
    # Set root logger level
    root_logger.setLevel(logging.DEBUG)
    
    # Configure specific loggers
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    # Create conversation logger
    conv_logger = ConversationLogger()
    
    logging.info("🚀 Logging system initialized")
    logging.info(f"📊 Log level: {level}")
    if log_file:
        logging.info(f"📁 Log file: {log_file}")
    
    return conv_logger

class DebugContext:
    """Context manager for debug sessions with detailed logging."""
    
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.start_time = None
        self.logger = logging.getLogger(f"debug.{session_name}")
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"🔍 DEBUG SESSION START: {self.session_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        if exc_type:
            self.logger.error(f"❌ DEBUG SESSION FAILED: {self.session_name} | {duration.total_seconds():.2f}s | {exc_type.__name__}: {exc_val}")
        else:
            self.logger.info(f"✅ DEBUG SESSION COMPLETE: {self.session_name} | {duration.total_seconds():.2f}s")
    
    def log_step(self, step: str, data: dict = None):
        """Log a debug step with optional data."""
        self.logger.debug(f"📍 {step}", extra=data or {})
    
    def log_checkpoint(self, checkpoint: str, variables: dict = None):
        """Log a checkpoint with variable states."""
        var_info = ""
        if variables:
            var_strs = [f"{k}={v}" for k, v in variables.items()]
            var_info = f" | Variables: {', '.join(var_strs)}"
        
        self.logger.debug(f"🏁 CHECKPOINT: {checkpoint}{var_info}")

# Convenience function for quick debug logging
def debug_log(message: str, level: str = "DEBUG", **kwargs):
    """Quick debug logging function."""
    logger = logging.getLogger("debug")
    getattr(logger, level.lower())(message, extra=kwargs)

# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance."""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger = logging.getLogger(f"performance.{func.__module__}.{func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            duration = datetime.now() - start_time
            logger.info(f"⏱️ {func.__name__} completed in {duration.total_seconds():.3f}s")
            return result
        except Exception as e:
            duration = datetime.now() - start_time
            logger.error(f"❌ {func.__name__} failed after {duration.total_seconds():.3f}s: {e}")
            raise
    
    return wrapper