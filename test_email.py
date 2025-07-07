import pytest
from unittest.mock import patch, MagicMock
from core.state import EmailState
from agents.filtering_agent import filter_email
from agents.summarization_agent import summarize_email
from agents.response_agent import generate_response
import config

# Mock LangChain LLM response
class MockLLMResponse:
    def __init__(self, content):
        self.content = content

class MockStructuredLLM:
    def __init__(self, category):
        self.category = category
    def invoke(self, *args, **kwargs):
        from agents.filtering_agent import EmailCategory
        return EmailCategory(category=self.category)

@pytest.fixture
def sample_email_state():
    return EmailState(
        email_id="test-123",
        subject="Question about your services",
        sender="test@example.com",
        body="Hello, I'm interested in your services. Can you tell me more?",
        cleaned_body="Hello, I'm interested in your services. Can you tell me more?"
    )

@pytest.fixture
def mock_llm():
    # This mock can be used for simple text-in, text-out calls
    llm = MagicMock()
    llm.invoke.return_value = MockLLMResponse("This is a mock response.")
    return llm

def test_config_loading():
    """Tests if essential configs are loaded."""
    assert config.DEEPSEEK_API_KEY is not None
    # Add more assertions if needed

@patch('agents.filtering_agent.ChatDeepseek')
def test_filtering_agent(MockChatDeepseek, sample_email_state):
    """Tests the filtering agent's classification logic."""
    mock_llm_instance = MockChatDeepseek.return_value
    mock_llm_instance.with_structured_output.return_value = MockStructuredLLM(category="needs_review")

    result = filter_email(sample_email_state, mock_llm_instance)
    assert result['category'] == "needs_review"

@patch('agents.summarization_agent.ChatDeepseek')
def test_summarization_agent(MockChatDeepseek, sample_email_state):
    """Tests the summarization agent."""
    mock_llm_instance = MockChatDeepseek.return_value
    mock_llm_instance.invoke.return_value = MockLLMResponse("Client is asking for more info on services.")
    
    # Create a chain mock
    chain_mock = MagicMock()
    chain_mock.invoke.return_value = MockLLMResponse("Client is asking for more info on services.")
    
    with patch('langchain_core.prompts.ChatPromptTemplate.from_messages') as mock_prompt:
        mock_prompt.return_value.__or__.return_value = chain_mock # Mock the | operator
        result = summarize_email(sample_email_state, mock_llm_instance)

    assert "Client is asking for more info" in result['summary']

@patch('agents.response_agent.ChatDeepseek')
def test_response_agent(MockChatDeepseek, sample_email_state):
    """Tests the response generation agent."""
    sample_email_state.category = "urgent"  # Ensure response is generated
    mock_llm_instance = MockChatDeepseek.return_value
    mock_llm_instance.invoke.return_value = MockLLMResponse("Thank you for your inquiry. We will get back to you shortly.")

    # Mock the chain
    chain_mock = MagicMock()
    chain_mock.invoke.return_value = MockLLMResponse("Thank you for your inquiry. We will get back to you shortly.")

    with patch('langchain_core.prompts.ChatPromptTemplate.from_messages') as mock_prompt:
        mock_prompt.return_value.__or__.return_value = chain_mock
        result = generate_response(sample_email_state, mock_llm_instance)
    
    assert "Thank you for your inquiry" in result['draft_response']
    assert result['needs_human_review'] is False # Based on simple keyword logic

@patch('core.email_imap.imaplib')
def test_imap_connection_failure(mock_imaplib):
    """Tests graceful failure of IMAP connection."""
    mock_imaplib.IMAP4_SSL.side_effect = Exception("Connection failed")
    from core.email_imap import fetch_unread_emails
    emails = fetch_unread_emails()
    assert emails == []

@patch('core.email_sender.smtplib.SMTP')
def test_smtp_send_success(mock_smtp):
    """Tests a successful SMTP call."""
    from core.email_sender import send_email
    send_email("recipient@example.com", "Test Subject", "Test Body")
    
    # Check if SMTP was called, logged in, and mail was sent
    mock_smtp.assert_called_with(config.EMAIL_SERVER, config.EMAIL_PORT)
    instance = mock_smtp.return_value
    instance.starttls.assert_called_once()
    instance.login.assert_called_with(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
    instance.sendmail.assert_called_once()
    instance.quit.assert_called_once()