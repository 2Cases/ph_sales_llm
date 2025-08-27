"""
Data models and structures for the pharmacy sales chatbot.
Provides clean abstractions for pharmacy data, conversations, and actions.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime

class ConversationStatus(Enum):
    """Status of the current conversation."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PENDING_EMAIL = "pending_email"
    PENDING_CALLBACK = "pending_callback"

class PharmacyType(Enum):
    """Classification of pharmacy by prescription volume."""
    HIGH_VOLUME = "high_volume"  # 10,000+ per month
    MEDIUM_VOLUME = "medium_volume"  # 5,000-9,999 per month
    LOW_VOLUME = "low_volume"  # 1,000-4,999 per month
    STARTUP = "startup"  # Less than 1,000 per month

@dataclass
class PharmacyData:
    """Clean data structure for pharmacy information."""
    name: str
    phone: str
    city: Optional[str] = None
    state: Optional[str] = None
    rx_volume: Optional[int] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None
    
    @property
    def location_display(self) -> str:
        """Get formatted location string."""
        if self.city and self.state:
            return f"{self.city}, {self.state}"
        elif self.city:
            return self.city
        elif self.state:
            return self.state
        return "Unknown location"
    
    @property
    def pharmacy_type(self) -> PharmacyType:
        """Classify pharmacy by volume."""
        if not self.rx_volume:
            return PharmacyType.STARTUP
        
        if self.rx_volume >= 10000:
            return PharmacyType.HIGH_VOLUME
        elif self.rx_volume >= 5000:
            return PharmacyType.MEDIUM_VOLUME
        elif self.rx_volume >= 1000:
            return PharmacyType.LOW_VOLUME
        else:
            return PharmacyType.STARTUP
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> 'PharmacyData':
        """Create PharmacyData from API response."""
        return cls(
            name=api_data.get('name', 'Unknown Pharmacy'),
            phone=api_data.get('phone', ''),
            city=api_data.get('city'),
            state=api_data.get('state'),
            rx_volume=api_data.get('rxVolume'),
            email=api_data.get('email'),
            contact_person=api_data.get('contactPerson')
        )

@dataclass
class LeadData:
    """Structure for new lead information collection."""
    phone: str
    pharmacy_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    rx_volume: Optional[int] = None
    interests: List[str] = field(default_factory=list)
    notes: str = ""
    
    @property
    def is_complete(self) -> bool:
        """Check if we have minimum required information."""
        return bool(self.pharmacy_name and self.email)
    
    @property
    def completion_percentage(self) -> int:
        """Calculate how complete the lead data is."""
        fields = [
            self.pharmacy_name, self.contact_person, self.email,
            self.location, self.rx_volume
        ]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)

@dataclass
class ConversationMessage:
    """Structure for conversation messages."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationState:
    """Complete state of a conversation session."""
    phone_number: str
    status: ConversationStatus = ConversationStatus.ACTIVE
    pharmacy_data: Optional[PharmacyData] = None
    lead_data: Optional[LeadData] = None
    messages: List[ConversationMessage] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_known_pharmacy(self) -> bool:
        """Check if this is a known pharmacy."""
        return self.pharmacy_data is not None
    
    @property
    def current_pharmacy_name(self) -> str:
        """Get the current pharmacy name from either source."""
        if self.pharmacy_data:
            return self.pharmacy_data.name
        elif self.lead_data and self.lead_data.pharmacy_name:
            return self.lead_data.pharmacy_name
        return "your pharmacy"
    
    @property
    def has_email(self) -> bool:
        """Check if we have an email address."""
        if self.pharmacy_data and self.pharmacy_data.email:
            return True
        if self.lead_data and self.lead_data.email:
            return True
        return False
    
    @property
    def email_address(self) -> Optional[str]:
        """Get the email address from either source."""
        if self.pharmacy_data and self.pharmacy_data.email:
            return self.pharmacy_data.email
        if self.lead_data and self.lead_data.email:
            return self.lead_data.email
        return None
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation."""
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
    
    def add_action(self, action: str):
        """Record an action taken during the conversation."""
        if action not in self.actions_taken:
            self.actions_taken.append(action)

@dataclass
class ActionRequest:
    """Structure for requested actions (email, callback, etc.)."""
    action_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def email_request(cls, email: Optional[str] = None) -> 'ActionRequest':
        """Create an email action request."""
        return cls(
            action_type='email',
            parameters={'email': email} if email else {}
        )
    
    @classmethod
    def callback_request(cls, preferred_time: Optional[str] = None) -> 'ActionRequest':
        """Create a callback action request."""
        return cls(
            action_type='callback',
            parameters={'preferred_time': preferred_time} if preferred_time else {}
        )