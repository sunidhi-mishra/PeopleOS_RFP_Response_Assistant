# Eval Design Rationale
## How to Think About Testing an AI Retrieval System, Using RFP Match as a Worked Example

**Author:** Sunidhi Mishra  
**Project:** RFP Match POC  
**Purpose:** To explain not just what was tested, but why the testing was designed this specific way

---

## Executive Summary

This document explains the thinking behind how the RFP Match prototype was tested, separate from the results themselves.

Testing an AI system is not the same as testing regular software. Regular software either works or it does not. An AI system can work most of the time and fail in specific, predictable ways that a simple pass or fail test would never catch.

This document covers four things: why the test set was split into five specific categories instead of one big pile of questions, why the results were scored separately for each category instead of one overall accuracy number, why fifty test cases was the right number for this stage, and what a real production version of this testing approach would need to look like.

The short version of the reasoning: the single most important thing to know about an AI system like this is not how often it is right. It is how often it is confidently wrong in a way that could cause real harm. Most testing approaches would have missed this distinction entirely.

---

## Table of Contents

1. [Why Testing an AI System Is Different](#1-why-testing-an-ai-system-is-different)
2. [Why Five Categories, Not One](#2-why-five-categories-not-one)
3. [Why Scores Were Never Blended Together](#3-why-scores-were-never-blended-together)
4. [Why Fifty Test Cases](#4-why-fifty-test-cases)
5. [What This Approach Deliberately Did Not Test](#5-what-this-approach-deliberately-did-not-test)
6. [What a Production-Scale Version of This Would Need](#6-what-a-production-scale-version-of-this-would-need)

---

## 1. Why Testing an AI System Is Different

Regular software testing usually looks for a clear pass or fail. Does the button do what it is supposed to do. Does the calculation return the correct number. If it works, it works every time, under the same conditions.

An AI system built on similarity scoring, like the one in this prototype, behaves differently. It does not simply work or not work. It produces a confidence score for every single question, and that score can be misleadingly high for a wrong answer just as easily as it can be appropriately high for a correct one.

This means a testing approach built only around "does it find the right answer" is not enough. The more important question is "when it is wrong, does it at least know it might be wrong." A system that is right 90 percent of the time but confidently wrong the other 10 percent is far more dangerous than a system that is right 70 percent of the time but honestly uncertain about the rest.

This distinction shaped every decision described in this document.

---

## 2. Why Five Categories, Not One

The test set for this prototype was deliberately split into five distinct categories, each testing a different way the system could fail.

**Genuinely correct matches.** Questions phrased close to how they appear in the existing answer library. This tests whether the system recognizes what it should recognize.

**Deliberately tricky wrong matches.** Questions that sound plausible and touch on a similar topic, but ask about something the company does not actually support. For example, asking about a specific software integration the company has never built, phrased in a way that sounds similar to an integration they do support. This tests the system's most dangerous failure mode: confidently returning a wrong answer because it sounds close enough.

**Completely unrelated questions.** Questions with no real connection to anything in the answer library at all. This tests whether the system correctly recognizes when it simply does not know the answer, rather than forcing a match anyway.

**Compound questions.** Questions that actually contain two or three separate questions bundled into one sentence. This tests whether the system silently returns a partial answer while appearing to have answered the full question.

**Negatively phrased questions.** Questions asking what a company does not support, rather than what it does. This tests a known weakness of similarity-based matching, since these systems tend to recognize topics well but do not reliably recognize the word "not."

Testing only the first category would have shown the system performing very well, since that is the easiest case. It would have completely missed the far more important question of how the system behaves when a question is designed to trick it, or when a question is phrased negatively, or when it genuinely has no good answer available.

---

## 3. Why Scores Were Never Blended Together

A simpler approach would have been to run all fifty questions together and report one single accuracy percentage. This was deliberately avoided.

Here is why that would have been misleading. Imagine a system that performs perfectly on the sixteen genuinely correct match questions but fails badly on the eight deliberately tricky wrong match questions, incorrectly showing several of them as safe, automatic answers. Blended into one overall number, this could still look like a reasonably good result, somewhere around 80 percent accuracy across all fifty questions.

But an 80 percent blended score would be hiding the single most important fact: the system is unsafe specifically in the category that matters most, the one where a wrong answer gets sent to a real customer with no human review at all.

By scoring each category separately, and specifically tracking one number above all others, how often something risky got shown as a safe automatic answer, the actual safety of the system becomes impossible to hide behind a good-looking overall average.

This is the single most important design decision in the entire testing approach, and it is the reason the final result could be stated with confidence: zero incorrect answers were ever shown as safe and automatic, across every single risk category tested.

---

## 4. Why Fifty Test Cases

Fifty was chosen as a deliberate, practical middle ground for this stage of the project, not as a scientifically ideal number.

A smaller test set, say ten or fifteen questions, would not have had enough cases in each of the five categories to reveal a pattern. A single lucky or unlucky result could have skewed the whole picture.

A much larger test set, several hundred or more questions, would have provided more statistical confidence, but would have taken significantly longer to build by hand for a prototype at this stage, where the immediate goal was to test the underlying mechanism and threshold decision, not to run a full statistical validation study.

Fifty questions, split roughly evenly across the five categories, was enough to reveal a real, meaningful pattern, specifically the discovery that correct and incorrect answers can produce overlapping confidence scores. That finding would very likely still hold true with a much larger test set. What a larger test set would add is more precision about exactly how often each type of failure happens, not a different conclusion about whether the failure exists at all.

---

## 5. What This Approach Deliberately Did Not Test

Being clear about the limits of this testing approach matters as much as describing what it covered.

This test set was built by hand, based on reasoning about likely failure patterns. It was not drawn from a large sample of real RFP questions asked by real customers. A real company's actual question patterns might reveal failure modes this test set did not anticipate at all.

This test set also only measures whether the system's matching and confidence labeling behaves correctly. It does not measure whether a real user, under real time pressure, actually behaves the way the confidence label suggests they should. A system correctly labeling something as "needs review" does not guarantee a busy Solutions Consultant actually reviews it carefully before sending. That is a separate, harder question about human behavior, not something this kind of testing can answer.

Finally, this test set reflects one specific answer library and one specific underlying AI model. Both of those could change. A different or updated AI model might behave differently on the exact same questions.

---

## 6. What a Production-Scale Version of This Would Need

A real production version of this testing approach would need several things this prototype does not have.

**A much larger, continuously growing test set**, built from real questions the system actually encounters in use, not just from hand-written examples of what failures might look like.

**A repeatable process for re-running this test set** every time the answer library changes significantly, or every time the underlying AI model is updated or replaced, since a threshold and a set of results calibrated against one model version cannot be assumed to still hold true against a different one.

**A way to track real-world outcomes**, not just test results. If a real user overrides the system's suggestion, or if a sent answer later turns out to have been wrong, that information should feed back into future testing, not just get lost.

**Clear ownership** of this testing process. Someone specific needs to be responsible for reviewing test results after every significant change and deciding whether the current threshold settings are still appropriate, rather than assuming a decision made once stays correct forever.

The core principle behind all of this: a testing approach that only gets run once, at the start of a project, tells you whether a system worked on one specific day. A testing approach that gets run repeatedly, and specifically watches for the same risky failure patterns every time, is what actually keeps a system trustworthy over time.

---

*This document is part of the RFP Match POC project documentation. For the full calibration story and detailed test results, see the Confidence Threshold and Evaluation Framework document.*