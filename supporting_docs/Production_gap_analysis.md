# Production Gap Analysis
## RFP Match: What a Real Production System Would Require

**Author:** Sunidhi Mishra  
**Project:** RFP Match POC  
**Purpose:** An honest accounting of what this prototype does not solve, and what building it into a real product would actually take

---

## Executive Summary

This document lists everything the RFP Match prototype does not do, and explains what a real, production-ready version would need to add.

This prototype proves that a search tool can reliably find existing answers to RFP questions and tell you how much to trust each match. That part works, and it was tested carefully.

But a working demo and a real product are very different things. A real version would need to handle messy PDF documents instead of clean typed text, keep its answer library from going stale automatically, learn from how people actually use it, work for many different companies at once without their data mixing together, and take enterprise data security seriously instead of relying on made-up test data.

The single biggest gap, and the hardest one to solve, is that this prototype's answer library only contains what someone formally wrote down. Many real commitments made during a sales call or in an email never get written down anywhere. A retrieval tool, no matter how good, can only find what has actually been captured. Fixing that is a much bigger problem than building a better search tool, though this document sketches a possible first direction for what a minimal fix could look like.

Data security is the other area covered in real depth here, including a staged way of thinking about it, from safe early testing through to full production use, and an open question about whether running the AI model inside a customer's own systems could remove the trust problem almost entirely.

This document walks through each gap honestly, explains why it matters, and describes what a real fix would look like.

---

## Table of Contents

