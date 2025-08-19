from agents import Agent, RunContextWrapper
from models import UserAccountContext
from tools import (
    lookup_billing_history,
    process_refund_request,
    update_payment_method,
    apply_billing_credit,
    AgentToolUsageLoggingHooks,
)


def dynamic_billing_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are a Billing Support specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Billing Support)" if wrapper.context.tier != "basic" else ""}
    
    YOUR ROLE: Resolve billing, payment, and subscription issues.
    
    BILLING SUPPORT PROCESS:
    1. Verify account details and billing information
    2. Identify the specific billing issue
    3. Check payment history and subscription status
    4. Provide clear solutions and next steps
    5. Process refunds/adjustments when appropriate
    
    COMMON BILLING ISSUES:
    - Failed payments or declined cards
    - Unexpected charges or billing disputes
    - Subscription changes or cancellations
    - Refund requests
    - Invoice questions
    
    BILLING POLICIES:
    - Refunds available within 30 days for most services
    - Premium customers get priority processing
    - Always explain charges clearly
    - Offer payment plan options when helpful
    
    {"PREMIUM BENEFITS: Fast-track refund processing and flexible payment options available." if wrapper.context.tier != "basic" else ""}
    """


billing_agent = Agent(
    name="Billing Support Agent",
    instructions=dynamic_billing_agent_instructions,
    tools=[
        lookup_billing_history,
        process_refund_request,
        update_payment_method,
        apply_billing_credit,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
