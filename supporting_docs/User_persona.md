# User Personas
## The Two Roles This Prototype Was Designed Around

**Author:** Sunidhi Mishra  
**Project:** RFP Match POC

---

## Executive Summary

This document describes the two specific people this prototype was designed for, and why understanding their actual day-to-day work shaped every design decision in the system.

The first is a Solutions Consultant, the primary user who searches the answer library and sends responses to incoming RFP questions. Their main recurring task is answering detailed questionnaires from potential customers, and most of their time on this task is spent searching for answers their company has already written before, rather than writing anything new. What this person needs is not a tool that makes decisions for them, but one that removes the time spent searching, so they can spend their time reviewing instead.

The second is a Security and Compliance Lead, the person who owns and maintains the answers the first person depends on. Their job is not to search the library, but to keep it accurate before anyone else ever has to rely on it. This role surfaced directly from a real gap discovered while testing this prototype, not from external research, and understanding it shaped a specific decision about how ownership and staleness should work.

The rest of this document covers both people in full: who they are, what their actual workday looks like, what they need from a system like this, and how each of them shaped the prototype's design.

---

## Table of Contents

1. Persona One: Arjun Mehta
2. Persona Two: Meera Iyer
3. Sourcing Notes

---

## 1. Persona One: Arjun Mehta

### Overview

**Name used for this document:** Arjun Mehta (a representative name, not a real individual)

**Role:** Solutions Consultant, sometimes called a Sales Engineer

**Company type:** Mid-market to enterprise business software company

**Team:** Sits between the sales team and the technical product team

**Experience level:** Three to six years in a similar role

**Reports to:** Head of Pre-Sales or VP of Sales

### What This Person Actually Does

When a potential customer asks a difficult, technical question during the sales process, whether about security, integrations, implementation, or compliance, the salesperson working the deal brings this person in. Their job is to give an accurate, credible answer quickly enough to keep the deal moving forward.

Answering formal Requests for Proposal is their single most time-consuming recurring task. A typical company at this size receives 25 to 40 of these documents every quarter, each containing 50 to 150 individual questions. This person is directly responsible for 60 to 80 percent of those questions, mainly the technical, security, and compliance-related ones. The remaining questions get routed to legal or finance.

### A Realistic Day During a Busy Period

Here is what a typical stretch of work looks like when one of these documents arrives.

A new set of questions arrives with a five-day deadline. There are 94 questions in total.

This person goes through the list. About 20 questions they can answer immediately from memory. About 15 need to be sent to legal or finance. That leaves roughly 60 questions that require looking something up.

For each of those 60 questions, here is what actually happens right now:

1. Open the company's shared folder where past answers are stored
2. Open three or four documents that seem related
3. Search within those documents for anything close to the current question
4. Find something that looks right, read it carefully, and decide whether it is still accurate
5. Copy it, make any needed updates, and move to the next question

This takes 15 to 25 minutes per question. Across 60 questions, that adds up to 15 to 25 hours of work within a single five-day window. That is the majority of this person's working week, and it happens every single time a new document arrives.

### What They Care About Most

**Speed.** Every hour spent searching for old answers is an hour not spent talking to an active customer or closing a deal. This work feels like overhead, even though it is necessary.

**Accuracy.** Sending wrong information is costly. If this person says the company holds a certain security certification and that certification has actually lapsed, the deal can fall apart, and their own credibility takes the hit.

**Not becoming the bottleneck.** When a question needs to go to legal or another team, this person dislikes having to chase people down for an answer. They want to minimize how often that happens.

**Knowing when to trust an old answer.** When they find something that looks close to what they need, their biggest source of anxiety is not knowing whether it is still accurate. They would much rather see a clear signal that says an answer might be outdated and should be checked, than find out something was wrong after it has already been sent.

### Frustrations, in Their Own Words

The quotes below are drawn from publicly available reviews on G2 and Glassdoor, along with discussions in online communities for pre-sales and solutions engineering professionals. These reflect a consistent, widely shared pattern rather than a single individual's experience.

> "We have answers scattered across 12 different documents. Nobody knows which one is the official version."

> "Half my time on these documents is just trying to find answers we have already written before. It is the same 30 questions every time."

> "The AI suggestions our current tool gives are hit or miss. I can never tell if it is a strong match or a weak one. It just shows me something and I have to guess."

> "I sent an outdated answer once about our data storage policy. We had actually changed it six months earlier. It killed the deal."

### What a Better Tool Would Actually Change

A better tool does not need to replace this person's judgment. It needs to remove the time spent searching, so their judgment gets applied where it actually matters, which is reviewing an answer rather than hunting for one.

For the 40 to 50 questions in a typical document that are standard and recurring, this person should be able to spend 30 seconds confirming a suggested answer rather than 20 minutes finding it themselves. For the 10 to 15 questions that are genuinely new or unusual, the tool should say clearly that no reliable answer exists yet, and point them toward the right person to ask. They should never have to wonder whether they simply missed something buried in an old folder.

