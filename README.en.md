# AI Development Bootcamp for Beginners

[中文](./README.md) | `English`

An open-source training repository that turns AI learning, project delivery, engineering evidence, and public writing into one workflow.

This is not just a note dump. It is an execution system: you are expected to build runnable projects, then turn each iteration into READMEs, solution docs, test traces, weekly reports, blog posts, and postmortems.

## Entry Rules

- Root `README.md`: the repository-level entry point
- Subdirectory `README.md` files: local indexes only, not replacements for the root entry point
- Project facts that change frequently: keep them in project README files, project issue/planning docs, weekly reports, and trace records instead of repeating them at multiple levels

## What This Repository Is

- Built for people with some `Python / Web` background who want to enter AI application development systematically
- Focused on delivery discipline: ship first, expand later
- Designed to produce both runnable projects and public-facing portfolio assets
- Structured to support three things at once: training, project execution, and blog serialization

## Best Entry Points

If this is your first visit, start here:

1. Repository orientation
   - [00-docs/en/README.md](./00-docs/en/README.md)
   - [00-docs/en/00-navigation/00-what-this-project-is.md](./00-docs/en/00-navigation/00-what-this-project-is.md)
   - [00-docs/en/00-navigation/01-getting-started.md](./00-docs/en/00-navigation/01-getting-started.md)
2. The first real project
   - [04-projects/text-api/README.md](./04-projects/text-api/README.md)
   - [04-projects/text-api/ENVIRONMENT.md](./04-projects/text-api/ENVIRONMENT.md)
   - [04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
3. The latest delivery and planning documents
   - [03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
   - [06-solution-docs/week-02-text-api-最小可交付拆解.md](./06-solution-docs/week-02-text-api-最小可交付拆解.md)
4. Public-output material
   - [05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md](./05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md)
   - [05-blog-posts/03-正式文章/01-把一个最小 LLM 文本 API 做出工程感：text-api 和第一轮收口.md](./05-blog-posts/03-正式文章/01-把一个最小%20LLM%20文本%20API%20做出工程感：text-api%20和第一轮收口.md)
   - [07-postmortems/2026-04-minimax-think-output-leak.md](./07-postmortems/2026-04-minimax-think-output-leak.md)

## Current Public Example

### `text-api`

This is the first baseline project in the repository. It is the current public example used to connect runnable code, engineering docs, weekly delivery records, blog drafts, and postmortems into one repeatable workflow.

Related links:

- Project README: [04-projects/text-api/README.md](./04-projects/text-api/README.md)
- Environment and startup: [04-projects/text-api/ENVIRONMENT.md](./04-projects/text-api/ENVIRONMENT.md)
- Project docs index: [04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
- Week 1 report: [03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
- Week 2 plan: [06-solution-docs/week-02-text-api-最小可交付拆解.md](./06-solution-docs/week-02-text-api-最小可交付拆解.md)
- Article: [05-blog-posts/03-正式文章/01-把一个最小 LLM 文本 API 做出工程感：text-api 和第一轮收口.md](./05-blog-posts/03-正式文章/01-把一个最小%20LLM%20文本%20API%20做出工程感：text-api%20和第一轮收口.md)

## Repository Structure

```text
ai-learning-bootcamp/
├─ 00-docs/               # navigation, training track, execution, output, project system
├─ 01-templates/          # reusable templates for reports, blog posts, READMEs, docs
├─ 02-daily-reports/      # daily execution records
├─ 03-weekly-reports/     # weekly reports
├─ 04-projects/           # project code and project-level docs
├─ 05-blog-posts/         # blog drafts and published articles
├─ 06-solution-docs/      # planning docs, solution docs, design notes
├─ 07-postmortems/        # failure reviews and postmortems
├─ 08-assets/             # screenshots, demo scripts, recordings
└─ 09-archive/            # archived materials
```

## How This Repository Works

The main difference between this repository and a typical learning repo is that every iteration is expected to leave behind a full evidence chain.

A minimal closed loop here includes:

- code and runnable results
- tests and verification records
- README, solution docs, and debugging notes
- weekly reports, blog drafts, and postmortems
- screenshots, scripts, or other reusable showcase assets

In other words, engineering delivery and content output are treated as part of the same workflow.

## Who This Is For

- People starting AI application development with some existing development basics
- People who need a training system, not just scattered notes
- People who want to turn learning into projects, writing, and a public portfolio

Not for:

- People with zero programming background who do not plan to build projects yet
- People who only want conceptual summaries without code or documentation work

## Participation

Feedback is especially useful in these areas:

- whether the documentation structure is clear
- whether the starting path is smooth for new users
- whether the example project is actually reproducible
- whether the repository structure supports long-form public writing
