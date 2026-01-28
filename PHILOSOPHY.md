# 🧠 The Philosophy: How to Think Like a Principal AI Engineer

> "Code is a liability. Functionality is an asset."

This document outlines the **Mental Models** required to succeed in this course and in your career.

## 1. Production > Proof of Concept
A Jupyter Notebook is a scratchpad, not a product.
- **Academic:** "It achieved 98% accuracy on the test set."
- **Production:** "It handles 50 concurrent requests with <200ms latency, retries on 5xx errors, and costs $0.002 per transaction."

## 2. The "Simple vs. Easy" Tradeoff
We prefer **Simple** (easy to reason about) over **Easy** (quick to write).
- **Don't** blindly chain 50 LangChain primitives.
- **Do** write a clean Python function that calls the LLM APIs directly if it's clearer.

## 3. Fail Loudly, Recover Gracefully
AI is non-deterministic. It *will* hallucinate. APIs *will* timeout.
- **Always** validate outputs (Pydantic).
- **Always** implement retries with functional backoff.
- **Always** have a fallback (e.g., if semantic search fails, fall back to keyword search).

## 4. Observability is Not Optional
If you can't trace <u>why</u> the bot gave that answer, you haven't built a system—you've built a black box.
- We log inputs, outputs, tokens, latency, and cost for **every** interaction.

## 5. Cost Awareness
An Engineer who doesn't know the cost of their system is dangerous.
- **Know your unit economics:** "This feature costs $0.05 per user per day."
- Design for the cheapest model that gets the job done.

## 6. The "Buy vs. Build" Rationale
- **Don't** build your own Vector DB unless you are Pinecone.
- **Don't** train your own foundation model unless you have $10M+.
- **Do** build the orchestration layer, the business logic, and the evaluation pipeline.

---
**Keep these principles in mind as you move through the Blocks.**
