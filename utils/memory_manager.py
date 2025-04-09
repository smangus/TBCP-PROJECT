# utils/memory_manager.py

from typing import Dict, Any, List, Optional
import os
import json
import datetime
import uuid
import time
import shutil

class MemoryManager:
    """
    Centralized memory management system for the TechBio C-Suite CoPilot.
    
    This manager handles different types of memory:
    1. Agent-specific memories (e.g., TxGemma's molecular memory)
    2. Cross-agent shared knowledge
    3. Conversation history
    """
    
    def __init__(self, storage_dir: str = "./memory"):
        """
        Initialize the memory manager with appropriate storage directories.
        
        Args:
            storage_dir (str): Base directory for storing memories
        """
        self.storage_dir = storage_dir
        self.agent_memory_dir = os.path.join(storage_dir, "agent_memory")
        self.shared_memory_dir = os.path.join(storage_dir, "shared_memory")
        self.conversation_dir = os.path.join(storage_dir, "conversations")
        
        # Create directories if they don't exist
        for directory in [self.storage_dir, self.agent_memory_dir, 
                         self.shared_memory_dir, self.conversation_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # In-memory cache for faster access
        self.memory_cache = {
            "agent_memory": {},
            "shared_memory": {},
            "conversations": {}
        }
        
        # Load existing memories into cache
        self._load_memories()
    
    def _load_memories(self):
        """Load existing memories from disk into the cache."""
        # Load agent memories
        for agent_name in os.listdir(self.agent_memory_dir):
            agent_dir = os.path.join(self.agent_memory_dir, agent_name)
            if os.path.isdir(agent_dir):
                self.memory_cache["agent_memory"][agent_name] = {}
                for memory_file in os.listdir(agent_dir):
                    if memory_file.endswith('.json'):
                        file_path = os.path.join(agent_dir, memory_file)
                        memory_type = memory_file.split('.')[0]  # e.g., 'plan', 'execution', 'molecular'
                        with open(file_path, 'r') as f:
                            self.memory_cache["agent_memory"][agent_name][memory_type] = json.load(f)
        
        # Load shared memories
        for memory_file in os.listdir(self.shared_memory_dir):
            if memory_file.endswith('.json'):
                file_path = os.path.join(self.shared_memory_dir, memory_file)
                memory_type = memory_file.split('.')[0]
                with open(file_path, 'r') as f:
                    self.memory_cache["shared_memory"][memory_type] = json.load(f)
        
        # Load recent conversations (limited to 100 most recent)
        conversation_files = []
        for conv_file in os.listdir(self.conversation_dir):
            if conv_file.endswith('.json'):
                file_path = os.path.join(self.conversation_dir, conv_file)
                file_time = os.path.getmtime(file_path)
                conversation_files.append((file_path, file_time))
        
        # Sort by modification time (newest first) and take most recent 100
        conversation_files.sort(key=lambda x: x[1], reverse=True)
        for file_path, _ in conversation_files[:100]:
            with open(file_path, 'r') as f:
                conv_data = json.load(f)
                conv_id = os.path.basename(file_path).split('.')[0]
                self.memory_cache["conversations"][conv_id] = conv_data
    
    def get_agent_memory(self, agent_name: str, memory_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve memory for a specific agent.
        
        Args:
            agent_name (str): Name of the agent (e.g., 'molecular_agent')
            memory_type (Optional[str]): Specific type of memory to retrieve (e.g., 'molecular')
            
        Returns:
            Dict[str, Any]: The requested memory
        """
        if agent_name not in self.memory_cache["agent_memory"]:
            return {}
        
        if memory_type:
            return self.memory_cache["agent_memory"][agent_name].get(memory_type, {})
        else:
            return self.memory_cache["agent_memory"][agent_name]
    
    def update_agent_memory(self, agent_name: str, memory_type: str, memory_data: Dict[str, Any]):
        """
        Update memory for a specific agent.
        
        Args:
            agent_name (str): Name of the agent (e.g., 'molecular_agent')
            memory_type (str): Type of memory to update (e.g., 'molecular')
            memory_data (Dict[str, Any]): The memory data to store
        """
        # Special handling for molecular knowledge
        if agent_name == "molecular_agent" and memory_type == "molecular_knowledge":
            self._merge_molecular_knowledge(memory_data)
            return
        
        # Initialize agent memory if it doesn't exist
        if agent_name not in self.memory_cache["agent_memory"]:
            self.memory_cache["agent_memory"][agent_name] = {}
        
        # Update memory in cache
        self.memory_cache["agent_memory"][agent_name][memory_type] = memory_data
        
        # Ensure agent directory exists
        agent_dir = os.path.join(self.agent_memory_dir, agent_name)
        os.makedirs(agent_dir, exist_ok=True)
        
        # Save to disk
        self._save_agent_memory(agent_name, memory_type, memory_data)
    
    def _save_agent_memory(self, agent_name: str, memory_type: str, memory_data: Dict[str, Any]):
        """Save agent memory to disk with proper error handling."""
        agent_dir = os.path.join(self.agent_memory_dir, agent_name)
        file_path = os.path.join(agent_dir, f"{memory_type}.json")
        
        # Create backup if file exists
        if os.path.exists(file_path):
            backup_path = file_path + ".bak"
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                print(f"Warning: Could not create backup of {file_path}: {e}")
        
        # Save new data
        try:
            with open(file_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving to {file_path}: {e}")
            # Restore from backup if available
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, file_path)
                    print(f"Restored {file_path} from backup")
                except Exception as e2:
                    print(f"Error restoring backup: {e2}")
    
    def _merge_molecular_knowledge(self, new_knowledge: Dict[str, Any]):
        """Specialized method to merge molecular knowledge from TxGemma."""
        if "molecular_agent" not in self.memory_cache["agent_memory"]:
            self.memory_cache["agent_memory"]["molecular_agent"] = {}
            
        existing = self.memory_cache["agent_memory"].get("molecular_agent", {}).get("molecular_knowledge", {})
        
        # Intelligent merging of molecular knowledge
        for key, new_items in new_knowledge.items():
            if key not in existing:
                existing[key] = []
            
            # Add new items, avoiding duplicates
            if isinstance(new_items, list):
                for item in new_items:
                    if item not in existing[key]:
                        existing[key].append(item)
            else:
                # Handle case where new_items is not a list
                if new_items not in existing[key]:
                    existing[key].append(new_items)
        
        # Update the cache
        self.memory_cache["agent_memory"]["molecular_agent"]["molecular_knowledge"] = existing
        
        # Save to disk
        self._save_agent_memory("molecular_agent", "molecular_knowledge", existing)
    
    def get_shared_memory(self, memory_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve shared memory across agents.
        
        Args:
            memory_type (Optional[str]): Specific type of shared memory to retrieve
            
        Returns:
            Dict[str, Any]: The requested shared memory
        """
        if memory_type:
            return self.memory_cache["shared_memory"].get(memory_type, {})
        else:
            return self.memory_cache["shared_memory"]
    
    def update_shared_memory(self, memory_type: str, memory_data: Dict[str, Any]):
        """
        Update shared memory across agents.
        
        Args:
            memory_type (str): Type of memory to update
            memory_data (Dict[str, Any]): The memory data to store
        """
        # Update memory in cache
        self.memory_cache["shared_memory"][memory_type] = memory_data
        
        # Save to disk
        file_path = os.path.join(self.shared_memory_dir, f"{memory_type}.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving shared memory to {file_path}: {e}")
    
    def record_conversation(self, user_query: str, agent_responses: Dict[str, str], 
                           synthesis_response: str, selected_agents: List[str]) -> str:
        """
        Record a conversation for future reference.
        
        Args:
            user_query (str): The original user query
            agent_responses (Dict[str, str]): Responses from each agent
            synthesis_response (str): The final synthesized response
            selected_agents (List[str]): List of agents that contributed
        
        Returns:
            str: Unique ID of the recorded conversation
        """
        # Generate unique conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Create conversation record
        conversation = {
            "id": conversation_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_query": user_query,
            "agent_responses": agent_responses,
            "synthesis_response": synthesis_response,
            "selected_agents": selected_agents
        }
        
        # Store in cache
        self.memory_cache["conversations"][conversation_id] = conversation
        
        # Save to disk
        file_path = os.path.join(self.conversation_dir, f"{conversation_id}.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(conversation, f, indent=2)
        except Exception as e:
            print(f"Error saving conversation to {file_path}: {e}")
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific conversation.
        
        Args:
            conversation_id (str): Unique ID of the conversation
            
        Returns:
            Dict[str, Any]: The conversation data
        """
        return self.memory_cache["conversations"].get(conversation_id, {})
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search through conversation history for relevant conversations.
        
        Args:
            query (str): The search query
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of relevant conversations
        """
        # Simple search implementation - can be enhanced with vector embedding search
        results = []
        query_lower = query.lower()
        
        for conv_id, conversation in self.memory_cache["conversations"].items():
            # Check if query appears in user question or response
            if (query_lower in conversation["user_query"].lower() or 
                query_lower in conversation["synthesis_response"].lower()):
                results.append(conversation)
                
            # Check agent responses
            for agent_name, response in conversation["agent_responses"].items():
                if isinstance(response, str) and query_lower in response.lower():
                    if conversation not in results:
                        results.append(conversation)
                    break
            
            if len(results) >= limit:
                break
        
        return results[:limit]
    
    def clear_memory(self, agent_name: Optional[str] = None, memory_type: Optional[str] = None):
        """
        Clear specific memory or all memories.
        
        Args:
            agent_name (Optional[str]): Name of the agent to clear memory for. If None, clears for all agents.
            memory_type (Optional[str]): Type of memory to clear. If None, clears all memory types.
        """
        if agent_name:
            if memory_type:
                # Clear specific memory type for specific agent
                if agent_name in self.memory_cache["agent_memory"] and memory_type in self.memory_cache["agent_memory"][agent_name]:
                    self.memory_cache["agent_memory"][agent_name][memory_type] = {}
                    file_path = os.path.join(self.agent_memory_dir, agent_name, f"{memory_type}.json")
                    if os.path.exists(file_path):
                        os.remove(file_path)
            else:
                # Clear all memory types for specific agent
                if agent_name in self.memory_cache["agent_memory"]:
                    self.memory_cache["agent_memory"][agent_name] = {}
                    agent_dir = os.path.join(self.agent_memory_dir, agent_name)
                    if os.path.exists(agent_dir):
                        for file_name in os.listdir(agent_dir):
                            os.remove(os.path.join(agent_dir, file_name))
        else:
            if memory_type:
                # Clear specific memory type for all agents
                for agent_name in self.memory_cache["agent_memory"]:
                    if memory_type in self.memory_cache["agent_memory"][agent_name]:
                        self.memory_cache["agent_memory"][agent_name][memory_type] = {}
                        file_path = os.path.join(self.agent_memory_dir, agent_name, f"{memory_type}.json")
                        if os.path.exists(file_path):
                            os.remove(file_path)
            else:
                # Clear all memories for all agents
                self.memory_cache["agent_memory"] = {}
                if os.path.exists(self.agent_memory_dir):
                    shutil.rmtree(self.agent_memory_dir)
                    os.makedirs(self.agent_memory_dir)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            Dict[str, Any]: Statistics about the memory system
        """
        stats = {
            "agent_memory": {},
            "shared_memory": {},
            "conversations": {
                "total": len(self.memory_cache["conversations"]),
                "oldest": None,
                "newest": None
            }
        }
        
        # Agent memory stats
        for agent_name, memory_types in self.memory_cache["agent_memory"].items():
            stats["agent_memory"][agent_name] = {
                "memory_types": list(memory_types.keys()),
                "size": sum(len(str(memory_data)) for memory_data in memory_types.values())
            }
        
        # Shared memory stats
        stats["shared_memory"] = {
            "memory_types": list(self.memory_cache["shared_memory"].keys()),
            "size": sum(len(str(memory_data)) for memory_data in self.memory_cache["shared_memory"].values())
        }
        
        # Conversation stats
        if self.memory_cache["conversations"]:
            timestamps = [conv.get("timestamp") for conv in self.memory_cache["conversations"].values() 
                         if "timestamp" in conv]
            if timestamps:
                stats["conversations"]["oldest"] = min(timestamps)
                stats["conversations"]["newest"] = max(timestamps)
        
        return stats

# Create a global instance of the memory manager
memory_manager = MemoryManager()

# Example usage
if __name__ == "__main__":
    # Test memory operations
    memory_manager.update_agent_memory(
        agent_name="molecular_agent",
        memory_type="molecular_knowledge",
        memory_data={"compounds": {"paclitaxel": {"solubility": "Poorly soluble in water, soluble in DMSO"}}}
    )
    
    # Retrieve the memory
    molecular_memory = memory_manager.get_agent_memory("molecular_agent")
    print(f"Molecular Agent Memory: {molecular_memory}")
    
    # Get memory statistics
    stats = memory_manager.get_memory_stats()
    print(f"Memory Statistics: {stats}")