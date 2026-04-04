# Model Evaluation

Open WebUI provides a built-in evaluation system to help discover which AI model best suits your needs through direct interaction and rating.

## How It Works

- During chats, leave a thumbs up or down on responses. If the message has a sibling message (regenerated response or side-by-side model comparison), it contributes to your personal leaderboard.
- Whenever you rate a response, the system captures a snapshot of that conversation for future model fine-tuning.
- Leaderboards are accessible in the Admin section, ranked using an ELO rating system.

## Two Evaluation Modes

### 1. Arena Model

The Arena Model randomly selects from a pool of available models for unbiased evaluation.

How to use:
- Select a model from the Arena Model selector
- Use it normally - you're in "arena mode"
- For feedback to affect the leaderboard, you need a sibling message (alternative response from the same query)
- When you thumbs up one response, the other automatically gets a thumbs down
- Only upvote the message you believe is genuinely the best

### 2. Normal Interaction

Chat normally and rate responses with thumbs up/down. For feedback to affect the leaderboard, swap out the model and interact with a different one to create a sibling response for comparison. Only comparisons between two different models influence rankings.

## Leaderboard

Access via **Admin Panel**. Models are ranked using an ELO rating system.

### Model Activity Tracking

Click a model in the Leaderboard to view its activity chart:
- **Diverging Chart**: Shows wins (positive) and losses (negative) daily or weekly
- **Time Ranges**: 30 Days, 1 Year, or All Time
- **Weekly Aggregation**: For longer ranges, data is aggregated by week

### Tagging for Granular Insights

Rate chats and tag them by topic (e.g., customer service, creative writing, technical support) for domain-specific model comparison.

**Automatic Tagging:** Open WebUI tries to auto-tag chats based on conversation topic, but may sometimes fail. Best practice is to manually tag for accuracy.

Tags allow re-ranking models based on specific topics to find the best model for particular use cases.

## Chat Snapshots for Fine-Tuning

When you rate a model's response, Open WebUI captures a snapshot of the chat. These snapshots can be used to fine-tune models. (Feature actively being developed.)

## Summary

Two goals:
1. Easily compare models
2. Find the model that best fits your individual needs

All data stays on your instance. Nothing is shared unless you opt-in for community sharing.
