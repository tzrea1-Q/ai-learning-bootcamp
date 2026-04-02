# Multilingual Documentation Strategy

## Goal

This repository aims to serve as many learners as possible, so the documentation system must support at least Chinese and English.

That support needs structure. It cannot rely on a few ad-hoc translated READMEs.

## Current Policy

### 1. Chinese remains the primary editing language

The current canonical editing flow is still centered on the Chinese documents.

### 2. English must cover the core usage path

The following content must have English coverage:

- root README
- documentation index
- first-time user navigation
- core training track
- execution system overview
- output system overview
- project system overview
- frequently used templates

### 3. Secondary docs can be translated in phases

If a document is not part of the critical path for an international user, it can remain Chinese for now and be translated later by priority.

## Directory Rules

- Chinese content stays in the current main structure
- English docs live in `00-docs/en/`
- English templates live in `01-templates/en/`
- the English root entry point is `README.en.md`

## Update Workflow

When a core Chinese document changes:

1. update the Chinese source
2. sync the corresponding English version
3. verify that language-switch links still work

## Minimum Quality Standard

- the English version must be usable, not just a title translation
- Chinese and English structures should remain as parallel as possible
- key templates must be directly reusable by English-speaking users
