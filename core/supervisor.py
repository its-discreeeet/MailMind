from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_deepseek import ChatDeepSeek
from core.state import EmailState
from agents.filtering_agent import filter_email
from agents.summarization_agent import summarize_email
from agents.response_agent import generate_response
from agents.human_review_agent import review_draft
from utils.logger import logger
import config

# Define the state for the graph
class GraphState(TypedDict):
    email_state: EmailState
    llm: Annotated[ChatDeepSeek, "LLM instance"]

class EmailSupervisor:
    def __init__(self):
        self.llm = ChatDeepSeek(api_key=config.DEEPSEEK_API_KEY, model="deepseek-chat")
        self.workflow = self.build_graph()

    def build_graph(self):
        workflow = StateGraph(GraphState)

        # Define nodes
        workflow.add_node("filter_email", self.run_filter_email)
        workflow.add_node("summarize_email", self.run_summarize_email)
        workflow.add_node("generate_response", self.run_generate_response)
        workflow.add_node("human_review", self.run_human_review)

        # Set entry point
        workflow.set_entry_point("filter_email")

        # Define edges
        workflow.add_conditional_edges(
            "filter_email",
            self.decide_after_filtering,
            {"continue": "summarize_email", "end": END}
        )
        workflow.add_edge("summarize_email", "generate_response")
        workflow.add_conditional_edges(
            "generate_response",
            self.decide_after_response_generation,
            {"review": "human_review", "end": END}
        )
        workflow.add_edge("human_review", END)

        # Compile the graph
        return workflow.compile()

    # Node execution functions
    def run_filter_email(self, state: GraphState):
        logger.info("--- Running Filter Email Node ---")
        updates = filter_email(state['email_state'], state['llm'])
        state['email_state'].category = updates.get('category', 'error')
        return state

    def run_summarize_email(self, state: GraphState):
        logger.info("--- Running Summarize Email Node ---")
        updates = summarize_email(state['email_state'], state['llm'])
        state['email_state'].summary = updates.get('summary', '')
        return state

    def run_generate_response(self, state: GraphState):
        logger.info("--- Running Generate Response Node ---")
        updates = generate_response(state['email_state'], state['llm'])
        state['email_state'].draft_response = updates.get('draft_response', '')
        state['email_state'].needs_human_review = updates.get('needs_human_review', False)
        return state

    def run_human_review(self, state: GraphState):
        logger.info("--- Running Human Review Node ---")
        updates = review_draft(state['email_state'])
        state['email_state'].final_response = updates.get('final_response')
        state['email_state'].status = updates.get('status', 'reviewed')
        return state

    # Conditional edge logic
    def decide_after_filtering(self, state: GraphState):
        logger.info(f"--- Decision: After Filtering (Category: {state['email_state'].category}) ---")
        if state['email_state'].category == "spam":
            return "end"
        return "continue"

    def decide_after_response_generation(self, state: GraphState):
        logger.info(f"--- Decision: After Response Generation (Review needed: {state['email_state'].needs_human_review}) ---")
        if state['email_state'].needs_human_review:
            return "review"
        
        # If no review is needed, the draft is final
        state['email_state'].final_response = state['email_state'].draft_response
        state['email_state'].status = "approved_for_sending"
        return "end"

    def process_email(self, email: EmailState):
        initial_state: GraphState = {"email_state": email, "llm": self.llm}
        final_state = self.workflow.invoke(initial_state)
        return final_state['email_state']