# Pharmacy Sales Chatbot Simulation

A text-based inbound pharmacy sales chatbot that simulates handling phone calls from pharmacies contacting Pharmesol, a pharmaceutical distribution company.

## Overview

This system demonstrates:
- API integration to look up existing pharmacy customers
- Personalized conversations based on pharmacy data
- Lead generation for new prospects
- Mock functions for email sending and callback scheduling
- Comprehensive error handling and edge case management

## Features

- **Pharmacy Lookup**: Integrates with external API to identify calling pharmacies
- **Personalized Conversations**: Customizes responses based on pharmacy data (volume, location)
- **Lead Generation**: Collects information from unknown callers
- **Action Handling**: Processes email requests and callback scheduling
- **Comprehensive Testing**: Includes unit tests and integration tests

## Project Structure

```
pharmechallenge/
├── main.py              # Main simulation script with demo scenarios
├── integration.py       # API integration for pharmacy lookup
├── llm.py              # LLM chatbot logic and conversation flow
├── prompt.py           # System prompts and conversation templates
├── function_calls.py   # Mock utility functions (email, callbacks)
├── tests.py            # Comprehensive test suite
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. The OpenAI API key is already configured in the `.env` file for immediate use. If you need to change it, edit the `.env` file:
```bash
# .env file contains:
OPENAI_API_KEY=your-api-key-here
```

**Note**: The `.env` file is included for demo purposes but would normally be excluded from version control for security.

## Usage

### Run Sample Scenarios
```bash
python main.py
```
This runs two demonstration scenarios:
1. Known pharmacy call (looked up from API)
2. Unknown pharmacy call (new lead generation)

### Run Complete Demo with AI
```bash
python full_demo.py
```
This runs a comprehensive demonstration with full OpenAI integration showing real AI conversations.

### Interactive Mode
```bash
python main.py interactive
```
Allows you to have a real conversation with the chatbot.

### Simulate Specific Phone Number
```bash
python main.py +1234567890
```
Simulates a call from a specific phone number.

### Run Tests
```bash
python main.py test
```
or
```bash
python tests.py
```

## API Integration

The system integrates with:
- **Pharmacy API**: `https://67e14fb758cc6bf785254550.mockapi.io/pharmacies`
- **OpenAI API**: For natural language processing and conversation

## Core Components

### 1. Integration Module (`integration.py`)
- Handles API calls to pharmacy database
- Provides pharmacy lookup by phone number
- Manages API errors and timeouts gracefully

### 2. LLM Module (`llm.py`)
- Main chatbot logic using OpenAI's API
- Conversation flow management
- Lead information extraction
- Action processing (emails, callbacks)

### 3. Prompts Module (`prompt.py`)
- System prompts for the LLM
- Conversation templates
- Response formatting utilities

### 4. Function Calls Module (`function_calls.py`)
- Mock implementations of business functions
- Email sending simulation
- Callback scheduling
- Lead logging

## Sample Conversation Flows

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

## Testing

The test suite includes:

### Unit Tests
- API integration testing with mocked responses
- Chatbot conversation flow testing
- Mock function testing
- Edge case handling

### Integration Tests
- Real API connectivity testing (when available)
- End-to-end conversation flow testing

### Edge Cases Covered
- API timeouts and failures
- Malformed API responses
- Missing data fields
- Invalid phone numbers
- Empty user inputs
- LLM API failures

## Key Features

### 1. Pharmacy Recognition
- Automatic lookup of calling pharmacy
- Personalized greetings using pharmacy data
- Volume-based conversation customization

### 2. Lead Generation
- Information collection from unknown callers
- Email and callback scheduling
- CRM integration simulation

### 3. Error Handling
- Graceful API failure handling
- Missing data accommodation
- User-friendly error messages

### 4. Action Processing
- Email information sending
- Callback scheduling
- Lead logging and follow-up task creation

## Security Considerations

- API keys are handled securely through environment variables
- No sensitive information is logged or stored
- Input validation prevents injection attacks
- Error messages don't expose system internals

## Future Enhancements

Potential improvements could include:
- Voice-to-text integration for real phone calls
- CRM system integration
- Advanced NLP for better information extraction
- Multi-language support
- Analytics and reporting features

## License

This is a demonstration project for educational purposes.