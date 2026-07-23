# Confidence Threshold and Evaluation Framework
## How the Auto-Answer Cutoff Was Chosen, Tested, and Confirmed

**Author:** Sunidhi Mishra  
**Project:** RFP Match POC

---

## Executive Summary

This document explains how the system decides whether an answer is safe to show automatically, and how that decision was tested against real data rather than left as a guess.

The cutoff for automatic answers was first set at 0.85 on a 0 to 1 similarity scale, based on reasoning that felt sound but had not been tested. Testing against real data showed that genuinely correct answers and genuinely incorrect answers can land in an overlapping range of scores, roughly between 0.77 and 0.81. This means no single number can perfectly separate right answers from wrong ones in that range.

The cutoff was kept at 0.85, just above the highest score seen from a wrong answer during testing, even though this means about 70 percent of correct answers require a quick human check instead of being shown automatically. This was a deliberate choice. A wrong answer sent automatically to a real customer is a far more expensive mistake than asking a human to spend a few extra seconds confirming a correct one.

This was validated with a structured, 50-case test set. Result: zero wrong answers were ever shown as safe and automatic, across every risk category tested.

One honest limitation was found during testing: questions phrased in a negative way, such as asking what a company does not support, are not always handled perfectly, because the underlying AI model recognizes topics well but does not reliably recognize the word "not." This is documented below rather than hidden.

Full reasoning and complete test data are included further down for anyone who wants to see the evidence directly. The summary above covers what most readers will need.

---

## Table of Contents

