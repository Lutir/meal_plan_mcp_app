"""
Base classes for the Grocery App Agent System
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class AgentStatus(Enum):
    """Status of an agent during execution"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING_FOR_HANDOFF = "waiting_for_handoff"


@dataclass
class AgentContext:
    """Context shared between agents"""
    user_id: str = "default"
    session_id: str = "default"
    inventory: List[Dict] = field(default_factory=list)
    meal_plan: Dict = field(default_factory=dict)
    shopping_list: List[Dict] = field(default_factory=list)
    preferences: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    data: Any
    message: str
    next_agent: Optional[str] = None
    context_updates: Dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.context: Optional[AgentContext] = None
        self.tools: List[Any] = []
        
    @abstractmethod
    async def execute(self, context: AgentContext, **kwargs) -> AgentResult:
        """Execute the agent's main logic"""
        pass
    
    def add_tool(self, tool: Any):
        """Add a tool to the agent"""
        self.tools.append(tool)
    
    def update_context(self, context: AgentContext, updates: Dict):
        """Update the shared context with new data"""
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                context.metadata[key] = value
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message from the agent"""
        print(f"[{self.name}] {level}: {message}")
    
    def get_status(self) -> Dict:
        """Get current status of the agent"""
        return {
            "name": self.name,
            "status": self.status.value,
            "description": self.description,
            "tools_count": len(self.tools)
        }


class AgentOrchestrator:
    """Orchestrates the execution of multiple agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_order: List[str] = []
        self.context: AgentContext = AgentContext()
        
    def add_agent(self, agent: BaseAgent, position: Optional[int] = None):
        """Add an agent to the orchestrator"""
        self.agents[agent.name] = agent
        if position is not None:
            self.execution_order.insert(position, agent.name)
        else:
            self.execution_order.append(agent.name)
    
    def set_execution_order(self, order: List[str]):
        """Set the order in which agents should execute"""
        self.execution_order = order
    
    async def execute_workflow(self, initial_context: Optional[AgentContext] = None) -> Dict:
        """Execute all agents in the specified order"""
        if initial_context:
            self.context = initial_context
        
        results = {}
        
        for agent_name in self.execution_order:
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not found")
            
            agent = self.agents[agent_name]
            agent.context = self.context
            
            try:
                agent.status = AgentStatus.RUNNING
                agent.log(f"Starting execution")
                
                result = await agent.execute(self.context)
                results[agent_name] = result
                
                if result.success:
                    agent.status = AgentStatus.COMPLETED
                    agent.log(f"Completed successfully: {result.message}")
                    
                    # Update context with result data
                    if result.context_updates:
                        agent.update_context(self.context, result.context_updates)
                    
                    # Check if we should handoff to another agent
                    if result.next_agent and result.next_agent in self.agents:
                        agent.log(f"Handing off to {result.next_agent}")
                        agent.status = AgentStatus.WAITING_FOR_HANDOFF
                else:
                    agent.status = AgentStatus.ERROR
                    agent.log(f"Failed: {result.message}")
                    break
                    
            except Exception as e:
                agent.status = AgentStatus.ERROR
                agent.log(f"Error during execution: {str(e)}")
                results[agent_name] = AgentResult(
                    success=False,
                    data=None,
                    message=f"Error: {str(e)}"
                )
                break
        
        return {
            "results": results,
            "final_context": self.context,
            "success": all(r.success for r in results.values() if r)
        }
    
    def get_workflow_status(self) -> Dict:
        """Get status of all agents in the workflow"""
        return {
            "agents": {name: agent.get_status() for name, agent in self.agents.items()},
            "execution_order": self.execution_order,
            "context": {
                "inventory_count": len(self.context.inventory),
                "meal_plan_days": len(self.context.meal_plan),
                "shopping_list_count": len(self.context.shopping_list)
            }
        } 