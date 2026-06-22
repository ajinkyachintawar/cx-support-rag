import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

import httpx

QUESTIONS = [
    "How many days does a standard customer have to request a refund?",
    "What's the refund window for a premium tier customer?",
    "Customer's delivery is 5 days late, what do we offer?",
    "When does a case need to be escalated?",
    "Customer was charged twice for the same order, what's the precedent?",
    "Is phone number alone enough to verify a customer?",
    "What two pieces of ID do we need to verify a customer's identity?",
    "Who pays for return shipping if the customer changed their mind?",
    "What's our policy on price matching competitor websites?",
    "Can a customer transfer their premium subscription to a family member?",
    "Customer cancelling premium wants a refund for unused days, can we do that?",
    "A promo code didn't apply at checkout, what do I check?",
    "Customer in Europe says they were charged more than the USD price, is that a billing error?",
    "Delivery shows as delivered but customer says they never got it, what process?",
    "Order of 3 items arrived with only 2, how do I handle the missing one?",
    "Customer threatened to post on social media because of a delay, do I escalate?",
    "A premium customer is asking for a refund on day 35, what should I tell them?",
    "Customer asked us to delete their account mid-call about a late delivery, what do I do?",
    "International order stuck in customs for 12 days, does delivery delay compensation apply?",
    "What's the process for logging a complaint about product quality?",
]

BASE_URL = "http://localhost:8000"
CONCURRENCY = 20


async def send_query(client: httpx.AsyncClient, question: str) -> dict:
    start = time.perf_counter()
    try:
        response = await client.post(
            f"{BASE_URL}/query",
            json={"question": question},
            timeout=30.0,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        response.raise_for_status()
        data = response.json()
        return {"success": True, "latency_ms": latency_ms, "server_latency_ms": data.get("latency_ms", 0)}
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {"success": False, "latency_ms": latency_ms, "error": str(e)}


async def main():
    print(f"Load test: {CONCURRENCY} concurrent requests")
    print(f"Target: {BASE_URL}/query")
    print()

    async with httpx.AsyncClient() as client:
        tasks = [send_query(client, q) for q in QUESTIONS[:CONCURRENCY]]
        results = await asyncio.gather(*tasks)

    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    print(f"Results: {len(successes)} success, {len(failures)} failed")

    if successes:
        latencies = sorted(r["latency_ms"] for r in successes)
        server_latencies = sorted(r["server_latency_ms"] for r in successes)

        print(f"\nClient-side latency (includes network):")
        print(f"  p50:  {latencies[len(latencies) // 2]}ms")
        print(f"  p95:  {latencies[int(0.95 * len(latencies))]}ms")
        print(f"  p99:  {latencies[min(int(0.99 * len(latencies)), len(latencies) - 1)]}ms")
        print(f"  mean: {statistics.mean(latencies):.0f}ms")
        print(f"  max:  {max(latencies)}ms")

        print(f"\nServer-side latency:")
        print(f"  p50:  {server_latencies[len(server_latencies) // 2]}ms")
        print(f"  p95:  {server_latencies[int(0.95 * len(server_latencies))]}ms")
        print(f"  mean: {statistics.mean(server_latencies):.0f}ms")

    if failures:
        print(f"\nFailures:")
        for f in failures:
            print(f"  {f['error']}")


if __name__ == "__main__":
    asyncio.run(main())
