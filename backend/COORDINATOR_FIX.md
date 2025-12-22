# Quick Fix for Coordinator Agent

## Problem
LLM is calling `calculate_risk_score` with empty parameters and returning confidence as string instead of integer.

## Solution
Update coordinator prompt to:
1. Show exact example of how to call the tool
2. Fix JSON format to use integer for confidence

## Files to Update
- `backend/agents/coordinator_agent.py` - lines 102-120 (sync) and 280-298 (async)
