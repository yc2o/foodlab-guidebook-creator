# FoodLAB Guidebook Creator (`fg`) Publishing System

An automated document publishing pipeline that compiles pure Markdown sources (`content/*.md`) into modular LaTeX structures inside `latex-formatter/` and builds clean, production-grade PDF deliverables into `build/`.

This system is designed so that 100% of document metadata, PDF properties, and cover configurations are controlled directly from Markdown frontmatter without requiring manual LaTeX file edits.

---

## Directory Architecture

```text
foodlab-guidebook-creator/
├── build/                 # Production output: contains strictly clean .pdf deliverables
├── content/               # Source Markdown files (.md)
│   ├── template-id.md     # Reference specification in Bahasa Indonesia (template)
│   ├── template-en.md     # Reference specification in standard English (template)
│   └── driver.md          # FoodLAB Delivery Partner Handbook (v0.2.8)
├── latex-formatter/       # Isolated LaTeX compilation workspace
│   ├── config/            # packages.tex, settings.tex, & metadata_<role>.tex
│   ├── frontmatter/       # Official FoodLAB cover.tex & kata_pengantar_<role>.tex
│   ├── chapters/          # Modular babN_<slug>.tex chapter files
│   ├── appendices/        # Modular lampiranN_<slug>.tex appendix files
│   ├── figures/           # Official FoodLAB and PENS vector/raster assets
│   ├── <role>.tex         # Generated master LaTeX root document
│   └── .latexmkrc         # Active LaTeXmk engine and auxiliary cleanup configuration
├── scripts/
│   └── md2latex.py        # Markdown parser & modular LaTeX generator (Python stdlib)
├── fg                     # Native Bash CLI (Linux, macOS, WSL, Git Bash)
├── fg.bat                 # Native Windows Command Prompt (CMD) batch wrapper
├── fg.ps1                 # Native Windows PowerShell CLI
├── .gitignore             # Git ignore configuration for build and cache artifacts
└── README.md              # Technical documentation
```

---

## Unified CLI Tool (`fg`)

The unified `fg` tool dynamically maps input names to `content/<name>.md`, strips redundant file extensions automatically (e.g. `fg driver.md`, `fg driver.ml`, `fg driver`), and skips reference templates during bulk builds.

### On Windows (PowerShell or CMD)

Run `.\fg` in PowerShell or `fg` in Command Prompt:

```powershell
# 1. Compile a specific handbook (maps to content/driver.md)
.\fg driver

# 2. Extension-resilient syntax (automatically resolves to driver.md)
.\fg driver.md

# 3. Compile reference templates directly by name
.\fg template-id
.\fg template-en

# 4. Compile all active handbooks (automatically skips templates)
.\fg all

# 5. Purge generated LaTeX cache (preserves compiled PDFs in build/)
.\fg clean-cache

# 6. Purge intermediate auxiliary compilation files (.aux, .log, .toc, .fls)
.\fg clean

# 7. Remove build/ directory and purge all LaTeX cache files
.\fg clean-all
```

### On Linux / WSL / macOS

Run `./fg`:

```bash
# Compile a specific handbook
./fg driver
./fg driver.md

# Compile reference templates
./fg template-id
./fg template-en

# Compile all active handbooks in content/ (skips templates)
./fg all

# Clean generated LaTeX cache (preserves compiled PDFs)
./fg clean-cache

# Clean intermediate auxiliary files
./fg clean

# Full distclean (removes build/ and all cache)
./fg clean-all
```

---

## Template Filtering Policy

- Files named with `template-*`, `template_*`, or starting with `_*` are recognized as templates or drafts.
- In bulk commands (`fg all` or running `fg` without arguments), template files are automatically skipped so that `build/` contains only active handbooks.
- If a user duplicates `template-id.md` to `tenant.md`, it is immediately recognized as a production handbook and compiled on `fg all` without requiring configuration changes.
- To compile a template explicitly, specify its name directly: `fg template-id` or `fg template-en`.

---

## Resilient Metadata Handling

- If a Markdown file contains complete YAML frontmatter, all fields are mapped directly to LaTeX definitions and PDF document properties.
- If a Markdown file has **no frontmatter**, the compiler automatically infers the title from the first `# Heading` or filename, applies sensible operational defaults, and compiles without interruption.

---

## YAML Frontmatter Specification

```yaml
---
# ==============================================================================
# DOCUMENT & COVER METADATA
# ==============================================================================
title: "Buku Panduan Mitra Driver"
subtitle: "OPERASIONAL PENGANTARAN"
description: "Pedoman Layanan Pengantaran Berjalan Kaki di Lingkungan"
doc_number: "FL-OPS-DRV-011"
version: "0.2.8"
role: "Mitra Driver"
status: "Dokumen revisi selesai"
publisher: "Tim Operasional FoodLAB PENS"
author: "FoodLAB - PENS"
edition: "Edisi Pertama"
year: "2026"
city: "Surabaya, Indonesia"
institution: "Politeknik Elektronika Negeri Surabaya (PENS)"
system: "SISTEM INFORMASI OPERASIONAL DIGITAL KAMPUS"
department: "Laboratorium Rekayasa Perangkat Lunak & Sistem Cerdas"

# ==============================================================================
# PDF METADATA (Document Properties & Hyperref)
# ==============================================================================
pdf_title: "Buku Panduan Mitra Driver FoodLAB"
pdf_subject: "Panduan Operasional Mitra Driver FL-OPS-DRV-011"
pdf_keywords: "FoodLAB, Driver, Handbook, PENS, SOP, Panduan"
pdf_author: "FoodLAB - PENS"

# ==============================================================================
# LAYOUT & VISUAL SETTINGS
# ==============================================================================
lang: "id"                   # "id" for Indonesian, "en" for English
enable_chapter_cover: "true" # Full-page solid deep blue chapter cover divider
---
```

---

## License & Intellectual Property

Copyright (c) 2026 yc2o. All rights reserved.

This project is licensed under the **FoodLAB Proprietary and Brand Asset Protection License**.

- **Brand Assets & Trademarks**: All FoodLAB logos, mascots, brand names, visual tokens, and handbook contents are the intellectual property of yc2o and the FoodLAB Project (All Rights Reserved). Unauthorized external use or commercial redistribution is strictly prohibited.
- **Tooling & Scripts**: The compilation scripts (`md2latex.py`) and CLI utilities (`fg`) are available for educational, research, and non-commercial publishing use under the terms stated in [LICENSE](LICENSE).
