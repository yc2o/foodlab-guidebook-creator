#!/usr/bin/env python3
"""
Universal Markdown to Modular LaTeX Converter for FoodLAB Guidebooks.
Parses Markdown documents with comprehensive YAML frontmatter, eliminates section
numbering conflicts, generates chapter divider pages matching v0.2.8.pdf,
and outputs the entire modular LaTeX project inside latex-formatter/.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def slugify(text: str) -> str:
    """
    Creates a clean alphanumeric filesystem and anchor slug from text.
    """
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug[:50] if slug else "section"


def get_heading_targets(text: str) -> List[str]:
    """
    Generates unique anchor slugs for a heading (standard and GitHub-style with stripped dots).
    """
    targets: List[str] = []
    s_slug = slugify(text)
    if s_slug:
        targets.append(s_slug)

    # GitHub-style anchor (removes dots and punctuation before slugifying)
    gh_slug = re.sub(r"[^\w\s-]", "", text.lower())
    gh_slug = re.sub(r"[\s_]+", "-", gh_slug).strip("-")
    if gh_slug and gh_slug not in targets:
        targets.append(gh_slug[:50])

    return targets


def format_markdown_line(line: str) -> str:
    """
    Safely translates inline Markdown (bold, italic, code, links) to LaTeX
    while properly escaping reserved LaTeX characters in free prose.
    """
    if not line:
        return ""

    # 0. Decode standard HTML entities and sanitize arrows
    line = line.replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#39;", "'")
    line = re.sub(r"-+>\s*", r"\\textrightarrow{} ", line)
    line = re.sub(r"<-+\s*", r"\\textleftarrow{} ", line)
    line = re.sub(r"<->\s*", r"\\textleftrightarrow{} ", line)

    # 1. Stash and protect inline code blocks
    code_stash: Dict[str, str] = {}

    def stash_code(m):
        key = f"XYZCODEZ{len(code_stash)}ZYX"
        code_stash[key] = m.group(1)
        return key

    line = re.sub(r"`([^`]+)`", stash_code, line)

    # 2. Stash and protect links: [text](url)
    link_stash: Dict[str, Tuple[str, str]] = {}

    def stash_link(m):
        key = f"XYZLINKZ{len(link_stash)}ZYX"
        link_stash[key] = (m.group(1), m.group(2))
        return key

    line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash_link, line)

    # 3. Protect pre-existing raw LaTeX commands
    cmd_stash: Dict[str, str] = {}

    def stash_cmd(m):
        key = f"XYZCMDZ{len(cmd_stash)}ZYX"
        cmd_stash[key] = m.group(0)
        return key

    line = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?(\{[^{}]*\})*", stash_cmd, line)

    # 4. Escape LaTeX characters in remaining plain text BEFORE adding LaTeX tags
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for ch, rep in replacements:
        line = line.replace(ch, rep)

    # 5. Markdown bold & italic formatting
    line = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\\textbf{\\textit{\1}}", line)
    line = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", line)
    line = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\textit{\1}", line)

    # 6. Restore pre-existing LaTeX commands
    for k, v in cmd_stash.items():
        line = line.replace(k, v)

    # 7. Restore links
    for k, (ltxt, lurl) in link_stash.items():
        escaped_ltxt = format_markdown_line(ltxt)
        if lurl.startswith("#"):
            target_slug = lurl[1:].strip()
            line = line.replace(k, f"\\hyperlink{{{target_slug}}}{{{escaped_ltxt}}}")
        else:
            clean_url = lurl.replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")
            line = line.replace(k, f"\\href{{{clean_url}}}{{{escaped_ltxt}}}")

    # 8. Restore code blocks with appropriate escaping
    for k, raw_code in code_stash.items():
        clean_code = (
            raw_code.replace("\\", r"\textbackslash{}")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("&", r"\&")
            .replace("%", r"\%")
            .replace("$", r"\$")
            .replace("#", r"\#")
            .replace("_", r"\_")
            .replace("~", r"\textasciitilde{}")
            .replace("^", r"\textasciicircum{}")
        )
        line = line.replace(k, f"\\code{{{clean_code}}}")

    return line


def parse_frontmatter(content: str, default_name: str = "Handbook") -> Tuple[Dict[str, str], str]:
    """
    Extracts YAML or key-value frontmatter metadata from markdown.
    If metadata is missing, automatically infers title and provides sensible defaults
    without crashing or interrupting compilation.
    """
    clean_default = default_name.replace("-", " ").replace("_", " ").title()
    metadata: Dict[str, str] = {
        # Document Attributes
        "title": f"Buku Panduan {clean_default}",
        "subtitle": "PANDUAN OPERASIONAL",
        "description": "Pedoman Layanan Operasional di Lingkungan Kampus",
        "doc_number": "FL-OPS-GEN-001",
        "version": "1.0.0",
        "role": clean_default,
        "status": "Dokumen Resmi Operasional",
        "publisher": "Tim Operasional FoodLAB PENS",
        "author": "FoodLAB - PENS",
        "edition": "Edisi Pertama",
        "year": "2026",
        "city": "Surabaya, Indonesia",
        "institution": "Politeknik Elektronika Negeri Surabaya (PENS)",
        "system": "SISTEM INFORMASI OPERASIONAL DIGITAL KAMPUS",
        "department": "Laboratorium Rekayasa Perangkat Lunak & Sistem Cerdas",
        # PDF Specific Metadata
        "pdf_title": f"Buku Panduan {clean_default}",
        "pdf_subject": "Panduan Operasional FoodLAB",
        "pdf_keywords": "FoodLAB, Guidebook, PENS, SOP, Panduan",
        "pdf_author": "FoodLAB - PENS",
        # Document Switches
        "enable_chapter_cover": "true",
        "show_toc": "true",
    }

    yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if yaml_match:
        yaml_text = yaml_match.group(1)
        body = content[yaml_match.end() :]
        for line in yaml_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                key = k.strip().lower().replace("-", "_").replace(" ", "_")
                val = v.strip().strip("\"'")
                metadata[key] = val
        return metadata, body

    # Fallback: check if old markdown list style headers exist
    lines = content.splitlines()
    body_lines = []
    in_meta_block = True
    found_custom_meta = False

    for line in lines:
        stripped = line.strip()
        if in_meta_block:
            if stripped.startswith("# ") and not metadata.get("custom_title"):
                metadata["title"] = stripped[2:].strip()
                metadata["custom_title"] = "true"
                found_custom_meta = True
                continue
            elif stripped.startswith("- **Nomor Dokumen:**"):
                metadata["doc_number"] = stripped.split(":", 1)[1].replace("**", "").strip()
                found_custom_meta = True
                continue
            elif stripped.startswith("- **Versi Dokumen:**"):
                metadata["version"] = stripped.split(":", 1)[1].replace("**", "").strip()
                found_custom_meta = True
                continue
            elif stripped.startswith("- **Status:**"):
                metadata["status"] = stripped.split(":", 1)[1].replace("**", "").strip()
                found_custom_meta = True
                continue
            elif stripped.startswith("- **Peran Sasaran:**"):
                metadata["role"] = stripped.split(":", 1)[1].replace("**", "").strip()
                found_custom_meta = True
                continue
            elif stripped == "---":
                in_meta_block = False
                continue
            elif not stripped.startswith("- **"):
                in_meta_block = False
        body_lines.append(line)

    if not found_custom_meta:
        # Check first heading in body
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            metadata["title"] = h1_match.group(1).strip()
        print(f"[NOTICE] No YAML frontmatter found. Using sensible default metadata (Title: '{metadata['title']}').")

    return metadata, "\n".join(body_lines)


class MarkdownParser:
    """
    Converts Markdown block structures (tables, lists, callout boxes, paragraphs) to LaTeX.
    Correctly recognizes decimal section numbering and eliminates numbering collision bugs.
    """

    def __init__(self):
        self.in_list = False
        self.list_type = ""
        self.in_table = False
        self.table_rows: List[List[str]] = []
        self.in_box = False
        self.box_title = ""
        self.box_lines: List[str] = []

    def parse_blocks(self, text: str) -> str:
        output: List[str] = []
        lines = text.splitlines()
        idx = 0
        total_lines = len(lines)

        while idx < total_lines:
            line = lines[idx]
            stripped = line.strip()

            # 1. Table (| cell | cell |)
            if stripped.startswith("|") and stripped.endswith("|"):
                row_cells = [c.strip() for c in stripped[1:-1].split("|")]
                if all(re.match(r"^:?-+:?$", c) for c in row_cells):
                    idx += 1
                    continue
                if not self.in_table:
                    self.in_table = True
                    self.table_rows = []
                self.table_rows.append(row_cells)
                idx += 1
                continue
            elif self.in_table:
                output.append(self._flush_table())
                self.in_table = False

            # 2. Blockquote / Infobox (> text)
            if stripped.startswith(">"):
                box_content = stripped[1:].strip()
                if not self.in_box:
                    self.in_box = True
                    self.box_lines = []
                    title_match = re.match(r"^\*\*([^*]+)\*\*[:\s]*(.*)$", box_content)
                    if title_match:
                        self.box_title = title_match.group(1).strip()
                        rest = title_match.group(2).strip()
                        if rest:
                            self.box_lines.append(rest)
                    else:
                        self.box_title = ""
                        self.box_lines.append(box_content)
                else:
                    self.box_lines.append(box_content)
                idx += 1
                continue
            elif self.in_box:
                output.append(self._flush_box())
                self.in_box = False

            # 3. Lists
            unordered_match = re.match(r"^[-*]\s+(.*)$", stripped)
            ordered_match = re.match(r"^\d+[\.\)]\s+(.*)$", stripped)

            if unordered_match or ordered_match:
                current_type = "itemize" if unordered_match else "enumerate"
                item_text = unordered_match.group(1) if unordered_match else ordered_match.group(1)

                if not self.in_list or self.list_type != current_type:
                    if self.in_list:
                        output.append(f"\\end{{{self.list_type}}}\n")
                    self.in_list = True
                    self.list_type = current_type
                    output.append(f"\\begin{{{self.list_type}}}")

                output.append(f"  \\item {format_markdown_line(item_text)}")
                idx += 1
                continue
            elif self.in_list and not stripped:
                if idx + 1 < total_lines and not re.match(r"^[-*\d]", lines[idx + 1].strip()):
                    output.append(f"\\end{{{self.list_type}}}\n")
                    self.in_list = False
                idx += 1
                continue
            elif self.in_list:
                output.append(f"\\end{{{self.list_type}}}\n")
                self.in_list = False

            # 4. Headings & Sub-headings
            heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading_match:
                level = len(heading_match.group(1))
                heading_raw = heading_match.group(2).strip()

                # Check if heading starts with decimal numbers like "1.1", "5.2", "1.1.2"
                num_match = re.match(r"^(\d+(\.\d+)+)\s+(.*)$", heading_raw)
                targets = get_heading_targets(heading_raw)
                target_tags = "\n".join(f"\\hypertarget{{{t}}}{{}}" for t in targets)

                if num_match:
                    num_prefix = num_match.group(1)
                    clean_heading_title = num_match.group(3).strip()
                    formatted_heading = format_markdown_line(clean_heading_title)
                    dot_count = num_prefix.count(".")

                    if dot_count == 1:
                        # e.g. 5.1 -> LaTeX Section (LaTeX automatically prints 5.1!)
                        output.append(
                            f"\n{target_tags}\n"
                            f"\\section{{{formatted_heading}}}\n"
                        )
                    elif dot_count == 2:
                        # e.g. 5.1.2 -> LaTeX Subsection
                        output.append(
                            f"\n{target_tags}\n"
                            f"\\subsection{{{formatted_heading}}}\n"
                        )
                    else:
                        # e.g. 5.1.2.1 -> LaTeX Subsubsection
                        output.append(
                            f"\n{target_tags}\n"
                            f"\\subsubsection{{{formatted_heading}}}\n"
                        )
                else:
                    # Heading without explicit numbers: Map level relative to chapter
                    formatted_heading = format_markdown_line(heading_raw)
                    if level <= 3:
                        output.append(
                            f"\n{target_tags}\n"
                            f"\\section{{{formatted_heading}}}\n"
                        )
                    elif level == 4:
                        output.append(
                            f"\n{target_tags}\n"
                            f"\\subsection{{{formatted_heading}}}\n"
                        )
                    else:
                        output.append(
                            f"\n{target_tags}\n"
                            f"\\subsubsection{{{formatted_heading}}}\n"
                        )

                idx += 1
                continue

            # 5. Image (![alt](path))
            img_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
            if img_match:
                caption = format_markdown_line(img_match.group(1))
                img_path = img_match.group(2)
                output.append(
                    f"\n\\begin{{figure}}[H]\n"
                    f"  \\centering\n"
                    f"  \\includegraphics[width=0.85\\textwidth]{{{img_path}}}\n"
                    f"  \\caption{{{caption}}}\n"
                    f"\\end{{figure}}\n"
                )
                idx += 1
                continue

            # 6. Horizontal Rule (--- or ***)
            if re.match(r"^[-*_]{3,}$", stripped):
                remaining_text = "\n".join(lines[idx + 1 :]).strip()
                if remaining_text:
                    output.append("\n\\noindent\\rule{\\textwidth}{0.4pt}\n")
                idx += 1
                continue

            # 7. Normal Paragraph
            if not stripped:
                output.append("")
            else:
                output.append(format_markdown_line(stripped))

            idx += 1

        if self.in_table:
            output.append(self._flush_table())
        if self.in_box:
            output.append(self._flush_box())
        if self.in_list:
            output.append(f"\\end{{{self.list_type}}}\n")

        return "\n".join(output)

    def _flush_table(self) -> str:
        if not self.table_rows:
            return ""

        num_cols = max(len(row) for row in self.table_rows)
        if num_cols == 2:
            col_spec = "p{4.5cm} X"
        elif num_cols == 3:
            col_spec = "p{3.5cm} p{4cm} X"
        else:
            col_spec = " ".join(["X"] * num_cols)

        lines: List[str] = [
            f"\n\\begin{{xltabular}}{{\\textwidth}}{{{col_spec}}}",
            "  \\toprule",
        ]

        header_cells_formatted: List[str] = []
        data_lines: List[str] = []

        for idx, row in enumerate(self.table_rows):
            padded = row + [""] * (num_cols - len(row))
            formatted_cells = [format_markdown_line(c) for c in padded]

            if idx == 0:
                header_cells_formatted = [f"\\textbf{{{c}}}" for c in formatted_cells]
                lines.append(f"  {' & '.join(header_cells_formatted)} \\\\")
                lines.append("  \\midrule")
                lines.append("  \\endfirsthead")
                lines.append("  \\midrule")
                lines.append(f"  {' & '.join(header_cells_formatted)} \\\\")
                lines.append("  \\midrule")
                lines.append("  \\endhead")
                lines.append("  \\bottomrule")
                lines.append("  \\endfoot")
            else:
                data_lines.append(f"  {' & '.join(formatted_cells)} \\\\")

        lines.extend(data_lines)
        lines.append("\\end{xltabular}\n")
        self.table_rows = []
        return "\n".join(lines)

    def _flush_box(self) -> str:
        title_latex = format_markdown_line(self.box_title)
        box_body_lines: List[str] = []
        in_box_list = False

        for line in self.box_lines:
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("* "):
                if not in_box_list:
                    in_box_list = True
                    box_body_lines.append(r"\begin{itemize}")
                item_txt = format_markdown_line(stripped[2:].strip())
                box_body_lines.append(f"  \\item {item_txt}")
            else:
                if in_box_list:
                    box_body_lines.append(r"\end{itemize}")
                    in_box_list = False
                if stripped:
                    box_body_lines.append(format_markdown_line(stripped))

        if in_box_list:
            box_body_lines.append(r"\end{itemize}")

        content_latex = "\n".join(box_body_lines)
        self.box_lines = []
        self.box_title = ""
        return f"\n\\begin{{infobox}}[{title_latex}]\n{content_latex}\n\\end{{infobox}}\n"


def split_document_sections(body: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    Splits the markdown body into frontmatter sections (Preface/Kata Pengantar, Abstract/Abstrak),
    numbered chapters (Chapter/Bab 1..N), and appendices (Appendix/Lampiran 1..N).
    Supports both Indonesian and English conventions.
    """
    sections: Dict[str, List[Tuple[str, str]]] = {
        "frontmatter": [],
        "chapters": [],
        "appendices": [],
    }

    heading_pattern = re.compile(
        r"^(#{1,3})\s+(BAB\s+\d+|Bab\s+\d+|CHAPTER\s+\d+|Chapter\s+\d+|Lampiran\s+\d+|Appendix\s+\d+|Kata\s+Pengantar|Preface|Foreword|Abstrak|Abstract|Daftar\s+Isi|Table\s+of\s+Contents)[:\s]*(.*)$",
        re.MULTILINE | re.IGNORECASE,
    )

    matches = list(heading_pattern.finditer(body))
    if not matches:
        sections["chapters"].append(("Main Document", body))
        return sections

    for i, match in enumerate(matches):
        section_type_raw = match.group(2).strip()
        section_title_rest = match.group(3).strip()
        full_title = f"{section_type_raw}: {section_title_rest}" if section_title_rest else section_type_raw

        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        section_content = body[start_pos:end_pos].strip()

        st_lower = section_type_raw.lower()
        if any(k in st_lower for k in ("kata pengantar", "preface", "foreword")):
            sections["frontmatter"].append((full_title, section_content))
        elif any(k in st_lower for k in ("abstrak", "abstract")):
            sections["frontmatter"].append((full_title, section_content))
        elif any(k in st_lower for k in ("daftar isi", "table of contents")):
            continue
        elif any(k in st_lower for k in ("lampiran", "appendix")):
            sections["appendices"].append((full_title, section_content))
        elif any(k in st_lower for k in ("bab", "chapter")):
            sections["chapters"].append((full_title, section_content))
        else:
            sections["chapters"].append((full_title, section_content))

    return sections


