# Problem Research Document
## RFP Response Automation: Understanding the Problem Before Building the Solution

**Author:** Sunidhi Mishra  
**Project:** RFP Match POC  
**Research Type:** Secondary research and analogical reasoning from adjacent domain primary data

---

## Executive Summary

This document explains the real-world problem that the RFP Match prototype was built to address.

When a big company wants to buy software, they send a long list of questions (called an RFP) to multiple software vendors. Someone at each vendor company has to answer all those questions, usually under a tight deadline. Most of those questions have been answered before. But those old answers are scattered across emails, shared folders, and Slack messages, and nobody can find them quickly.

So people end up wasting hours searching for answers they already wrote, instead of doing anything more useful.

The tools that exist today to solve this problem store answers in one place but do not tell you how much to trust each suggested answer. That is the gap this prototype tests.

There is also a deeper problem underneath: even a well-organized library of answers only contains what someone formally wrote down. But many important commitments get made in phone calls, email threads, and meetings, and those never get recorded anywhere. So the library slowly drifts away from reality without anyone noticing.

This document covers the evidence behind both problems and explains how that research shaped the design decisions in the prototype.

---

## Table of Contents

1. [The User and Their World](#1-the-user-and-their-world)
2. [The Scale of the Problem](#2-the-scale-of-the-problem)
3. [Why Existing Solutions Do Not Fully Solve It](#3-why-existing-solutions-do-not-fully-solve-it)
4. [The Deeper Problem Underneath](#4-the-deeper-problem-underneath)
5. [What This Means for Product Direction](#5-what-this-means-for-product-direction)
6. [Research Basis and Limitations](#6-research-basis-and-limitations)

---

## 1. The User and Their World

### What is an RFP and Why Does It Matter?

When a large organization, say a hospital chain or a bank, wants to buy new software, they do not just pick one and purchase it. Instead, they create a formal document with 50 to 150 detailed questions and send it to 10 to 15 different software companies at the same time. This document is called a **Request for Proposal**, or RFP.

Each vendor that receives this document must answer every question accurately and send it back, usually within 5 to 7 business days. The buyer then compares all the responses and decides which vendor to buy from.

The questions cover things like:
- Is your software secure? Do you have the right certifications?
- Which other tools does your software connect with?
- How long does it take to set up?
- How much does it cost?
- Can you share examples of similar customers you have worked with?

These are serious, high-stakes questions. A wrong or incomplete answer can cost a company the deal.

### Who Has to Answer These Questions?

The person responsible for answering most of these questions is usually called a **Solutions Consultant** or a **Sales Engineer**. Think of them as the bridge between the sales team and the technical team. When a prospect asks a hard question, this person is the one who has to answer it.

They are typically skilled, experienced professionals who understand both the product and the customer's needs. They are also always busy. RFPs are one of their biggest recurring time drains.

### What Their Day Actually Looks Like During an RFP

Here is a realistic picture of what happens when an RFP lands in someone's inbox.

An RFP arrives on a Monday morning with a Friday deadline. It has 94 questions.

The Solutions Consultant goes through the list. About 20 questions they can answer from memory right away. About 15 need to go to the legal or finance team. That leaves around 60 questions they need to look up.

For each of those 60 questions, the current process looks like this:

1. Open the company's shared Google Drive folder (usually named something like "RFP Responses Archive")
2. Open 3 to 4 documents that look relevant
3. Search within those documents for related keywords
4. Find something close to what they need, read it carefully, and decide if it is still accurate
5. Copy it, update it manually, and move on to the next question

This takes 15 to 25 minutes per question. For 60 questions, that is 15 to 25 hours of work across the 5-day window. That is most of their working week, every single time an RFP arrives.

### What Real Users Say About This Problem

The following observations are drawn from publicly available reviews on G2, Glassdoor, and discussions in pre-sales professional communities online. These are not invented. They reflect a pattern seen consistently across many different companies and roles.

> "We have answers scattered across 12 different Google Docs. Nobody knows which one is the official version."

> "Half my time on RFPs is just trying to find answers we have already written. It is the same 30 questions every time."

> "The AI suggestions our tool gives are hit or miss. I can never tell if it is a strong match or a weak one. It just shows me something and I have to guess."

> "I sent a stale answer once about our data residency policy. We had changed our EU data storage region six months earlier. It killed the deal."

These are not complaints about bad tools or lazy people. They reflect a structural problem in how most organizations manage their RFP knowledge.

---

## 2. The Scale of the Problem

### The Time Cost

Let us put a rough number on this.

If a Solutions Consultant handles 35 RFPs per quarter, with about 60 questions per RFP requiring retrieval, and each question takes around 20 minutes on average to search and retrieve, that comes out to roughly **700 hours per quarter** spent just searching for answers that already exist somewhere.

At a typical fully-loaded cost of $50 to $80 per hour for a mid-senior pre-sales professional, this represents roughly **$35,000 to $56,000 per quarter per person** in search overhead alone. This does not include the opportunity cost of not being available for active deals during that time.

**These are illustrative estimates** based on publicly available pre-sales compensation data and community-sourced time-per-question figures. They are directional, not audited. The actual numbers will vary by company, team size, and RFP volume.

### The Accuracy Cost

Time is the visible cost. Accuracy is the hidden one.

When someone searches manually across fragmented files, they make a judgment call on every answer: is this the right version, is it still accurate, does it apply to this specific prospect? Under time pressure, that judgment gets rushed.

The most common failure mode is not sending a deliberately wrong answer. It is sending an answer that was accurate when it was written but was never updated after something changed. A product feature got deprecated. A certification got renewed and its scope expanded. A data storage policy changed. Nobody updated the document.

The consequences range from awkward follow-up questions from prospects, to losing a deal when a procurement team loses confidence in the vendor's credibility, to legal exposure when a committed capability turns out to not actually be available.

### The Consistency Cost

When multiple Solutions Consultants work on different sections of the same RFP, or when the same question gets answered differently across RFPs sent to different prospects at the same time, that inconsistency creates risk.

A procurement team comparing vendor responses carefully will notice when the same vendor gives different answers to the same question across different rounds of evaluation. No tool in the current market explicitly tracks or addresses this cross-person, cross-RFP consistency problem.

---

## 3. Why Existing Solutions Do Not Fully Solve It

Five well-established tools address the RFP response problem today:

- **Loopio** (founded 2014)
- **Responsive**, formerly known as RFPIO (founded 2015, raised $180M, valued at over $1.8 billion)
- **Ombud** (founded 2016)
- **QorusDocs** (founded 2012)
- **Proposify** (founded 2013)

All five solve the basic organization problem. They store your company's answers in one central place so your team is not searching through scattered email threads and shared folders. This is genuinely useful and the reason these companies exist and have large customer bases.

But all five have the same gaps:

### Gap 1: No Honest Confidence Signal

Every tool shows answer suggestions. None of them tell the user how confident to be in each suggestion.

A match that is 95% similar to the incoming question and a match that is 60% similar look identical in every one of these tools. They both appear as suggestions. The user has to decide how much to trust each one with no explicit signal to guide them.

Under time pressure, most users default to accepting the top suggestion regardless. That is the behavior that produces inaccurate RFP responses. The tools are optimized for convenience over trustworthiness.

### Gap 2: No Independent Staleness Signal

Match quality and answer freshness are completely different things.

A tool can return a highly similar match on an answer that was last updated two years ago. None of the five tools surface staleness as a signal independent of match quality. They do not tell you that the answer you are looking at might be outdated, even when they are fairly confident it matches your question.

A high-confidence match on a stale answer is more dangerous than a low-confidence match on a current one. No existing tool makes this distinction visible to the user.

### Gap 3: AI Was Added Later, Not Built In From the Start

Every competitor in this space was built on document management and workflow logic first. AI was added later as a feature on top of an existing product.

The matching is often based on keyword similarity rather than meaning. This means that paraphrased questions do not always match reliably. "Do you support SSO?" and "Is SAML authentication available?" are asking the same thing, but a keyword-based system may not recognize that.

### Gap 4: No Learning from Usage

When a user accepts or rejects a suggested answer, that action does not improve future suggestions in any of these tools. The system stays the same regardless of how the team uses it. There is no mechanism for the tool to get smarter over time.

### Gap 5: No Autonomous Handling

All five tools require a human to make every decision. There is no tier of answers the system is trusted to handle on its own. Every suggestion still requires a human to review, accept, and send. The tools reduce search time but do not reduce the total number of human decisions required.

---

## 4. The Deeper Problem Underneath

The gaps described in Section 3 are real and worth solving. But there is a deeper structural problem that sits underneath all of them.

### The Filing Metric vs. the Management Metric

This distinction comes from **Sanchita Sur**, the founder of Emplay Inc., whose published research covers 500 enterprise contracts across Tech, Telecom, IT, and Energy sectors.

Her observation, drawn from post-award contract management but directly applicable to RFP knowledge bases:

A knowledge base is a **filing metric**, not a **management metric**.

What does that mean?

A filing metric tells you what has been formally recorded. A management metric tells you what is actually happening in reality.

Every company knows how many answers they have saved in their knowledge base. Almost none know how many commitments they have made to customers that their knowledge base does not actually reflect.

These two numbers are almost never the same. And the gap between them is where the real risk lives.

### The Capture Gap: Why the Library Drifts Away from Reality

Sanchita's research found that fewer than 3 in 10 post-award obligation changes are ever formally recorded in any system. The rest live in Slack messages, email threads, phone calls, and verbal conversations in meetings.

Nobody lied. Nobody failed. The process simply was not designed to capture what happens in informal channels.

**The same failure exists in the RFP response workflow, one stage earlier.**

Here are three examples of how it happens:

- A Solutions Consultant commits to a custom implementation timeline on a discovery call. The knowledge base still shows the standard timeline.
- A Sales Engineer confirms a product capability over email that was actually deprecated six months ago. The knowledge base was never updated.
- A VP of Sales says in a presentation "we can probably make that work." Nobody captures what "that" was, or whether it was actually delivered.

Each of these informal commitments becomes a contract obligation when the deal closes. At that point, the knowledge base and the actual real-world commitment are already different, and nobody knows it until something goes wrong.

This is what Sanchita calls the **Capture Gap**: the space between what is documented and what is actually true.

WorldCC, a globally recognized authority on commercial and contract management, estimates that organizations lose 11% of contract value annually to untracked obligation drift. On a $400 million supplier portfolio, that is $44 million leaving through gaps that appear on nobody's dashboard. This figure comes from Sanchita's published content referencing WorldCC research, applied here to illustrate the scale of the underlying problem.

### Why Ownership Failure Causes the Capture Gap

The capture gap is not caused by careless people. It is caused by a structural ownership failure.

Before a contract is signed, ownership is clear. The Solutions Consultant owns the formal RFP response. Legal reviews compliance answers. Finance approves pricing commitments. Everyone knows their role.

The moment the contract is signed, those owners move on to the next deal. Nobody inherits the responsibility for tracking what happens to those commitments in the weeks and months that follow.

The process was built for the pre-signing stage. It was never designed to handle the informal agreements that accumulate after.

The fix is not a better tool. It is a decision about who owns each commitment, at every stage, and what happens when that commitment changes in a conversation nobody formally recorded.

### What This Means for a Retrieval System

A retrieval system can only surface what has been captured. If the capture rate is around 30%, meaning 70% of real operative commitments never reach the knowledge base, then a retrieval system returning confident answers from that 30% is solving an incomplete version of the problem.

This is not an argument against building retrieval tools. It is an argument for being precise about what retrieval solves and what it does not.

The RFP Match prototype addresses the retrieval layer. It does not address the capture layer. That boundary is stated clearly throughout the project documentation, not hidden or minimized.

---

## 5. What This Means for Product Direction

The research above directly shaped four specific design decisions in the prototype.

### Decision 1: Focus on Retrieval, Not Generation

The problem is finding existing answers, not writing new ones. AI-generated RFP responses without a grounded knowledge base produce made-up answers, which is worse than no tool at all. The prototype tests whether semantic search can make retrieval fast, reliable, and trustworthy.

### Decision 2: Make Confidence Explicit and Tiered

The research showed that the existing market's failure is not retrieval quality. It is retrieval trust. Users cannot tell how much to believe each suggestion. The prototype addresses this directly by assigning every result one of three explicit labels: Auto-Answer (high confidence), Review Required (medium confidence), or Escalate to SME (low confidence). The user always knows what the system thinks and what action is recommended.

### Decision 3: Separate Staleness from Confidence

The stale answer failure mode appears consistently in community discussions about RFP tool failures. A high-confidence match on an outdated entry is more dangerous than a low-confidence match on a current one. The prototype separates these two signals explicitly. Every result card shows both a confidence score and an independent staleness flag, so the user can see both dimensions at once.

### Decision 4: Name the Capture Gap Rather Than Pretend It Does Not Exist

The research makes clear that a retrieval system operating on a formally documented knowledge base is solving one layer of a multi-layer problem. The prototype does not claim to solve the capture gap. It names it explicitly as the harder, unsolved problem that sits underneath the retrieval mechanism. This is the most important product honesty decision in the project. A tool that overpromises what it can do is less useful than one that is clear about its own limits.

---

## 6. Research Basis and Limitations

### What This Research Is

This document is based entirely on secondary research and analogical reasoning. It draws from:

- Publicly available practitioner reviews on G2 and Glassdoor
- Discussions in pre-sales and solutions engineering professional communities
- Published research insights from Sanchita Sur, Founder of Emplay Inc., based on her primary data from 500 enterprise contracts
- WorldCC research cited in Sanchita Sur's published content
- Publicly available information about competitor tools and their feature sets

The WorldCC figure about contract value loss (11% annually) is applied here by analogy to the pre-award RFP context. It was not measured directly for the RFP response workflow.

The time-per-question estimates (15 to 25 minutes in retrieval mode) are drawn from aggregated community discussions. They are directional estimates, not empirically measured in a controlled study.

### What This Research Is Not

This is not a primary research study. No Solutions Consultants or Sales Engineers were interviewed directly. No workflow observations were conducted in a real sales environment. No A/B test compared task completion time with and without a retrieval tool.

The research establishes that the problem is real and that the mechanism being tested addresses a genuine gap in the market. It does not establish that the specific design choices made in the prototype are the optimal ones for a real user population.

### What Primary Research Would Look Like Next

The most valuable next step before building further: three to five structured interviews with active Solutions Consultants at mid-market B2B SaaS companies.

Key questions to answer:
- How long does retrieval actually take per question in practice, on a real RFP with real time pressure?
- What percentage of questions are genuinely recurring versus genuinely novel?
- How often do you send an answer you are not fully confident in, and what stops you from verifying it further?
- What would you need to see from a system before you trusted it to suggest an answer without you reviewing it first?

Those interviews would either confirm the assumptions in this document or surface the specific ways they are wrong. Both outcomes are equally useful before committing to a production build.

---

*This document is part of the RFP Match POC project documentation. For the full set of artifacts, see the project repository and linked documents.*