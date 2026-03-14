# Monetization Model

This document defines the pricing and monetization strategy for the Personal AI Assistant.

The application follows a **freemium SaaS model**.

Users can start for free and upgrade to unlock advanced capabilities.

---

# Pricing Strategy

Target pricing:

Premium plan: **10-15 EUR per month**

This price point balances:

* AI infrastructure costs
* perceived value
* market competitiveness

The assistant provides long-term personal value, making subscription pricing appropriate.

---

# Free Plan

The free plan allows users to try the assistant and experience its core value.

Included features:

Voice memory recording
Basic question answering
Limited memory storage
Limited monthly AI usage

Example limits:

100 memories
50 questions per month

Attachments may be limited or disabled.

# Premium Plan

The premium plan unlocks the full potential of the assistant.

Features:

Unlimited memories
Unlimited questions
Receipt photo attachments
Advanced dashboard insights
Priority AI processing

Price range:

10-15 EUR per month

Role-based exception:

- `admin` and `author` accounts are always `premium` and billing-exempt
- no subscription payment is charged for these privileged operational roles

Payment method management policy:

- regular `user` accounts can manage payment methods in settings (add/update, set default, remove)
- payment method data exposed to client must be masked
- `admin` and `author` cannot use self-service billing/payment-method flows

Churn management policy:

- cancellation flow must capture reason before final cancellation
- cancellation preview should offer retention alternatives (for example downgrade/pause)
- churn reasons must be tracked for pricing/product iteration
- proactive churn-risk scoring may trigger pre-cancel retention offers

---

# AI Cost Control

To maintain sustainable margins, the system implements several safeguards.

Examples:

Rate limits on free users
Efficient database-first queries
Vector search for memory retrieval
Optimized AI pipeline

AI is used only when necessary.

---

# Business Tier (Future)

A future business plan may support professional users.

Potential features:

Team accounts
Shared knowledge base
Advanced analytics
Higher API limits

Example pricing:

25-40 EUR per user per month

---

# Growth Strategy

User growth is expected through:

word-of-mouth
product utility
viral discovery

The assistant becomes more valuable as users accumulate memories over time.

This increases long-term retention.

---

# Long-Term Revenue Opportunities

Future monetization options include:

Advanced analytics packages
Business integrations
Custom AI models
Professional productivity features

---

# Key Principle

The assistant must provide **continuous value** to justify subscription pricing.

The product should feel like a:

personal memory system
life organizer
knowledge assistant