def build_modular_project(md_path: Path, formatter_root: Path) -> Path:
    """
    Converts a single Markdown document into a complete modular LaTeX project
    inside the latex-formatter/ directory with dual-language support (ID / EN).
    """
    content = md_path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(content, default_name=md_path.stem)

    role_key = re.sub(r"[^a-z0-9_-]+", "_", md_path.stem.lower())

    # Detect language (respect explicit lang first; fallback to heading scan)
    raw_lang = metadata.get("lang", "").lower().strip()
    if raw_lang:
        is_english = raw_lang.startswith("en")
    else:
        is_english = bool(re.search(r"^#{1,3}\s+(Chapter|CHAPTER|Preface|Foreword)", body, re.MULTILINE))

    # Localization dictionary
    if is_english:
        label_doc_number = metadata.get("label_doc_number", "Document Number")
        label_doc_version = metadata.get("label_doc_version", "Document Version")
        label_doc_status = metadata.get("label_doc_status", "Document Status")
        label_doc_publisher = metadata.get("label_doc_publisher", "Publisher")
        label_contents = metadata.get("label_contents", "Table of Contents")
        label_chapter = metadata.get("label_chapter", "Chapter")
        label_chapter_upper = metadata.get("label_chapter_upper", "CHAPTER")
        label_appendix = metadata.get("label_appendix", "Appendix")
        label_preface = metadata.get("label_preface", "Preface")
    else:
        label_doc_number = metadata.get("label_doc_number", "Nomor Dokumen")
        label_doc_version = metadata.get("label_doc_version", "Versi Dokumen")
        label_doc_status = metadata.get("label_doc_status", "Status Dokumen")
        label_doc_publisher = metadata.get("label_doc_publisher", "Penerbit")
        label_contents = metadata.get("label_contents", "Daftar Isi")
        label_chapter = metadata.get("label_chapter", "Bab")
        label_chapter_upper = metadata.get("label_chapter_upper", "BAB")
        label_appendix = metadata.get("label_appendix", "Lampiran")
        label_preface = metadata.get("label_preface", "Kata Pengantar")

    # Directories inside latex-formatter/
    config_dir = formatter_root / "config"
    frontmatter_dir = formatter_root / "frontmatter"
    chapters_dir = formatter_root / "chapters" / role_key
    appendices_dir = formatter_root / "appendices" / role_key

    for d in [config_dir, frontmatter_dir, chapters_dir, appendices_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Generate config/metadata_<role>.tex
    metadata_tex_path = config_dir / f"metadata_{role_key}.tex"
    enable_chapter_cover_flag = "true" if metadata.get("enable_chapter_cover", "true").lower() in ("true", "1", "yes") else "false"

    pdf_title = format_markdown_line(metadata.get("pdf_title", metadata.get("title", "Buku Panduan FoodLAB"))).replace(r"\&", "&")
    pdf_subject = format_markdown_line(metadata.get("pdf_subject", metadata.get("subtitle", "Panduan Operasional"))).replace(r"\&", "&")
    pdf_keywords = format_markdown_line(metadata.get("pdf_keywords", "FoodLAB, PENS, SOP, Panduan"))
    pdf_author = format_markdown_line(metadata.get("pdf_author", metadata.get("author", "FoodLAB - PENS"))).replace(r"\&", "&")

    metadata_tex_content = f"""% Metadata for {metadata.get('title', 'FoodLAB Guidebook')} ({metadata.get('role', 'Role')})
% 100% Generated from Markdown Frontmatter
\\newcommand{{\\docTitle}}{{{format_markdown_line(metadata.get('title', 'Buku Panduan FoodLAB'))}}}
\\newcommand{{\\docSubtitle}}{{{format_markdown_line(metadata.get('subtitle', 'OPERASIONAL'))}}}
\\newcommand{{\\docDescription}}{{{format_markdown_line(metadata.get('description', 'Pedoman Layanan Operasional Kampus'))}}}
\\newcommand{{\\docNumber}}{{{format_markdown_line(metadata.get('doc_number', 'FL-OPS-001'))}}}
\\newcommand{{\\docVersion}}{{{format_markdown_line(metadata.get('version', '1.0.0'))}}}
\\newcommand{{\\docRole}}{{{format_markdown_line(metadata.get('role', 'Mitra'))}}}
\\newcommand{{\\docStatus}}{{{format_markdown_line(metadata.get('status', 'Dokumen Resmi Operasional'))}}}
\\newcommand{{\\docPublisher}}{{{format_markdown_line(metadata.get('publisher', metadata.get('author', 'Tim Operasional FoodLAB PENS')))}}}
\\newcommand{{\\docAuthor}}{{{format_markdown_line(metadata.get('author', 'FoodLAB - PENS'))}}}
\\newcommand{{\\docEdition}}{{{format_markdown_line(metadata.get('edition', 'Edisi Pertama'))}}}
\\newcommand{{\\docYear}}{{{format_markdown_line(metadata.get('year', metadata.get('date', '2026')))}}}
\\newcommand{{\\docCity}}{{{format_markdown_line(metadata.get('city', 'Surabaya, Indonesia'))}}}
\\newcommand{{\\docInstitution}}{{{format_markdown_line(metadata.get('institution', 'Politeknik Elektronika Negeri Surabaya (PENS)'))}}}
\\newcommand{{\\docSystem}}{{{format_markdown_line(metadata.get('system', 'SISTEM INFORMASI OPERASIONAL DIGITAL KAMPUS'))}}}
\\newcommand{{\\docDepartment}}{{{format_markdown_line(metadata.get('department', 'Laboratorium Rekayasa Perangkat Lunak & Sistem Cerdas'))}}}

% Localized Labels
\\newcommand{{\\labelDocNumber}}{{{format_markdown_line(label_doc_number)}}}
\\newcommand{{\\labelDocVersion}}{{{format_markdown_line(label_doc_version)}}}
\\newcommand{{\\labelDocStatus}}{{{format_markdown_line(label_doc_status)}}}
\\newcommand{{\\labelDocPublisher}}{{{format_markdown_line(label_doc_publisher)}}}
\\newcommand{{\\labelContentsName}}{{{format_markdown_line(label_contents)}}}
\\newcommand{{\\labelChapterName}}{{{format_markdown_line(label_chapter)}}}
\\newcommand{{\\labelChapterUpper}}{{{format_markdown_line(label_chapter_upper)}}}
\\newcommand{{\\labelAppendixName}}{{{format_markdown_line(label_appendix)}}}
\\newcommand{{\\labelPrefaceTitle}}{{{format_markdown_line(label_preface)}}}

% PDF Properties (Metadata)
\\newcommand{{\\docPdfTitle}}{{{pdf_title}}}
\\newcommand{{\\docPdfSubject}}{{{pdf_subject}}}
\\newcommand{{\\docPdfKeywords}}{{{pdf_keywords}}}
\\newcommand{{\\docPdfAuthor}}{{{pdf_author}}}

% Feature Flags
\\def\\enableChapterCover{{{enable_chapter_cover_flag}}}
"""
    metadata_tex_path.write_text(metadata_tex_content, encoding="utf-8")

    # 2. Split body into sections
    sections = split_document_sections(body)
    parser = MarkdownParser()

    # Frontmatter files
    has_preface = False
    for title, sec_content in sections["frontmatter"]:
        if any(k in title.lower() for k in ("kata pengantar", "preface", "foreword")):
            kp_path = frontmatter_dir / f"kata_pengantar_{role_key}.tex"
            parsed_kp = parser.parse_blocks(sec_content)
            kp_path.write_text(
                f"\\chapter*{{\\labelPrefaceTitle}}\n"
                f"\\addcontentsline{{toc}}{{chapter}}{{\\labelPrefaceTitle}}\n"
                f"\\hypertarget{{preface}}{{}}\n"
                f"\\hypertarget{{kata-pengantar}}{{}}\n\n"
                f"{parsed_kp}\n\n"
                f"\\vspace{{1.5cm}}\n"
                f"\\noindent\\textbf{{\\docPublisher}}\\\\\n"
                f"\\docInstitution\\par\n",
                encoding="utf-8",
            )
            has_preface = True

    # Chapters
    chapter_files: List[str] = []
    for idx, (title, sec_content) in enumerate(sections["chapters"], 1):
        clean_title = re.sub(r"^(BAB\s+\d+|Bab\s+\d+|CHAPTER\s+\d+|Chapter\s+\d+)[:\s]*", "", title, flags=re.IGNORECASE).strip()
        if not clean_title:
            clean_title = title

        slug = re.sub(r"[^a-z0-9]+", "_", clean_title.lower()).strip("_")[:40]
        chap_filename = f"bab{idx}_{slug}.tex"
        chap_path = chapters_dir / chap_filename

        chapter_anchor = slugify(title)
        parsed_content = parser.parse_blocks(sec_content)

        # Chapter file with optional Chapter Divider Cover Page
        chap_latex = f"""% Chapter {idx}: {clean_title}
\\makechaptercover{{{idx}}}{{{format_markdown_line(clean_title)}}}

\\hypertarget{{{chapter_anchor}}}{{}}
\\chapter{{{format_markdown_line(clean_title)}}}

{parsed_content}
"""
        chap_path.write_text(chap_latex, encoding="utf-8")
        chapter_files.append(f"chapters/{role_key}/{chap_filename}")

    # Appendices
    appendix_files: List[str] = []
    for idx, (title, sec_content) in enumerate(sections["appendices"], 1):
        clean_title = re.sub(r"^(Lampiran\s+\d+|Appendix\s+\d+)[:\s]*", "", title, flags=re.IGNORECASE).strip()
        if not clean_title:
            clean_title = title

        slug = re.sub(r"[^a-z0-9]+", "_", clean_title.lower()).strip("_")[:40]
        app_filename = f"lampiran{idx}_{slug}.tex"
        app_path = appendices_dir / app_filename

        app_anchor = slugify(title)
        parsed_content = parser.parse_blocks(sec_content)
        app_latex = (
            f"\\hypertarget{{{app_anchor}}}{{}}\n"
            f"\\chapter{{{format_markdown_line(clean_title)}}}\n\n"
            f"{parsed_content}\n"
        )
        app_path.write_text(app_latex, encoding="utf-8")
        appendix_files.append(f"appendices/{role_key}/{app_filename}")

    # 3. Generate Master document: <role_key>.tex inside latex-formatter/
    master_path = formatter_root / f"{role_key}.tex"

    chapters_includes = "\n".join(f"\\input{{{cf}}}" for cf in chapter_files)
    appendices_includes = ""
    if appendix_files:
        appendices_includes = "\\appendix\n" + "\n".join(f"\\input{{{af}}}" for af in appendix_files)

    kp_include = f"\\input{{frontmatter/kata_pengantar_{role_key}.tex}}\n" if has_preface else ""

    master_content = f"""% Master Document for {metadata.get('title', 'FoodLAB Guidebook')}
% Generated automatically by scripts/md2latex.py from {md_path.name}
\\documentclass[12pt,a4paper,oneside]{{report}}

% Load Global Configuration & Packages
\\input{{config/packages.tex}}

% Load Document-Specific Metadata
\\input{{config/metadata_{role_key}.tex}}

% Load Settings & Styling (dependent on metadata)
\\input{{config/settings.tex}}

\\begin{{document}}

% Frontmatter: Cover Page (Matching v0.2.8.pdf standard)
\\pagestyle{{empty}}
\\input{{frontmatter/cover.tex}}
\\newpage

% Pagination for Frontmatter
\\pagestyle{{plain}}
\\pagenumbering{{arabic}}
\\setcounter{{page}}{{2}}

{kp_include}
\\newpage

\\tableofcontents
\\newpage

% Body Chapters
\\pagestyle{{fancy}}

% Chapters
{chapters_includes}

% Appendices
{appendices_includes}

\\end{{document}}
"""
    master_path.write_text(master_content, encoding="utf-8")
    print(f"==> [SUCCESS] Generated master LaTeX project in latex-formatter/:")
    print(f"    - Master Doc: {master_path.name}")
    print(f"    - Language  : {'English' if is_english else 'Indonesian'}")
    print(f"    - Metadata  : config/metadata_{role_key}.tex")
    print(f"    - Chapters  : {len(chapter_files)} files in chapters/{role_key}/")
    print(f"    - Appendix  : {len(appendix_files)} files in appendices/{role_key}/")

    return master_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown guidebook to modular PENS LaTeX structure."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to source Markdown file (e.g. content/driver.md)",
    )
    parser.add_argument(
        "--formatter-dir",
        "-f",
        default="latex-formatter",
        help="Directory containing the latex-formatter environment.",
    )
    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    formatter_path = Path(args.formatter_dir)
    build_modular_project(input_file, formatter_path)


if __name__ == "__main__":
    main()
