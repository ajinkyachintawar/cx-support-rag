import pytest


@pytest.fixture
def sample_docs():
    return [
        {"id": "1", "source": "refund_policy_standard.md", "content": "Standard refund is 14 days.", "score": 0.9},
        {"id": "2", "source": "refund_policy_premium.md", "content": "Premium refund is 30 days. REF-PREM-030.", "score": 0.85},
        {"id": "3", "source": "delivery_delay_process.md", "content": "Delivery delays over 3 days get $10 credit.", "score": 0.7},
        {"id": "4", "source": "lost_package_process.md", "content": "Lost packages get immediate reshipment.", "score": 0.6},
        {"id": "5", "source": "escalation_rules.md", "content": "Escalate for legal action or regulatory complaints.", "score": 0.5},
    ]
