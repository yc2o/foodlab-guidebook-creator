---
# ==============================================================================
# DOCUMENT & COVER METADATA
# ==============================================================================
title: "Standard Template Handbook"
subtitle: "OPERATIONAL & PUBLISHING GUIDELINES"
description: "Technical Guidelines for Publishing Markdown to PENS LaTeX Format"
doc_number: "FL-OPS-TMP-EN-001"
version: "1.0.0"
role: "Template EN"
status: "Official Reference Document"
publisher: "FoodLAB Architecture & Operations Team"
author: "FoodLAB - PENS"
edition: "First Edition"
year: "2026"
city: "Surabaya, Indonesia"
institution: "Politeknik Elektronika Negeri Surabaya (PENS)"
system: "CAMPUS DIGITAL OPERATIONAL INFORMATION SYSTEM"
department: "Software Engineering & Intelligent Systems Laboratory"

# ==============================================================================
# PDF METADATA (Document Properties & Hyperref)
# ==============================================================================
pdf_title: "FoodLAB Standard Template Handbook"
pdf_subject: "Standard Operational Documentation Guidelines FL-OPS-TMP-EN-001"
pdf_keywords: "FoodLAB, Template, Guidebook, PENS, SOP, English"
pdf_author: "FoodLAB - PENS"

# ==============================================================================
# LAYOUT & VISUAL SETTINGS
# ==============================================================================
lang: "en"
enable_chapter_cover: "true"
---
# Preface

This preface is automatically extracted by the publishing pipeline into the frontmatter section of the LaTeX document with unified pagination. Provide a concise summary of the document purpose, intended audience, and operational context in one to three structured paragraphs.

All publication manuals are authored using a single Markdown source file within the `content/` directory. Authors never need to edit LaTeX source files manually because all layout parameters, covers, and typography are defined through the YAML frontmatter above.

---

# Chapter 1: Document Structure and Heading Hierarchy

## 1.1 Heading Levels and Numbering Standards

The converter parses standard Markdown heading structures and maps them deterministically into LaTeX levels without numbering collisions:

- `# Chapter <N>: <Title>` or `# Bab <N>: <Title>` maps to the main chapter level (`\chapter`). When `enable_chapter_cover` is set to `true`, a full-page solid deep blue cover divider is automatically generated.
- `## <Section Title>` or `## <N.M> <Section Title>` maps to a section (`\section`). LaTeX automatically provides sequential numbers such as `1.1 Title` without duplicating numbers.
- `### <Subsection Title>` or `### <N.M.P> <Subsection Title>` maps to a subsection (`\subsection`).

> **Operational Note**:Section headings can be written with or without manual decimal prefixes (e.g. `## Service Architecture` or `## 1.1 Service Architecture`). The compiler normalizes the title so that the generated output remains clean.

## 1.2 Inline Typography and Text Styling

Use standard Markdown syntax for text emphasis:

- **Bold Text**: Two asterisks `**bold text**` for key terms, actions, and critical invariants.
- *Italic Text*: Single asterisk `*foreign terms*` for technical terminology.
- `Inline Code`: Backticks `` `FL-ORDER-001` `` for identifiers, parameters, and commands.
- Internal Hyperlinks: Use `[Link Text](#section-anchor)` for interactive cross-references.

## 1.3 Operational Callout Boxes

To produce highlighted notices, critical SOPs, or safety instructions, use Markdown blockquote syntax (`>`) with a bold title:

> **Delivery Service Core Pillars**
>
> - **Efficiency**: Orders are dispatched and delivered swiftly to minimize waiting time during short academic breaks.
> - **Integrity**: Food and beverages arrive in pristine condition matching the original vendor preparation.

The callout box is rendered with a golden dashed border, warm cream background, and bold royal blue headings matching official FoodLAB design tokens.

---

# Chapter 2: Tables, Figures, and Lists

## 2.1 Tabular Data Specifications

Tabular data is authored using standard Markdown pipe tables. The converter renders them into full-width LaTeX `tabularx` environments with formal academic horizontal rules:

| YAML Parameter | Requirement | Purpose and Behavior |
| --- | --- | --- |
| title | Mandatory | Primary document title rendered on the cover page |
| subtitle | Mandatory | Uppercase secondary title rendered in royal blue |
| doc_number | Mandatory | Official operational document identifier code |
| version | Mandatory | Published semantic release version (e.g. 0.2.8) |
| lang | Optional | Language identifier (`en` for English, `id` for Indonesian) |
| pdf_title | Optional | Embedded document title inside PDF viewer properties |

## 2.2 Ordered and Unordered Lists

Unordered bullet points use standard hyphens `-`:

- Verification of order seal integrity at canteen stalls.
- Pickup confirmation via the mobile application.
- Delivery execution to designated campus building landmarks.

Ordered procedural steps use numerical prefixes `1.`:

1. Launch application and toggle operational status to online.
2. Accept nearest available dispatch assignment notification.
3. Validate handoff verification code with the merchant partner.

---

# Appendix 1: Configuration Parameters Glossary

| Term | Operational Definition |
| --- | --- |
| GBL | *Guide Book LaTeX*, the autonomous Markdown-to-PDF publishing pipeline. |
| Frontmatter | YAML configuration block at the top of each content Markdown file. |
| Clean Cache | CLI target to clear intermediate LaTeX files while preserving PDFs. |

---

# Appendix 2: Quick Publishing Checklist

1. Place new manual source files at `content/<name>.md`.
2. Execute `gbl <name>` on Windows or `./gbl <name>` on Linux/macOS.
3. Inspect the compiled deliverable located at `build/<name>.pdf`.