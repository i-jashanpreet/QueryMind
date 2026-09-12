import uuid
import datetime
from app.schemas.conversation import ConversationState
from app.schemas.analysis import QueryAnalysis
from app.schemas.clarification import ClarificationResponse

class ConversationManager:
    """In-memory conversation store for QueryMind."""
    
    _conversations: dict[str, ConversationState] = {}

    @classmethod
    def create_conversation(
        cls, 
        original_question: str, 
        query_analysis: QueryAnalysis, 
        clarification: ClarificationResponse | None = None,
        clarification_type: str | None = None,
    ) -> str:
        """Create and store a new conversation, returning its ID."""
        conv_id = str(uuid.uuid4())
        state = ConversationState(
            conversation_id=conv_id,
            original_question=original_question,
            query_analysis=query_analysis,
            clarification=clarification,
            clarification_type=clarification_type,
            pending_clarification=(clarification is not None and clarification.needs_clarification)
        )
        cls._conversations[conv_id] = state
        return conv_id

    @classmethod
    def get_conversation(cls, conversation_id: str) -> ConversationState | None:
        """Retrieve a conversation by ID."""
        return cls._conversations.get(conversation_id)

    @classmethod
    def update_conversation(cls, conversation_id: str, **kwargs) -> ConversationState:
        """Update fields of an existing conversation."""
        state = cls._conversations.get(conversation_id)
        if not state:
            raise ValueError(f"Conversation {conversation_id} not found.")
        
        # Update allowed fields
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        state.updated_at = datetime.datetime.now(datetime.timezone.utc)
        return state

    @classmethod
    def delete_conversation(cls, conversation_id: str) -> None:
        """Remove a conversation from the store."""
        if conversation_id in cls._conversations:
            del cls._conversations[conversation_id]