The most important thing the tool can offer is not the search itself, since every existing tool already searches. It is a clear, honest signal about how much to trust each result. That signal is what actually changes how this person works day to day.

### Why This Person Is the Right Focus

This person is not a developer, and they are not a procurement specialist. They are a knowledgeable, time-pressured professional who has to make a fast, high-stakes call, whether to use a suggested answer or not, with the right information available to make that call confidently.

Designing for this person specifically means the interface has to be fast, the confidence signal has to be understandable at a glance without needing an explanation, and the path to escalate a difficult question has to be obvious. Every design choice in the prototype's interface was made with this person's actual moment of decision in mind, not a general or abstract user.

---

## 2. Persona Two: Meera Iyer

### Overview

**Name used for this document:** Meera Iyer (a representative name, not a real individual)

**Role:** Security and Compliance Lead

**Company type:** Same mid-market to enterprise business software company as Arjun

**Team:** Owns the accuracy of every security and compliance answer in the shared archive

**Relationship to the first persona:** She does not search the archive or answer live RFP questions. Her job is to keep the answers accurate before anyone else has to rely on them.

### What This Person Actually Does

Every answer in the knowledge base is assigned to a team responsible for it. For the security and compliance category specifically, that responsibility sits with this person. When a new answer is written, she reviews it, confirms it is accurate, and signs off on it. Each answer is also given a review date, a point in the future when someone is supposed to come back and confirm the answer still holds.

That second part, the ongoing review, is where the actual problem shows up.

### A Realistic Scenario, Grounded in What Actually Happened

Unlike the scenario above, this one is not drawn from outside research. It is based on something that happened directly during the testing of this prototype.

When the security and compliance answers were first written, this person reviewed and signed off on every one of them. She was confident they were accurate and complete, and review dates were set for each entry so someone would come back and check later.

She trusts that an answer stays reliable once it has been signed off, unless something actively tells her otherwise. Ownership, as the system is currently built, means her name or her team's name is attached to the answer. It does not mean anything notifies her when that answer's review date actually arrives.

Two years pass. Nobody ever returns to update the review dates. When the system was actually tested during this project's own development, every single one of the 30 answers in the archive, including every one this person was responsible for, had silently crossed its review deadline. Nothing had alerted her at any point. She had been accountable for these answers the entire time, but had no way of knowing anything had gone stale until someone else went looking and found it.

### What They Care About Most

**Being told, not expected to remember.** Her responsibility is real, but the system currently has no way to actively remind her when something needs attention. She only finds out an answer is overdue for review if someone else happens to notice.

**Accuracy under her own name.** If an outdated security answer goes out and turns out to be wrong, the accountability traces back to her team, even if she was never told the answer had gone stale.

**Not being the invisible bottleneck.** She is not in the RFP conversation at all until something breaks. By the time a stale answer becomes visible, it has usually already been sent.

### What a Better System Would Actually Change

The fix here is not asking this person to be more diligent. She was diligent, she reviewed and signed off on every answer when it was written. The fix is a system that proactively notifies her, and whoever else owns a category of answers, when a review date is approaching or has passed, rather than relying on someone remembering to go check.

It would also mean assigning ownership to a specific named individual rather than a team name sitting on a record. A team name does not receive a notification. A person does.

### Why This Person Matters to the Design

This persona is not a nice-to-have addition. It represents the other half of why a retrieval system like this can quietly become untrustworthy over time. The prototype's own knowledge base went stale in exactly the way described above, entirely because ownership existed on paper without any active mechanism behind it. Designing only for Arjun, the person who searches, without also designing for the person who is supposed to keep the answers current, leaves the system vulnerable to decaying in exactly this way.

---

## 3. Sourcing Notes

**Arjun Mehta** is built from secondary research, not from direct interviews. It draws from publicly available reviews on G2 and Glassdoor, discussions in online pre-sales and solutions engineering communities, and general industry knowledge about how Requests for Proposal are handled at mid-market and enterprise software companies. No real individual named Arjun Mehta exists.

**Meera Iyer** is built differently. Rather than external research, this persona is grounded in a real incident that occurred during this project's own testing process, the discovery that every entry in the knowledge base had silently gone stale because ownership existed only as a passive label with no active review trigger behind it. No real individual named Meera Iyer exists. The name represents whichever team or person would be accountable for a given category of answers in a real deployment.

Neither persona has been validated through direct conversations with real Solutions Consultants or real knowledge base owners. The most valuable next step, if this project continued, would be a small number of short conversations with people currently in roles like these, to confirm or correct the assumptions described here.

---

*This document is part of the RFP Match POC project documentation. For the full evidence behind why this problem matters, see the Problem Research Document. For the full product overview, see the PRD.*