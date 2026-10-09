# SerpApi India Hackathon 2026 — GAP Submission Pack

## Project name

**GAP — Technology Opportunity Intelligence**

## Tagline

**See where the signals don't agree.**

## Recommended track

**Knowledge & Public Interest**

Why: GAP combines live Scholar, Patents, News, Trends, and Search data into a research and technology-intelligence workflow. The project is primarily about evidence-backed research and innovation intelligence rather than shopping, pricing, or finance.

## Short description

GAP is a technology opportunity intelligence platform that combines live research, patent, attention, commercial-event, and market-presence signals to help users compare emerging technology subdomains. It retrieves evidence through SerpApi, derives transparent signal scores, ranks subdomains, and visualizes where technical momentum and demand are strong relative to visible market presence.

## Longer description

Technology opportunity research is fragmented across papers, patents, trends, news, and search results. GAP brings those sources together into one evidence-backed workflow.

A user enters a technology domain and a set of subdomains. GAP creates a multi-source query plan, retrieves live results through SerpApi, derives five normalized signals, and calculates a transparent opportunity score. The Landscape view then plots each subdomain on an Opportunity Map and exposes the underlying evidence so the user can inspect why an area ranked the way it did.

GAP is not a future-prediction engine. Its scoring model is a heuristic decision-support system designed to highlight areas that deserve deeper research.

## Who it is for

- researchers and students exploring emerging technology areas,
- founders evaluating technology spaces before deeper validation,
- innovation teams comparing technical and market signals,
- analysts who want source-backed evidence instead of a single opaque score.

## Why it is useful

Most technology landscape research requires manually switching between Scholar, patent databases, trend tools, news, and web search. GAP turns those fragmented searches into one repeatable analysis and preserves the evidence behind each derived signal.

## SerpApi usage

SerpApi is core to GAP's functionality.

GAP uses:

- **Google Scholar API** for baseline and recent research activity,
- **Google Patents API** for baseline and recent patent activity,
- **Google Trends API** for attention momentum,
- **Google News API** for recent commercial events such as funding, partnerships, launches, and products,
- **Google Search API** for visible market presence across companies, products, and platforms.

For six subdomains, GAP typically executes 38 planned SerpApi searches: 36 subdomain-level searches and two batched Google Trends requests.

Search results are normalized into a common evidence model. GAP derives Research (R), Patents (P), Attention (A), Commercial Events (E), and Market Presence (M), then computes:

```text
technical = 0.55R + 0.45P
demand = 0.55A + 0.45E
whitespace = technical × demand × (1 - M)
GAP score = whitespace × confidence
```

Missing required sources are treated as unknown rather than zero so an API/source failure cannot artificially create a high-opportunity score.

## Public links

**Live frontend**  
https://gap-technology-opportunity-intellig.vercel.app/

**Public GitHub repository**  
https://github.com/TanayP26/gap-technology-opportunity-intelligence

**Backend API**  
https://gap-tpproduction.up.railway.app/

**OpenAPI docs**  
https://gap-tpproduction.up.railway.app/docs

## Suggested AI-tool disclosure

Use only if accurate for the final submission:

**ChatGPT** — planning, debugging, architecture review, UI iteration, deployment troubleshooting, and documentation.

**OpenAI Codex** — coding assistance and implementation support.

Add any other AI development or content-generation tools that were actually used.

## Demo video plan — target 2:20 to 2:45

The official rules require a screen recording under three minutes showing the project running locally.

### 0:00–0:15 — Problem

Show the GAP landing page.

Narration:

> Technology opportunity research is fragmented across papers, patents, trends, news, and market search. GAP combines those signals so you can see where technical momentum and demand are strong but visible market presence is still comparatively low.

### 0:15–0:35 — Input

Enter a technology domain and select around six subdomains.

Briefly point out the five source families: Scholar, Patents, Trends, News, and Search.

### 0:35–0:55 — Analysis

Start the analysis.

While it runs, explain:

> GAP creates a multi-source SerpApi query plan. For six subdomains it typically performs 38 searches across five SerpApi engines, then normalizes the evidence into five signals.

If a fresh analysis takes too long for the recording, use an already-completed local analysis after briefly showing the analysis action.

### 0:55–1:35 — Landscape

Open the completed Landscape view.

Explain:

- X-axis = technical momentum,
- Y-axis = demand momentum,
- bubble size = GAP score,
- opacity = confidence,
- outer ring = visible market presence.

Highlight the top-ranked subdomain.

### 1:35–2:05 — Signal Matrix and evidence

Show the Signal Matrix and open a subdomain/evidence view.

Narration:

> The important part is that GAP does not just output a score. You can inspect the source evidence behind research, patents, attention, commercial events, and market presence.

### 2:05–2:30 — Integrity + close

Mention:

> Missing required source data is treated as unknown rather than zero, so an API failure cannot create artificial whitespace. GAP is a transparent decision-support heuristic, not a future-prediction engine.

End on the Landscape screen and the tagline:

**See where the signals don't agree.**

## Pre-recording checklist

- run the backend locally,
- run the frontend locally,
- verify the local database connection,
- pre-run the exact demo analysis once so cached source responses are available,
- close unrelated tabs and notifications,
- record at 1080p if practical,
- keep the final video below 3:00,
- upload as unlisted YouTube or an equivalent public link,
- test the video in an incognito/private window.

## Submission-form checklist

Prepare:

- project name,
- short and long description,
- **Knowledge & Public Interest** track,
- public GitHub repository,
- public demo video link,
- explanation of SerpApi engines and why each matters,
- lead participant name, email, phone, occupation, and years of professional experience,
- teammate names and emails if applicable,
- whether the project existed before the hackathon,
- how you learned about the event,
- AI tools used and how they contributed,
- acceptance of the Rules and Terms & Conditions.

## Final judge-facing checks

Before the deadline:

- verify the GitHub repository opens without sign-in,
- verify README setup instructions are clear,
- verify the demo video opens in incognito,
- verify the deployed frontend loads,
- verify the Railway `/health` endpoint,
- run one end-to-end production analysis,
- ensure no secrets or API keys are committed,
- ensure the submission is actually marked **Submitted**, not left as a draft.
