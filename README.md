# Pharmacy Sales Chatbot - Production-Ready Architecture

A sophisticated, production-ready pharmacy sales chatbot with **clean architecture**, **excellent error handling**, and **high maintainability**. This system simulates handling inbound phone calls from pharmacies contacting Pharmesol, a pharmaceutical distribution company, emphasizing **usability, readability, and proper organization of logic**.

## 🎯 Overview

This system demonstrates:
- **Clean API Integration**: Robust pharmacy lookup with comprehensive error handling
- **Intelligent Conversations**: AI-powered personalized responses based on pharmacy data
- **Lead Generation**: Smart collection and management of new prospect information  
- **Action Processing**: Email automation and callback scheduling with audit trails
- **Production Features**: Structured logging, performance monitoring, and error recovery

## 🏗️ Architecture Overview

### Core Design Principles
- **Separation of Concerns**: Each component has a single, well-defined responsibility
- **Clean Abstractions**: Interfaces that hide complexity while providing powerful functionality
- **Error Resilience**: Comprehensive error handling at every layer
- **Observability**: Detailed logging and debugging throughout the system
- **Testability**: Components can be tested independently
- **Maintainability**: Easy to modify, extend, or replace parts

### Component Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   chatbot.py    │    │    models.py     │    │ logging_config  │
│  (Orchestrator) │    │ (Data Structures)│    │   (Observability│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                         │
         └────────────────────────┼─────────────────────────┘
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
    ▼                             ▼                             ▼
┌─────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│ integration │    │conversation_manager │    │ action_handler   │
│(API Layer)  │    │  (Business Logic)   │    │(Action Execution)│
└─────────────┘    └─────────────────────┘    └──────────────────┘
```

## 📦 Component Details

### 1. `models.py` - Clean Data Structures
- **PharmacyData**: Type-safe pharmacy information with computed properties
- **LeadData**: Lead generation data with completion tracking
- **ConversationState**: Complete conversation session state management
- **Enums**: Clear status and type definitions

**Key Benefits**: Type safety, data validation, clear business object definitions

### 2. `integration.py` - Robust API Integration
- **PharmacyLookup**: Clean API interface with retry logic and connection pooling
- **Comprehensive Error Handling**: Graceful degradation for API failures
- **Performance Features**: Connection pooling, automatic retries, health checks
- **Search Capabilities**: Flexible pharmacy search and filtering

**Key Benefits**: Reliable external service integration, excellent error recovery

### 3. `conversation_manager.py` - Business Logic
- **ConversationFlowManager**: Intent analysis and conversation flow control
- **Message Analysis**: Smart extraction of entities and user intentions
- **Context Management**: Maintains conversation state and history
- **Strategy Determination**: Decides optimal response approaches

**Key Benefits**: Separates conversation logic from LLM interactions, highly maintainable

### 4. `action_handler.py` - Action Execution
- **ActionHandler**: Clean action execution with comprehensive result tracking
- **Structured Results**: Consistent success/failure handling across all actions
- **Email Templates**: Smart email generation based on pharmacy type and context
- **Performance Monitoring**: Track action success rates and execution history

**Key Benefits**: Testable business actions, consistent error handling, audit trails

### 5. `logging_config.py` - Observability
- **ConversationLogger**: Specialized logging for conversation tracking
- **DebugContext**: Context manager for detailed debugging sessions
- **Performance Monitoring**: Automatic function performance tracking
- **Structured Logging**: Consistent log formats with contextual information

**Key Benefits**: Excellent debugging capabilities, production monitoring ready

### 6. `chatbot.py` - Main Orchestrator
- **PharmacySalesChatbot**: Clean main interface that coordinates all components
- **Context Management**: Proper session and resource management
- **Fallback Handling**: Graceful degradation when services are unavailable
- **Comprehensive API**: Simple to use, powerful underneath

**Key Benefits**: Clean public API, proper resource management, excellent usability

## 📁 Project Structure

```
pharmechallenge/
├── main.py                  # Main simulation script (entry point)
├── README.md               # This documentation
├── requirements.txt         # Python dependencies
├── .env                    # Environment configuration
├── .env.example            # Environment template
├── core/                   # Core chatbot architecture
│   ├── __init__.py
│   ├── chatbot.py          # Main orchestrator - clean public API
│   ├── models.py           # Clean data structures and business objects
│   ├── conversation_manager.py # Business logic and conversation flow
│   └── action_handler.py   # Action execution with comprehensive results
├── api/                    # API integration layer
│   ├── __init__.py
│   ├── integration.py      # Robust API client with error handling
│   └── llm.py              # Main chatbot class with LLM interactions
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── logging_config.py   # Advanced logging and debugging features
│   ├── prompt.py           # System prompts and conversation templates
│   └── function_calls.py   # Mock utility functions (email, callbacks)
├── demos/                  # Demo scripts and tests
│   ├── __init__.py
│   ├── demo_refactored.py  # Comprehensive architecture demonstration
│   ├── full_demo.py        # Complete AI integration demo
│   ├── demo.py             # Basic functionality demo
├── tests/    
│   └── tests.py            # Comprehensive test suite
├── docs/                   # Additional documentation
│   ├── ARCHITECTURE_SUMMARY.md
│   ├── ENVIRONMENT_CONFIG.md
│   └── README.md           # Copy of main README
└── logs/                   # Automatic log file directory
    └── pharmacy_chatbot_*.log
```

## ⚙️ Installation & Configuration

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Copy the environment template:
```bash
cp .env.example .env
```

The environment file contains:
```bash
# OpenAI API key for LLM functionality  
OPENAI_API_KEY=your-openai-api-key-here

# Pharmacy API endpoint for data lookup
PHARMACY_API_URL=https://67e14fb758cc6bf785254550.mockapi.io
```

**Note**: The actual `.env` file is included for demo purposes but would normally be excluded from version control for security.

## 🚀 Usage Examples

### Basic Usage (Refactored Architecture)
```python
from chatbot import PharmacySalesChatbot

# Initialize with clean configuration (uses environment variables)
with PharmacySalesChatbot(log_level="INFO") as bot:
    # Start conversation
    greeting = bot.start_conversation("+1-555-123-4567")
    print(f"Bot: {greeting}")
    
    # Process messages
    response = bot.process_message("Can you send me pricing information?")
    print(f"Bot: {response}")
    
    # Get comprehensive summary
    summary = bot.get_conversation_summary()
    print(f"Actions taken: {summary['actions_taken']}")
```

### Debug Mode
```python
# Enable comprehensive debugging
with PharmacySalesChatbot(enable_debug=True) as bot:
    # All operations are logged in detail
    greeting = bot.start_conversation("+1-555-999-8888")
    response = bot.process_message("Hi, I'm from Metro Pharmacy in Seattle")
    
    # Check logs/ directory for detailed debugging information
```

### Component Testing
```python
from integration import PharmacyAPIClient
from conversation_manager import ConversationFlowManager

# Test components independently (uses PHARMACY_API_URL from environment)
with PharmacyAPIClient() as api:
    pharmacies = api.get_all_pharmacies()
    high_volume = api.search_pharmacies(min_volume=10000)

# Test conversation logic
flow_manager = ConversationFlowManager()
analysis = flow_manager.analyze_user_message("Send me pricing info at test@pharmacy.com")
```

## 🎮 Demo Scripts

### Run Comprehensive Demo (Refactored)
```bash
python demo_refactored.py
```
Shows the complete refactored architecture with clean error handling and logging.

### Run Original Demo
```bash
python main.py
```
Runs the original demonstration scenarios.

### Run Complete AI Demo
```bash
python full_demo.py
```
Comprehensive demonstration with full OpenAI integration.

### Interactive Mode
```bash
python main.py interactive
```
Allows real-time conversation with the chatbot.

## 🧪 Testing & Debugging

### Run Tests
```bash
python main.py tests
```

### Enable Debug Logging
```bash
python -c "
from chatbot import PharmacySalesChatbot
with PharmacySalesChatbot(enable_debug=True) as bot:
    bot.start_conversation('+1-555-TEST-123')
    bot.process_message('Test message')
# Check logs/ directory for detailed debug information
"
```

### Component Health Checks
```bash
python -c "
from integration import PharmacyAPIClient
with PharmacyAPIClient() as api:
    print('API Health:', api.health_check())
    print('API Stats:', api.get_api_stats())
"
```

## 💬 Sample Conversation Flows

### Known Pharmacy
```
🤖 Great! I see you're calling from Central Pharmacy in Springfield, IL. 
   With your high prescription volume, you'd be an excellent fit for our 
   premium tier services. How can Pharmesol help you today?

👤 We're interested in better pricing for high-volume pharmacies.

🤖 Perfect! With your volume, we can offer dedicated account management 
   and priority inventory allocation. Would you like me to send you 
   detailed pricing information?
```

### Unknown Pharmacy (New Lead)
```
🤖 Thank you for calling Pharmesol! I don't have your information in 
   our system yet. Could you please tell me your pharmacy name, 
   location, and monthly prescription volume?

👤 I'm calling from MedCare Pharmacy in downtown Chicago. We fill 
   about 8,000 prescriptions per month.

🤖 Thank you! MedCare Pharmacy sounds like a great fit for our services. 
   With 8,000 prescriptions monthly, you'd benefit from our bulk pricing 
   and reliable delivery schedules...
```

## 🎯 Key Improvements Over Original Architecture

### 1. **Better Code Organization**
- **Before**: Monolithic classes with mixed responsibilities
- **After**: Clean separation with single-responsibility components

### 2. **Superior Error Handling** 
- **Before**: Basic try-catch blocks
- **After**: Comprehensive error handling with graceful degradation at every layer

### 3. **Enhanced Observability**
- **Before**: Basic logging
- **After**: Structured logging, debug contexts, performance monitoring, conversation tracking

### 4. **Improved Maintainability**
- **Before**: Tightly coupled components
- **After**: Loosely coupled with clean interfaces, easy to modify or extend

### 5. **Better Data Management**
- **Before**: Dictionary-based data handling
- **After**: Type-safe data models with validation and computed properties

### 6. **Enhanced Testability**
- **Before**: Difficult to test components in isolation
- **After**: Each component can be tested independently with clear interfaces

## 📊 Performance & Reliability Features

- **Connection Pooling**: Efficient API connections with automatic retry
- **Circuit Breaker Pattern**: API health checks with fallback behavior
- **Structured Logging**: Production-ready logging with log rotation
- **Memory Management**: Proper resource cleanup with context managers
- **Performance Monitoring**: Automatic tracking of function execution times
- **Error Recovery**: Graceful degradation when external services fail

## 🔧 Key Features

### 1. Pharmacy Recognition
- Automatic lookup of calling pharmacy
- Personalized greetings using pharmacy data
- Volume-based conversation customization

### 2. Lead Generation
- Information collection from unknown callers
- Email and callback scheduling with audit trails
- CRM integration simulation with completion tracking

### 3. Error Handling
- Graceful API failure handling
- Missing data accommodation
- User-friendly error messages with fallback responses

### 4. Action Processing
- Smart email template generation based on pharmacy type
- Callback scheduling with follow-up task creation
- Lead logging with completion percentage tracking

## 🔒 Security Considerations

- API keys are handled securely through environment variables
- No sensitive information is logged or stored
- Input validation prevents injection attacks
- Error messages don't expose system internals
- Proper resource cleanup prevents memory leaks

## 🎉 Benefits Summary

This refactored architecture provides:

- **🧩 Modularity**: Clean component separation makes the system easy to understand and modify
- **🛡️ Reliability**: Comprehensive error handling ensures the system gracefully handles failures
- **🔍 Observability**: Detailed logging and debugging make troubleshooting straightforward
- **🧪 Testability**: Components can be tested independently with clear interfaces
- **📈 Scalability**: Clean abstractions make it easy to add new features or integrate new services
- **🎯 Usability**: Simple API that's powerful underneath - easy for developers to use
- **🔧 Maintainability**: Well-organized code that's easy to modify, extend, or refactor

## 📈 Future Enhancements

Potential improvements could include:
- Voice-to-text integration for real phone calls
- Advanced CRM system integration
- Machine learning for better intent classification
- Multi-language support with localized templates
- Advanced analytics and reporting dashboards
- A/B testing framework for conversation optimization

## 📄 License

This is a demonstration project for educational purposes showcasing production-ready software engineering practices.

---

The refactored system demonstrates **production-ready code** with **excellent engineering practices** while maintaining the core functionality of the original pharmacy sales chatbot. The architecture emphasizes **usability, readability, and proper organization of logic** as requested.