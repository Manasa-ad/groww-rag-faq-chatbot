"""Quick sanity test of route_query() against the canonical question types + guardrails."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import app as appmod

facts = appmod.load_facts.__wrapped__()
index = appmod.load_index.__wrapped__()

tests = [
    "What is the expense ratio of Groww Large Cap Fund?",
    "What is the exit load for the ELSS fund?",
    "What is the minimum SIP for the liquid fund?",
    "What is the ELSS lock-in?",
    "What is the lock-in for the large cap fund?",
    "What is the riskometer for the multicap fund?",
    "What is the benchmark of the liquid fund?",
    "What is the expense ratio of the multicap fund?",
    "How do I download my capital gains statement?",
    "Should I buy the ELSS fund or the large cap fund?",
    "Which fund is better, large cap or multicap?",
    "My PAN is ABCDE1234F, can you check my portfolio?",
    "My phone number is 9876543210, call me back",
    "What is quantum computing?",
]

for q in tests:
    print("=" * 90)
    print("Q:", q)
    print("A:", appmod.route_query(q, facts, index))
