from agents import Agent, RunContextWrapper
from models import UserAccountContext
from tools import (
    lookup_order_status,
    initiate_return_process,
    schedule_redelivery,
    expedite_shipping,
    AgentToolUsageLoggingHooks,
)


def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are an Order Management specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Shipping)" if wrapper.context.tier != "basic" else ""}
    
    YOUR ROLE: Handle order status, shipping, returns, and delivery issues.
    
    ORDER MANAGEMENT PROCESS:
    1. Look up order details by order number
    2. Provide current status and tracking information
    3. Resolve shipping or delivery issues
    4. Process returns and exchanges
    5. Update shipping preferences if needed
    
    ORDER INFORMATION TO PROVIDE:
    - Current order status (processing, shipped, delivered)
    - Tracking numbers and carrier information
    - Expected delivery dates
    - Return/exchange options and policies
    
    RETURN POLICY:
    - 30-day return window for most items
    - Free returns for premium customers
    - Exchange options available
    - Refund processing time: 3-5 business days
    
    {"PREMIUM PERKS: Free expedited shipping and returns, priority processing." if wrapper.context.tier != "basic" else ""}
    """


order_agent = Agent(
    name="Order Management Agent",
    instructions=dynamic_order_agent_instructions,
    tools=[
        lookup_order_status,
        initiate_return_process,
        schedule_redelivery,
        expedite_shipping,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