1. [Why This Decision Deserved Its Own Document](#1-why-this-decision-deserved-its-own-document)
2. [What a Similarity Score Actually Measures](#2-what-a-similarity-score-actually-measures)
3. [How the Cutoff Was First Set](#3-how-the-cutoff-was-first-set)
4. [Test One: Scoring Genuinely Correct Answers](#4-test-one-scoring-genuinely-correct-answers)
5. [Test Two: Scoring Deliberately Tricky Wrong Answers](#5-test-two-scoring-deliberately-tricky-wrong-answers)
6. [The Central Finding: An Overlap That Cannot Be Avoided](#6-the-central-finding-an-overlap-that-cannot-be-avoided)
7. [The Decision: Why 0.85 Was Kept](#7-the-decision-why-085-was-kept)
8. [Validation: The 50-Case Test Suite](#8-validation-the-50-case-test-suite)
9. [A Known Limitation: Negative Phrasing](#9-a-known-limitation-negative-phrasing)
10. [Why This Matters Beyond This Prototype](#10-why-this-matters-beyond-this-prototype)
11. [Open Questions for a Future Version](#11-open-questions-for-a-future-version)
12. [Appendix A: Full Test Data](#12-appendix-a-full-test-data)
13. [Appendix B: Negative Phrasing Failure Detail](#13-appendix-b-negative-phrasing-failure-detail)

---

## 1. Why This Decision Deserved Its Own Document

Most AI product decisions that look simple from the outside, such as "the system automatically answers above a certain confidence level," hide a genuinely difficult question underneath: what does that number actually mean, and how do you know it is the right one to use.

This document walks through exactly how that question was answered for this system. Not by guessing, but by building a labeled test set, measuring how the AI model actually behaves, and making a deliberate, reasoned trade-off once real evidence was available.

This decision is the single most evidence-backed piece of thinking in the entire project, and it deserves to be read on its own rather than summarized in a single sentence elsewhere.

---

## 2. What a Similarity Score Actually Measures

Before any cutoff number can mean anything, it helps to be precise about what the underlying score actually represents.

The system compares an incoming question to every answer in the library and produces a similarity score between 0 and 1, showing how closely related the two pieces of text are in meaning. This score measures how similar the topic and wording are. It does not measure whether the answer is actually correct.

For example, a question about integrating with Salesforce and an answer describing integration with Slack and Microsoft Teams can score highly similar, because both are about connecting with third-party software. The system has no built-in way of knowing that one is something the company actually supports and the other is not.

This distinction matters for everything that follows. A similarity score tells you how related two things sound. It does not tell you whether one is true. Treating a similarity score as proof of correctness, without testing where that assumption breaks down, is how AI systems can fail quietly, appearing to work because they produce a confident-looking number, while that number means something narrower than it appears to.

---

## 3. How the Cutoff Was First Set

The first version of this system used a cutoff of 0.85 for automatic answers, and anything below 0.60 was treated as too weak to trust at all, sent straight to a human expert instead.

This starting number came from reasonable-sounding intuition. A score of 0.85 felt like a high enough bar to represent genuine confidence, and 0.60 felt like a sensible floor below which nothing should be trusted. No real data informed this choice at the time. It was a starting assumption, not a measured decision.

This is worth stating plainly, because the value of everything that follows comes from the contrast: an assumption that was then actually tested against reality, rather than left unchallenged.

---

## 4. Test One: Scoring Genuinely Correct Answers

To test the cutoff, 15 questions were written that closely matched, or slightly reworded, questions already answered in the library. These represent the kind of question the system should recognize clearly.

**Result:** Scores ranged from 0.7667 to 0.9045, averaging 0.8302. Full scores for all 15 are in Appendix A.

Every single one of the 15 questions matched the correct answer in the library. That part worked perfectly. But only 4 of the 15 actually scored above the original 0.85 cutoff. The other 11, despite being genuinely correct matches, scored between 0.77 and 0.84, just below the line for an automatic answer.

This was the first sign that the original cutoff might not match how this specific AI model actually behaves in practice.

---

## 5. Test Two: Scoring Deliberately Tricky Wrong Answers

Knowing where correct answers land is only half the picture. The cutoff also needed to be tested against questions that should not be trusted, to see where incorrect answers land.

12 deliberately tricky questions were written: some asking about features or integrations the company does not actually support but that sound similar to ones it does, and some asking about topics that overlap two different categories in a confusing way, plus a few questions with no real connection to anything in the library at all.

**Result:** Scores ranged from 0.4984 to 0.8149, averaging 0.6462. Full scores for all 12 are in Appendix A.

Completely unrelated questions, like asking about the capital of France, scored clearly low, below roughly 0.57. The system correctly recognized these as unrelated. But the riskiest category, questions that sound plausible and touch on a similar topic while actually being wrong, scored as high as 0.8149. That single score is higher than four of the genuinely correct answers from the first test.

---

## 6. The Central Finding: An Overlap That Cannot Be Avoided

Placing both sets of results side by side reveals the most important finding in this entire process.

Genuinely correct answers scored between 0.7667 and 0.9045. Genuinely incorrect answers scored between 0.4984 and 0.8149. These two ranges overlap, roughly between 0.77 and 0.81.

This means there is no single cutoff number that can perfectly separate correct answers from incorrect ones in that range. Any number chosen inside that overlap will end up treating some correct answers as too risky, and some incorrect answers as safe, at the same time.

This is not a flaw in how the test was designed. It reflects something real about how this kind of AI matching works: how related two pieces of text sound and whether one is actually correct are connected, but not the same thing, and the gap between them shows up exactly as this kind of overlapping range rather than a clean dividing line.

---

## 7. The Decision: Why 0.85 Was Kept

Since no cutoff can perfectly separate the two groups, the decision had to be based on a clear principle rather than simply picking the number in the middle.

**Decision:** Keep the cutoff for automatic answers at 0.85, just above the highest score seen from an incorrect answer during testing, accepting that a meaningful share of genuinely correct answers would require a quick human check instead of being shown automatically.

**Reasoning:** The two possible mistakes this system can make are not equally costly.

If a correct answer gets routed to a quick human check instead of being shown automatically, that costs a few seconds of someone's time confirming something that was already right.

If an incorrect answer gets shown automatically with no human check at all, that risks sending wrong information about compliance, security, or pricing directly to a real customer during a high-stakes decision.

These two outcomes are not equally bad. When a clean separation is not possible, the safer choice is to protect against the more expensive mistake, even if it means asking for more human review than would feel maximally convenient. The number 0.85 was chosen specifically because it sits just above the worst wrong answer actually observed in testing, not simply because it happened to match the original guess.

---

## 8. Validation: The 50-Case Test Suite

Two rounds of testing are informative, but they are not something that can be easily repeated or checked again later. A structured, 50-case test suite was built to turn this testing into something repeatable, so it can be run again any time the answer library or the underlying AI model changes.

**Structure:** Each of the 50 test cases was labeled ahead of time with what the correct outcome should be, and grouped into five categories: genuinely correct matches, deliberately tricky wrong matches, completely unrelated questions, questions that actually contain multiple sub-questions, and questions phrased in a negative way.

**Why results were never blended into one number:** A single overall accuracy score would have hidden the one thing that matters most, which is whether anything risky ever gets shown as a safe, automatic answer. Blending everything together into one percentage would have made it easy to miss that exact signal.

**Results:**

| Category | Number of Cases | Correctly Handled | Shown as Automatic Answer |
|---|---|---|---|
| Genuinely correct matches | 16 | 31.2% | 31.2% (5 of 16) |
| Deliberately tricky wrong matches | 8 | 100% | 0.0% (0 of 8) |
| Completely unrelated questions | 5 | 100% | 0.0% (0 of 5) |
| Multiple sub-questions bundled together | 10 | 100% | 0.0% (0 of 10) |
| Negatively phrased questions | 11 | 81.8% | 0.0% (0 of 11) |

**The single most important result: zero incorrect answers were shown as safe and automatic, across all 34 risky test cases.**

Stated plainly, this is the trade-off: only about 31 percent of genuinely correct answers were shown automatically, and the rest required a brief human check. This was the deliberate cost of guaranteeing zero risky automatic answers, not an accidental shortcoming. A higher automatic answer rate was achievable by lowering the cutoff, and that option was deliberately rejected, because doing so would have also allowed the Salesforce-style wrong answer, at 0.8149, to be shown automatically.

---

## 9. A Known Limitation: Negative Phrasing

Two test cases involving negatively phrased questions did not behave exactly as expected, and they are worth examining honestly rather than treated as fully solved.

**Case 1:** "What compliance certifications have you not yet achieved that competitors typically have?" Expected outcome: no good match exists, should be sent to a human expert. Actual outcome: matched an existing certification answer, scored 0.6767, landed in the quick human check tier. The AI model picked up on the words about compliance and certifications and returned a close match, without recognizing that the question was actually asking about something the company lacks, not something it has.

**Case 2:** "Besides the regions you currently mentioned, where do you NOT have data residency options?" Expected outcome: should be sent to a human expert due to the negative phrasing. Actual outcome: correctly matched the right answer about data residency, but scored 0.7039, landing in the quick human check tier rather than being escalated as strictly expected.

**Root cause:** The underlying AI model recognizes topics well, but does not reliably recognize the word "not" or similar negative phrasing. A single negating word tends to get lost when the rest of the question strongly matches an existing topic. This was predicted as a likely weakness before testing began, and the test results confirmed it with real data.

**Why this was not patched over:** Both cases still landed in the quick human check tier, not the automatic answer tier, so the core safety guarantee held in both cases. The second case arguably represents reasonable behavior overall, since it did find the right topic and still flagged it for a human to check, even if it technically missed a stricter internal expectation. The first case is a more genuine gap worth naming directly: the system cannot yet reliably tell the difference between "what a company has" and "what a company lacks." Properly fixing this would require a separate step that identifies the intent of a question before searching for a match, which is a real, well-scoped feature for a future version, not something to patch into this prototype's current logic.

---

## 10. Why This Matters Beyond This Prototype

The specific numbers in this document, the 0.85 cutoff, the 0.77 to 0.81 overlap, and the zero percent result on risky test cases, are not universal truths. They are specific to one particular AI model and one specific 30-answer library. If either of those changes, this entire testing process would need to be run again.

That limitation is exactly why the test suite itself matters more than any single number it produced. A cutoff chosen once and never checked again is just a guess that happened to look reasonable one time. A cutoff backed by a labeled, repeatable test suite is a measurement that can be checked again every time something changes, whether that is a new AI model, a larger answer library, or new patterns in the kinds of questions being asked. This is the kind of ongoing discipline that separates a one-time AI feature from something that stays trustworthy over time.

---

## 11. Open Questions for a Future Version

**A secondary check step.** Could an additional AI-based step, one that checks whether a matched answer actually addresses what the question is really asking, rather than just how similar the topic sounds, recover some of the correct answers currently stuck in the quick human check tier, without bringing back the risk of wrong automatic answers.

**A dedicated way to catch negative phrasing.** Would a simple pre-check that identifies whether a question is asking positively or negatively, before any matching happens, meaningfully fix the negative phrasing weakness, and is this pattern common enough in real RFP questions to be worth building.

**Whether a different AI model would help.** Would switching to a different or larger underlying AI model shrink the overlap between correct and incorrect answer scores, or is this kind of overlap simply an unavoidable property of this type of matching technology in general. This would be worth testing seriously before moving toward a real production version.

---

## 12. Appendix A: Full Test Data

### Test One: Genuinely Correct Answers (15 cases)

| Question | Matched Answer | Score |
|---|---|---|
| Does PeopleOS have SOC 2 Type II certification? | KB001 | 0.9045 |
| What is the implementation timeline for enterprise companies? | KB012 | 0.8865 |
| Can you share retail customer references? | KB026 | 0.8797 |
| What pricing model does PeopleOS use? | KB017 | 0.8633 |
| Are there any implementation or onboarding setup fees? | KB018 | 0.8447 |
| What customer support tiers do you have? | KB022 | 0.8443 |
| Which payroll programs do you integrate with natively? | KB007 | 0.8402 |
| Is dedicated support provided during onboarding? | KB013 | 0.8330 |
| Do you integrate with Slack and Teams? | KB009 | 0.8191 |
| What is your penetration testing policy? | KB005 | 0.8102 |
| Do you have case studies in the healthcare sector? | KB027 | 0.8032 |
| What is your service uptime SLA percentage? | KB021 | 0.8020 |
| Is your platform fully compliant with GDPR? | KB002 | 0.7879 |
| Do you have public REST APIs for clients? | KB008 | 0.7672 |
| Does your company support Single Sign-On? | KB004 | 0.7667 |

All 15 matched the correct answer. Only 4 of the 15 scored above the 0.85 cutoff.

### Test Two: Deliberately Tricky Wrong Answers (12 cases)

| Question | Type | Matched Answer | Score |
|---|---|---|---|
| Does PeopleOS support native integration with Salesforce CRM? | Unsupported integration | KB009 | 0.8149 |
| Is PeopleOS compliant with HIPAA for healthcare workers' personal bank details? | Topic overlap | KB006 | 0.7765 |
| How does the uptime SLA affect my annual pricing discount? | Cross-category overlap | KB021 | 0.7763 |
| Can I pay for implementation support with credit cards? | Cross-category overlap | KB013 | 0.6971 |
| Is there a discount on your SOC 2 audit report? | Cross-category overlap | KB001 | 0.6819 |
| Can we import profiles via Active Directory LDAP? | Unsupported feature | KB010 | 0.6817 |
| Do you offer a mobile app for Android and iOS? | Unsupported feature | KB009 | 0.6460 |
| What is the capital of France? | Unrelated | KB002 | 0.5630 |
| How do I reset my admin password? | Unrelated | KB011 | 0.5628 |
| What is your favorite color? | Unrelated | KB022 | 0.5412 |
| Tell me a joke about computers? | Unrelated | KB021 | 0.5147 |
| How do I bake sourdough bread? | Unrelated | KB014 | 0.4984 |

---

## 13. Appendix B: Negative Phrasing Failure Detail

**Case 1:** "What compliance certifications have you not yet achieved that competitors typically have?" Expected: no match, should be sent to a human expert. Actual: matched KB001, scored 0.6767, landed in the quick human check tier.

**Case 2:** "Besides the regions you currently mentioned, where do you NOT have data residency options?" Expected: should be sent to a human expert due to strict negative phrasing rules. Actual: correctly matched KB002, scored 0.7039, landed in the quick human check tier.

---

*This document is part of the RFP Match POC project documentation. For the full product overview, see the PRD. For details on how this test suite was designed and why, see the Eval Design Rationale document.*