1. [Why This Document Exists](#1-why-this-document-exists)
2. [Gap: The Answer Library Only Reflects What Was Written Down](#2-gap-the-answer-library-only-reflects-what-was-written-down)
3. [Gap: No PDF Intake](#3-gap-no-pdf-intake)
4. [Gap: No Feedback Loop](#4-gap-no-feedback-loop)
5. [Gap: The Library Cannot Stay Current on Its Own](#5-gap-the-library-cannot-stay-current-on-its-own)
6. [Gap: No Support for Multiple Companies](#6-gap-no-support-for-multiple-companies)
7. [Gap: No Way to Edit an Answer Before Sending It](#7-gap-no-way-to-edit-an-answer-before-sending-it)
8. [Gap: Real Enterprise Data Security](#8-gap-real-enterprise-data-security)
9. [Gap: Handling Real, Messy Knowledge Bases](#9-gap-handling-real-messy-knowledge-bases)
10. [Gap: Trust Erosion Over Time](#10-gap-trust-erosion-over-time)
11. [What Would Come First](#11-what-would-come-first)

---

## 1. Why This Document Exists

Every prototype has limits. The honest and useful thing to do is name them clearly rather than let someone discover them later, or worse, assume the prototype does more than it actually does.

This document is organized around a simple question for each gap: what does this prototype not solve, why does that matter in the real world, and what would actually need to be built to solve it.

Some of these gaps were obvious from the start of the project. Others were discovered while testing the prototype and thinking through how it would behave with real customers. All of them are documented here, not glossed over.

---

## 2. Gap: The Answer Library Only Reflects What Was Written Down

### The Gap

This is the most important gap in the entire project, and it is worth understanding clearly.

The prototype's answer library contains 30 formally written, verified answers. In the real world, many important commitments never get formally written down anywhere. A Solutions Consultant might confirm a custom implementation timeline on a phone call. A Sales Engineer might mention over email that a feature will be available soon. A VP of Sales might say in a meeting "we can probably make that work."

None of these get captured into a formal answer library. They live in people's memory, in email threads, in call recordings nobody reviews again. The library only knows what someone deliberately chose to write down.

### Why This Matters

A retrieval system can only find what has been captured. If a large share of real commitments never get captured, then even a perfectly accurate retrieval system is only searching through a partial, incomplete picture of what the company has actually promised its customers.

This is not a hypothetical concern. Research on post-contract commitment tracking across hundreds of enterprise agreements has found that fewer than three in ten changes made after a contract is signed ever get formally recorded anywhere. There is good reason to believe a similar pattern exists earlier in the process, during the RFP and sales cycle itself.

### What a Real Fix Would Look Like

This is not solved by better search. It requires a way to make capturing informal commitments easy enough that people actually do it, ideally at the exact moment the commitment is made rather than requiring someone to remember to update a separate system later.

A realistic first step: a lightweight prompt after a sales call or email exchange, asking whether anything was promised that differs from the standard documented answer. Not a full library editing workflow, just a quick, low-friction way to flag it. That flagged item would then need a review process before it becomes part of the trusted, searchable library.

### Sketching a Minimal Version

It helps to think through what the smallest possible version of this fix could actually look like, even without building it.

**The trigger has to be tied to a specific moment, not a scheduled reminder.** Waiting for someone to remember to update a document later does not work, since that is the exact behavior causing the problem in the first place. The prompt should appear right after a natural end point, such as the close of a call or the sending of a follow up email, while the commitment is still fresh in the person's mind.

**The prompt itself needs to ask almost nothing.** A single, simple question is enough: did you say anything on this call that is different from what is currently documented. A yes or no answer, with a short optional note if the answer is yes. Anything more effortful than this will not get used consistently under real deadline pressure.

**A flagged commitment should not become a trusted answer automatically.** It needs a review step first, ideally by whoever already owns that specific answer category, before it gets promoted into the searchable library. This keeps the library trustworthy rather than filling it with unverified, one-off statements.

**A flagged commitment could work alongside the existing staleness signal, not replace it.** A pending, unverified update could show up as a visible note attached to the existing answer, something like a small flag saying a newer verbal commitment may exist and has not yet been confirmed. This way, a future search still shows the official answer, but also surfaces a signal that reality might have moved since it was written.

**The hardest part is not the mechanism, it is getting people to actually use it.** Research into post-contract obligation tracking shows this exact kind of system already exists in many companies for contract management, and people still do not consistently use it, because capturing an informal commitment does not feel like anyone's specific job. A real fix would likely need to attach this prompt to something people are already required to do anyway, such as an existing call log or customer relationship update, rather than asking them to do one more separate task.

None of this was built in this prototype. It is sketched here to show that the problem has been thought through past simply naming it, even though building and testing a real version of it is a separate, significant project on its own.

---

## 3. Gap: No PDF Intake

### The Gap

This prototype expects a question to be typed or pasted in as plain text. Real RFP documents almost always arrive as PDF files, often 50 to 150 pages long, mixing actual questions with legal boilerplate, formatting tables, and instructions.

### Why This Matters

Before any matching or searching can happen, someone has to manually find and extract each individual question from the PDF. This is often one of the most tedious and time-consuming parts of the entire process, and this prototype does nothing to help with it.

### What a Real Fix Would Look Like

A real system would need a way to read a PDF, reliably tell the difference between an actual question and surrounding text, and pull out a clean list of individual questions automatically. This is a genuinely difficult problem on its own, since RFP documents vary enormously in formatting and structure from one company to another. It was intentionally left out of this prototype to keep the scope focused on testing the matching and confidence mechanism specifically.

---

## 4. Gap: No Feedback Loop

### The Gap

When a user in this prototype accepts or rejects a suggested answer, nothing happens with that information. The system does not learn from it. The next time someone asks a similar question, the system behaves exactly the same way.

### Why This Matters

Without a way to learn from real usage, the system's quality is frozen at whatever level it was built to. It cannot improve as more people use it, and it cannot adjust to patterns specific to one company's actual questions and answers.

This also means the system provides no way to notice new gaps in the answer library over time. If Solutions Consultants keep escalating the same type of question because no good answer exists, nobody finds out unless someone happens to notice the pattern manually.

### What a Real Fix Would Look Like

A production version would log every accepted and rejected suggestion, and use that data in two ways. First, to identify which categories of questions have weak or missing coverage in the library, so someone knows where to focus effort writing new answers. Second, over time, to potentially improve how the matching itself works, though this second part is a more advanced capability that would need careful testing before being trusted.

---

## 5. Gap: The Library Cannot Stay Current on Its Own

### The Gap

Every answer in this prototype's library has a review date. If that date passes, the system shows a warning that the answer might be outdated. But nothing actually happens automatically when an answer becomes stale. Nobody gets notified. Nobody is responsible for updating it.

### Why This Matters

A library that nobody actively maintains decays. This is not a theoretical risk. During testing of this very prototype, every single answer in the library ended up flagged as outdated, simply because enough time had passed since the review dates were originally set and nobody had gone back to update them. The prototype demonstrated its own failure mode by simply existing untouched for a while.

### What a Real Fix Would Look Like

Every answer needs a specific, named person responsible for it, not just a general team. When an answer approaches its review date, that person should get a direct notification. If it passes the date without being reviewed, that should escalate, and ideally show up on some kind of visible dashboard showing how much of the library is currently overdue for review.

---

## 6. Gap: No Support for Multiple Companies

### The Gap

This prototype is built for one single, fictional company. There is no concept of separate companies, separate user accounts, or separate answer libraries that stay isolated from each other.

### Why This Matters

A real product would need to serve many different companies, and it would be a serious problem if one company's answers could somehow be seen by a different company using the same system. This kind of data leakage between customers is one of the fastest ways to lose enterprise trust entirely.

### What a Real Fix Would Look Like

Each company's data would need to be kept completely separate at every level, not just in how the interface displays it, but in how the underlying data is stored and searched. Someone using the system should never be able to accidentally see or search another company's answers, even by mistake. This requires careful technical design from the ground up, not something that can be easily added after the fact.

---

## 7. Gap: No Way to Edit an Answer Before Sending It

### The Gap

In this prototype, an answer is either used as-is or not used. There is no way to make small edits, like adjusting a detail for a specific customer's situation, without leaving the system entirely.

### Why This Matters

In practice, even a well-matched answer often needs a small tweak. Maybe the customer asked about a specific region, or used slightly different terminology that should be reflected in the response. Forcing someone to copy the answer elsewhere to edit it adds friction right at the point where the tool should be saving time.

### What a Real Fix Would Look Like

A simple in-place editing option, with a record kept of what was changed and why, so the original verified answer and any customer-specific adjustments are both visible and traceable.

---

## 8. Gap: Real Enterprise Data Security

### The Gap

This prototype uses entirely made-up, fictional company data by design. It was never intended to handle real, sensitive customer information, and does not have any of the security measures a real product would need.

### Why This Matters

An RFP document contains some of the most sensitive commercial information a company has. This includes internal budget details from the buyer, and unreleased product plans, real pricing limits, and known security gaps from the vendor answering the questions. Before any real company trusts an AI tool with this kind of information, they need clear, verifiable answers to specific questions.

There are three specific concerns any serious enterprise buyer would raise:

**Will my data be used to train your AI model, or could it somehow influence what other customers see?** This is a well-known concern, and it became especially prominent after public incidents where employees at other companies accidentally exposed confidential information by pasting it into AI tools that were not designed with proper data handling guarantees.

**If your system serves multiple companies, could our information ever be visible to a different customer using the same system?** As discussed in the section above, this requires real data isolation, not just a promise that it will not happen.

**Who inside your company can see our data, and what happens to it if we stop using your product?** This requires clear access controls and clear answers about data retention and deletion.

### What a Real Fix Would Look Like

A production system would need a formal agreement with whatever AI service it uses, guaranteeing that customer data is never stored or used to improve the AI model. Services like Google's enterprise cloud AI offering, Microsoft's enterprise AI offering, and OpenAI's enterprise API all offer this kind of guarantee through a formal contract, sometimes called a zero retention agreement, meaning submitted data is processed and then discarded rather than stored or used to improve the model.

Note for this prototype specifically: the free version of Google's AI tools used to build this prototype does not carry this kind of enterprise guarantee. This is exactly why the prototype uses entirely made-up, fictional data rather than any real company information. A real deployment would need to move to an enterprise tier with this guarantee formally in place before handling any real customer data.

Beyond the AI provider agreement, a production system would also need strict technical separation between different customers' data, not just a promise that data stays separate, but an actual technical design that makes it structurally impossible for one customer's information to appear in another customer's results. This needs to happen at several different levels at once.

| Layer | How Separation Would Work |
|---|---|
| Where data is stored | Each customer's answer library kept in its own separate storage space, not mixed together in one shared pool |
| The AI matching step itself | Every search is tagged with which customer it belongs to, and the AI only ever compares against that one customer's data, never the full combined set |
| How the system is accessed | Every request requires proof of which customer is making it, so there is no way to accidentally query someone else's data |
| For the most sensitive customers | An option to run a fully separate, dedicated version of the system just for one customer, rather than sharing infrastructure at all |

The point of designing it this way is that the system would never even attempt a search across all customers combined. It would always narrow down to one specific customer's data first, before doing any matching at all, so a leak between customers becomes structurally difficult rather than just procedurally forbidden.

On top of this, a production system would need clear records of who accessed what and when, detailed enough that a customer's legal or security team could review them, along with customer control over how long their data is kept and the ability to request full deletion at any time.

### Thinking About This as Stages, Not One Big Leap

Data security in a product like this is not something to solve all at once. It makes more sense to think about it as three distinct stages, each with a different level of real risk and a different level of protection required.

**Stage one is where this prototype currently sits.** Only fictional, made-up data is used. Nothing real or sensitive ever enters the system. The goal at this stage is simply to prove the matching mechanism itself works, without any real data ever being at risk.

**Stage two would be an early pilot with a real customer.** Only non-sensitive parts of their answer library would be loaded in at first, things like general capability descriptions or public pricing information, not sensitive security or compliance details. Basic protections like the AI provider agreement and simple access logging would need to be in place by this point.

**Stage three is full production use.** This includes sensitive information like security certifications and compliance documentation, and would require every protection described above to be fully in place, along with a formal outside security review before a large enterprise customer would realistically agree to use the system with their real, sensitive data.

The important product thinking here is that a system should not try to solve every stage three requirement while still at stage one. But it should be built from the start in a way that does not make stage three harder to reach later. This prototype's design choices, no persistent storage of any kind, no real data anywhere in the system, a completely fictional answer library, were all made specifically so that moving toward stage two and three later would not require rebuilding the system from scratch.

### An Open Question Worth Thinking About Further

One genuinely interesting unresolved question in this space: could running the AI matching model directly inside a customer's own private cloud environment, rather than sending their data to an outside AI service at all, remove this entire trust problem from the start.

If the AI model itself runs inside a customer's own systems, their data never has to leave their control in the first place, which would make questions about outside data retention agreements far less relevant. This is technically possible today using openly available AI models that can run on a customer's own infrastructure, though it comes with real trade-offs in setup complexity and ongoing maintenance.

For a product aimed at large, security-conscious enterprise buyers, this kind of customer-controlled deployment might end up being the detail that finally removes the last real barrier to adoption. This would be worth exploring directly with a customer's security and legal teams, not just the person making the buying decision, since it is often security and legal stakeholders who hold up a deal over exactly this kind of concern.

---

## 9. Gap: Handling Real, Messy Knowledge Bases

### The Gap

This prototype's 30 answers are clean, consistent, and well-organized. Real company answer libraries, built up over years by different people, are rarely this tidy. They often contain duplicate answers, partially outdated information, inconsistent terminology, and answers that were written for one specific customer situation but got reused more broadly without anyone checking if that made sense.

### Why This Matters

This prototype has not been tested against messy, real-world data of this kind. There is no evidence yet that the matching and confidence system would perform as well when the underlying answer library itself is inconsistent or contains conflicting information.

### What a Real Fix Would Look Like

Before a real company could use a production version of this system, their existing answer library would likely need a cleanup process: identifying duplicates, resolving contradictions, and standardizing formatting. This is realistically a significant undertaking on its own, separate from the technology itself.

---

## 10. Gap: Trust Erosion Over Time

### The Gap

If a system like this makes even a small number of visible mistakes early on, people tend to stop trusting it much faster than the actual error rate would suggest is reasonable. This prototype has not been tested with real users over time, so this risk has not actually been observed, but it is a well-documented pattern with automated tools generally.

### Why This Matters

A system that is highly accurate but loses user trust after a few visible mistakes will end up being used less and less, even if it continues working well. People will quietly go back to manual searching rather than risk being burned again by a bad automatic answer.

### What a Real Fix Would Look Like

A production rollout would likely need to start deliberately conservative, showing fewer automatic answers and asking for more human review than the system might technically support, specifically to build a track record of reliability before gradually loosening those settings. This is a rollout and change management strategy as much as it is a technical one.

---

## 11. What Would Come First

If this project moved from prototype to real product development, the honest priority order would be:

**First, the capture problem described in Section 2.** Without a way to get real commitments into the library, everything else is solving a smaller version of the actual problem.

**Second, real data security, described in Section 8.** No enterprise customer will use this with real data without it, regardless of how good the matching quality is.

**Third, PDF intake, described in Section 3.** This is table stakes for the tool to actually save time in a real workflow, since manually extracting questions defeats much of the purpose.

Everything else described in this document matters, but these three represent the difference between an interesting demonstration and something a real company could actually rely on.

---

*This document is part of the RFP Match POC project documentation. See the PRD for the full product overview, and the Problem Research Document for the evidence behind why this problem matters.*