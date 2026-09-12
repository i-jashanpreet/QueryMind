import pytest
from app.services.conversation_manager import ConversationManager
from app.schemas.analysis import QueryAnalysis
from app.schemas.clarification import ClarificationResponse, ClarificationOption

def get_dummy_analysis():
    return QueryAnalysis(
        question="dummy",
        intent="lookup",
        entities=[],
        filters={},
        ambiguities=[],
        missing_information=[],
        needs_clarification=False
    )

def get_dummy_clarification():
    return ClarificationResponse(
        needs_clarification=True,
        clarification_type="entity",
        question="Which entity?",
        options=[]
    )

class TestConversationManager:
    
    @pytest.fixture(autouse=True)
    def reset_manager(self):
        ConversationManager._conversations.clear()

    def test_create_conversation(self):
        analysis = get_dummy_analysis()
        clarification = get_dummy_clarification()
        conv_id = ConversationManager.create_conversation("dummy", analysis, clarification, "entity")
        
        assert conv_id is not None
        state = ConversationManager.get_conversation(conv_id)
        assert state is not None
        assert state.original_question == "dummy"
        assert state.pending_clarification is True
        assert state.clarification_type == "entity"

    def test_update_conversation(self):
        conv_id = ConversationManager.create_conversation("dummy", get_dummy_analysis(), get_dummy_clarification(), "entity")
        
        ConversationManager.update_conversation(conv_id, pending_clarification=False)
        state = ConversationManager.get_conversation(conv_id)
        assert state.pending_clarification is False

    def test_delete_conversation(self):
        conv_id = ConversationManager.create_conversation("dummy", get_dummy_analysis())
        assert ConversationManager.get_conversation(conv_id) is not None
        
        ConversationManager.delete_conversation(conv_id)
        assert ConversationManager.get_conversation(conv_id) is None

    def test_unknown_conversation_id(self):
        assert ConversationManager.get_conversation("non-existent") is None

    def test_multiple_conversations_are_isolated(self):
        id1 = ConversationManager.create_conversation("q1", get_dummy_analysis(), get_dummy_clarification(), "entity")
        id2 = ConversationManager.create_conversation("q2", get_dummy_analysis(), get_dummy_clarification(), "time_range")
        
        state1 = ConversationManager.get_conversation(id1)
        state2 = ConversationManager.get_conversation(id2)
        
        assert state1.original_question == "q1"
        assert state1.clarification_type == "entity"
        
        assert state2.original_question == "q2"
        assert state2.clarification_type == "time_range"
