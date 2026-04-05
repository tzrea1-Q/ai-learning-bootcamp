# AI Development Bootcamp for Beginners

[中文](./README.md) | `English`

An open-source training repository that turns AI learning, project delivery, engineering evidence, and public writing into one workflow.

This is not just a note dump. It is an execution system: you are expected to build runnable projects, then turn each iteration into READMEs, solution docs, test traces, weekly reports, blog posts, and postmortems.

## What This Repository Is

- Built for people with some `Python / Web` background who want to enter AI application development systematically
- Focused on delivery discipline: ship first, expand later
- Designed to produce both runnable projects and public-facing portfolio assets
- Structured to support three things at once: training, project execution, and blog serialization

## Current Status

As of `2026-04-05`, this repository has moved beyond a training-notes repo and become an early open-source project with a real example project and output pipeline.

What is already in place:

- Core documentation for navigation, training track, execution system, output system, and project system
- Reusable templates for daily reports, weekly reports, blog posts, READMEs, solution docs, and postmortems
- The first example project: [`text-api`](./04-projects/text-api/README.md)
- A week 1 engineering report, a first blog draft, a week 2 delivery plan, and postmortem records
- A `docs/traces/` workflow for preserving tests, debugging, regressions, and environment verification as evidence

What is next:

- fuller request-level logging
- explicit timeout / retry behavior
- GitHub Actions running successfully in the remote repo
- more stable Docker / PostgreSQL local development support

## What You Can Reuse Right Now

- Runnable example code: a `FastAPI + OpenAI-compatible Chat Completions API` text-processing baseline, with MiniMax as the current default example upstream
- Engineering docs: README, API contract, local debugging guide, known issues, and next steps
- Execution records: daily reports, weekly reports, and planning docs
- Public-output assets: blog drafts, screenshots, demo scripts, and postmortems
- Trace records: verification files that preserve what was tested and why

If your goal is to build an open-source project that can also be written about in public, the key idea here is simple: every iteration should leave behind reusable assets, not just code.

## Best Entry Points

If this is your first visit, start here:

1. Repository orientation
   - [00-docs/en/README.md](./00-docs/en/README.md)
   - [00-docs/en/00-navigation/00-what-this-project-is.md](./00-docs/en/00-navigation/00-what-this-project-is.md)
   - [00-docs/en/00-navigation/01-getting-started.md](./00-docs/en/00-navigation/01-getting-started.md)
2. The first real project
   - [04-projects/text-api/README.md](./04-projects/text-api/README.md)
   - [04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
3. The latest delivery and planning documents
   - [03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
   - [06-solution-docs/week02-text-api-最小可交付拆解.md](./06-solution-docs/week02-text-api-最小可交付拆解.md)
4. Public-output material
   - [05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md](./05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md)
   - [05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md](./05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md)
   - [07-postmortems/2026-04-minimax-think-output-leak.md](./07-postmortems/2026-04-minimax-think-output-leak.md)

Most of the latest project-delivery artifacts are currently written in Chinese first, then selectively mirrored into English.

## Current Example Project

### `text-api`

This is the first baseline project in the repository. Its job is not to be large. Its job is to be a small AI API project that is actually runnable, testable, and documentable.

Current deliverables:

- `GET /health`
- `POST /summarize`
- `POST /key-points`
- `POST /rewrite`
- `pytest` test coverage
- unified `500 / 502` error structure
- a minimal `request_id` error path
- Docker PostgreSQL verification records

Related links:

- Project README: [04-projects/text-api/README.md](./04-projects/text-api/README.md)
- Project docs index: [04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
- Week 1 report: [03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
- Blog draft: [05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md](./05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md)

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

## Recommended Reading Order

If you want to use this repository as your own training system:

1. Start with project orientation and the getting-started path
2. Continue with the training-track and environment docs
3. Use `01-templates/` to start your own daily reports, weekly reports, and project docs
4. Run `04-projects/text-api`
5. Read the traces, weekly report, and blog draft together to understand how one round of work becomes public output

## Roadmap

Short-term direction:

1. Push `text-api` from "runnable" to "more stable"
2. Finish the next hardening pass around logging, timeout / retry, CI, and Docker
3. Publish ongoing weekly reports, blog posts, and postmortems as a serialized public record
4. Add more example projects so the repository becomes a series instead of a single example

## Who This Is For

This repository is a good fit for people who:

- are starting AI application development and want an engineering-first path
- can code a bit but lack a repeatable training system
- want to turn learning into a portfolio, blog series, and open-source work
- want to learn how to turn a small project into a public project with evidence

This repository is not a good fit for people who:

- have zero programming background and do not plan to build projects yet
- only want conceptual material without code or documentation work

## Contributing

This repository is still being upgraded from a personal training repo into a more mature open-source project.

Future contributions through `Issues / PRs / Discussions` are welcome, especially around:

- documentation clarity
- onboarding flow
- reproducibility of the example project
- how well the repository structure supports public writing and sharing

Supporting open-source files such as `LICENSE`, `CONTRIBUTING`, and a clearer project board will be added as the public release setup matures.

## Core Principles

- deliver before expanding
- close the loop before abstracting
- keep evidence before conclusions
- use AI as a collaborator, not a replacement for judgment
- preserve traces for tests, debugging, regressions, and real examples


