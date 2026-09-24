---
# ==============================================================================
# DOCUMENT & COVER METADATA
# ==============================================================================
title: "Standard Template Guidebook"
subtitle: "OPERATIONAL & PUBLISHING SPECIFICATIONS"
description: "Technical Writing Guidelines for Markdown to LaTeX PENS Compilation"
doc_number: "FL-OPS-TMP-EN-001"
version: "1.0.0"
role: "Template EN"
status: "Official Reference Standard"
publisher: "FoodLAB Systems & Architecture Team"
author: "FoodLAB - PENS"
edition: "First Edition"
year: "2026"
city: "Surabaya, Indonesia"
institution: "Politeknik Elektronika Negeri Surabaya (PENS)"
system: "SISTEM INFORMASI OPERASIONAL DIGITAL KAMPUS"
department: "Laboratorium Rekayasa Perangkat Lunak & Sistem Cerdas"

# ==============================================================================
# PDF METADATA (Document Properties & Hyperref)
# ==============================================================================
pdf_title: "FoodLAB PENS Standard Template Guidebook"
pdf_subject: "Standard Operational Publishing Guidelines FL-OPS-TMP-EN-001"
pdf_keywords: "FoodLAB, Template, Guidebook, PENS, SOP, English"
pdf_author: "FoodLAB - PENS"

# ==============================================================================
# LAYOUT & VISUAL SETTINGS
# ==============================================================================
template: true
lang: "en"
enable_chapter_cover: "true"
---

# Preface

This preface section is automatically parsed into the LaTeX frontmatter with standardized Roman numeral page numbering. Authors should describe the context of the document, the target reader demographic, and institutional acknowledgments within one to three concise paragraphs.

All manuals are authored as self-contained Markdown files inside the `content/` folder. Authors do not need to configure separate LaTeX template files because all typography, layout geometry, and cover properties are driven by the YAML frontmatter above.

---

# Chapter 1: Document Structure and Heading Hierarchy

## 1.1 Section Numbering and Level Mapping

The compiler maps Markdown heading levels intelligently to avoid redundant numbering:

- `# Chapter <N>: <Title>` or `# Bab <N>: <Title>` maps to a primary chapter (`\chapter`). When `enable_chapter_cover` is set to `true`, a full-page chapter divider page featuring royal blue and gold accent strips alongside official branding is automatically generated before chapter content.
- `## <Section Title>` or `## <N.M> <Section Title>` maps to a section (`\section`). LaTeX automatically applies hierarchical numbering such as `1.1 Title` without duplicating numbers.
- `### <Subsection Title>` or `### <N.M.P> <Subsection Title>` maps to a subsection (`\subsection`).

> **Note**
>
> You may write section titles directly as `## Background` or with manual numbering as `## 1.1 Background`. The compiler automatically normalizes the titles for clean and consistent PDF typography.

## 1.2 Text Styling and Emphasis

Use standard Markdown formatting for inline emphasis:

- **Bold Text**: Double asterisks `**bold keywords**` for core concepts and critical terms.
- *Italic Text*: Single asterisk `*foreign terms*` for technical terminology.
- `Inline Code`: Backticks `` `FL-ORDER-001` `` for identifiers, parameters, and commands.
- Internal Hyperlinks: Use `[Link Text](#section-anchor)` for interactive cross-references.

## 1.3 Operational Callout Boxes

To produce highlighted notices, critical SOPs, or safety instructions, use Markdown blockquote syntax (`>`) with a bold title on the first line:

> **Delivery Service Core Pillars**
>
> - **Efficiency**: Orders are dispatched and delivered swiftly to minimize waiting time during short academic breaks.
> - **Integrity**: Food and beverages arrive in pristine condition matching the original vendor preparation.

The callout box is rendered with a golden dashed border, warm cream background, and bold royal blue headings matching official FoodLAB design tokens.

## 1.4 Special Characters, Sequences, and Internal Links

- **Special Characters**: Symbols such as `&`, `%`, `$`, `#`, `_` are automatically escaped by the compiler.
- **Process Sequences**: Use standard text arrows like `->` or `>` (e.g. `Order Placed -> Ready for Delivery -> Delivered`) without raw LaTeX math formulas.
- **Cross References**: Use `[Reference Text](#anchor-slug)` to link between chapters or sections (e.g. `[Section 2.1](#21-tabular-data-specifications)`). Links automatically render as interactive clickable anchors in the output PDF.

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

## 2.3 Figures, Screenshots, and Narrative Captions

To embed diagrams or mobile application screenshots, store image assets in the `figures/` directory (e.g., `figures/foodlab-logo.png`) and use standard Markdown image syntax with caption text:

![Official FoodLAB Brand Mark](figures/foodlab-logo.png)

*The illustration above exemplifies UI screenshot or diagram embedding. Narrative paragraphs directly following the figure provide contextual operational walk-throughs and interface component breakdowns.*
