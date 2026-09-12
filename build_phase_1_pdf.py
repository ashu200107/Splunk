import os
import re
import base64
import subprocess
import glob

PHASE_1_DIR = "/home/venom/Documents/Study/Study/Splunk Admin/01 - Phase 1 - Splunk Fundamentals"
ASSETS_DIR = "/home/venom/Documents/Study/Study/Splunk Admin/assets"
OUTPUT_HTML = "/tmp/phase_1_handbook.html"
OUTPUT_PDF = os.path.join(PHASE_1_DIR, "Splunk_Enterprise_Phase_1_Complete_Handbook.pdf")

FILES_IN_ORDER = [
    "00_Phase_1_Overview_and_TOC.md",
    "Chapter_01_What_is_Splunk_and_Machine_Data.md",
    "Chapter_02_Splunk_Core_Architecture_and_Components.md",
    "Chapter_03_The_End_to_End_Data_Pipeline.md",
    "Chapter_04_Splunk_Directory_Structure_and_Config_Precedence.md",
    "Chapter_05_Index_Storage_Architecture_and_Bucket_Lifecycle.md",
    "Chapter_06_Splunk_Licensing_Mechanics.md",
    "Chapter_07_Splunk_Ports_Protocols_and_Firewall_Matrix.md",
    "Chapter_08_Phase_1_Master_Revision_Notes.md",
    "Chapter_09_Phase_1_Master_Flashcards.md",
    "Chapter_10_Phase_1_Master_Assessment_Exam.md",
    "Chapter_11_Phase_1_Targeted_Review_Guide.md"
]

def image_to_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            ext = os.path.splitext(img_path)[1].lower().replace(".", "")
            if ext == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    return ""

def preprocess_markdown(content, filename):
    # 1. Replace Obsidian image links ![[filename.jpg]] with standard markdown ![caption](url)
    def repl_wiki_img(match):
        img_name = match.group(1).strip()
        img_path = os.path.join(ASSETS_DIR, img_name)
        b64 = image_to_base64(img_path)
        if b64:
            return f'![{img_name}]({b64})'
        return match.group(0)

    content = re.sub(r'!\[\[(.*?\.(?:jpg|jpeg|png|gif|svg))\]\]', repl_wiki_img, content, flags=re.IGNORECASE)

    # 2. Replace standard image links ![caption](../assets/filename.jpg)
    def repl_std_img(match):
        caption = match.group(1)
        rel_path = match.group(2)
        img_name = os.path.basename(rel_path)
        img_path = os.path.join(ASSETS_DIR, img_name)
        b64 = image_to_base64(img_path)
        if b64:
            return f'![{caption}]({b64})'
        return match.group(0)

    content = re.sub(r'!\[([^\]]*)\]\(([^)]+\.(?:jpg|jpeg|png|gif|svg))\)', repl_std_img, content, flags=re.IGNORECASE)

    # 3. Convert Obsidian callouts > [!NOTE], > [!IMPORTANT], > [!WARNING], > [!TIP], > [!CAUTION]
    # We will mark them for HTML rendering
    callout_pattern = re.compile(r'(?m)^> \[!(NOTE|IMPORTANT|WARNING|TIP|CAUTION|INFO)\][ \t]*(.*?)$\n((?:^>.*$\n?)*)')
    def repl_callout(match):
        c_type = match.group(1).upper()
        title = match.group(2).strip() or c_type
        body = match.group(3)
        # strip leading > from each line
        body_lines = [re.sub(r'^>[ \t]?', '', line) for line in body.splitlines()]
        body_text = "\n".join(body_lines)
        return f'\n<div class="callout callout-{c_type.lower()}">\n<div class="callout-title"><span class="callout-icon"></span> {title}</div>\n<div class="callout-content">\n\n{body_text}\n\n</div>\n</div>\n\n'

    content = callout_pattern.sub(repl_callout, content)

    return content

all_sections = []

for fname in FILES_IN_ORDER:
    fpath = os.path.join(PHASE_1_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            raw_text = f.read()
            processed = preprocess_markdown(raw_text, fname)
            all_sections.append({
                "filename": fname,
                "content": processed
            })

# HTML Template with Marked, Highlight.js, Mermaid, KaTeX, and Obsidian-like CSS
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Splunk Enterprise Administrator Handbook - Phase 1</title>
<!-- Marked for Markdown Parsing -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<!-- KaTeX for Math Formulas -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<!-- Highlight.js for Syntax Highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/ini.min.js"></script>
<!-- Mermaid for Diagrams -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.4.0/dist/mermaid.min.js"></script>
<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
  @page {
    size: A4 portrait;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-right {
      content: counter(page);
    }
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #1e293b;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
  }

  /* Cover Page */
  .cover-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    page-break-after: always;
    padding: 40px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f8fafc;
    border-radius: 8px;
  }

  .cover-badge {
    background: rgba(234, 88, 12, 0.2);
    color: #fb923c;
    border: 1px solid #ea580c;
    padding: 6px 16px;
    font-size: 11pt;
    font-weight: 700;
    border-radius: 9999px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 24px;
  }

  .cover-title {
    font-size: 32pt;
    font-weight: 800;
    line-height: 1.2;
    margin: 0 0 16px 0;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .cover-subtitle {
    font-size: 15pt;
    font-weight: 400;
    color: #94a3b8;
    max-width: 650px;
    margin: 0 0 32px 0;
  }

  .cover-meta {
    margin-top: 40px;
    padding-top: 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    text-align: left;
    width: 100%;
    max-width: 500px;
    font-size: 9.5pt;
  }

  .cover-meta-item strong {
    color: #38bdf8;
    display: block;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Chapter Container & Headings */
  .chapter-section {
    page-break-before: always;
  }

  .chapter-section:first-of-type {
    page-break-before: avoid;
  }

  h1 {
    font-size: 20pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin-top: 24px;
    margin-bottom: 16px;
    page-break-after: avoid;
  }

  h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 6px;
    margin-top: 20px;
    margin-bottom: 12px;
    page-break-after: avoid;
  }

  h3 {
    font-size: 11.5pt;
    font-weight: 600;
    color: #334155;
    margin-top: 16px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }

  p, ul, ol {
    margin-top: 0;
    margin-bottom: 12px;
  }

  li {
    margin-bottom: 4px;
  }

  /* Code Blocks */
  pre {
    background-color: #0f172a !important;
    border-radius: 6px;
    padding: 12px 14px;
    font-family: 'Fira Code', 'JetBrains Mono', Consolas, monospace;
    font-size: 8.5pt;
    line-height: 1.45;
    overflow-x: auto;
    border: 1px solid #1e293b;
    page-break-inside: avoid;
    margin-bottom: 14px;
  }

  code {
    font-family: 'Fira Code', 'JetBrains Mono', Consolas, monospace;
    font-size: 8.5pt;
    background-color: #f1f5f9;
    color: #be185d;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }

  pre code {
    background-color: transparent !important;
    color: #f8fafc !important;
    padding: 0;
    border: none;
    font-size: 8.5pt;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9pt;
    page-break-inside: avoid;
  }

  th, td {
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }

  th {
    background-color: #f8fafc;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #94a3b8;
  }

  tr:nth-child(even) {
    background-color: #f8fafc;
  }

  /* Images */
  img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 16px auto 6px auto;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    page-break-inside: avoid;
  }

  em {
    color: #64748b;
    font-size: 8.5pt;
    display: block;
    text-align: center;
    margin-bottom: 16px;
  }

  /* Mermaid Container */
  .mermaid {
    display: flex;
    justify-content: center;
    margin: 16px 0;
    page-break-inside: avoid;
    background: #ffffff;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
  }

  /* Callouts / Alerts */
  .callout {
    border-left: 4px solid #3b82f6;
    background-color: #eff6ff;
    padding: 12px 14px;
    border-radius: 0 6px 6px 0;
    margin: 14px 0;
    page-break-inside: avoid;
  }

  .callout-title {
    font-weight: 700;
    font-size: 9.5pt;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .callout-content {
    font-size: 9.5pt;
  }

  .callout-content p:last-child {
    margin-bottom: 0;
  }

  .callout-note {
    border-left-color: #3b82f6;
    background-color: #eff6ff;
    color: #1e3a8a;
  }
  .callout-note .callout-title { color: #1d4ed8; }

  .callout-important {
    border-left-color: #8b5cf6;
    background-color: #f5f3ff;
    color: #4c1d95;
  }
  .callout-important .callout-title { color: #6d28d9; }

  .callout-warning {
    border-left-color: #f59e0b;
    background-color: #fffbeb;
    color: #78350f;
  }
  .callout-warning .callout-title { color: #b45309; }

  .callout-tip {
    border-left-color: #10b981;
    background-color: #ecfdf5;
    color: #064e3b;
  }
  .callout-tip .callout-title { color: #047857; }

  .callout-caution {
    border-left-color: #ef4444;
    background-color: #fef2f2;
    color: #7f1d1d;
  }
  .callout-caution .callout-title { color: #b91c1c; }

  /* Blockquotes */
  blockquote {
    border-left: 3px solid #94a3b8;
    background-color: #f8fafc;
    margin: 12px 0;
    padding: 8px 14px;
    color: #475569;
    font-style: italic;
  }

  hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
  }
</style>
</head>
<body>

<!-- Cover Page -->
<div class="cover-page">
  <div class="cover-badge">Splunk Enterprise Administrator</div>
  <div class="cover-title">Phase 1 Complete Handbook<br>& Reference Manual</div>
  <div class="cover-subtitle">Foundations, Multi-Tier Architecture, 4-Stage Ingestion Pipeline, Configuration Precedence, Storage Buckets, Licensing & Enterprise Network Matrix</div>
  
  <div class="cover-meta">
    <div class="cover-meta-item">
      <strong>Candidate / Engineer</strong>
      Aspiring Enterprise Splunk Administrator
    </div>
    <div class="cover-meta-item">
      <strong>Curriculum Phase</strong>
      Phase 1 of 11 (Days 1–7)
    </div>
    <div class="cover-meta-item">
      <strong>Status & Benchmark Score</strong>
      Mastered & Verified (9.6 / 10 Avg)
    </div>
    <div class="cover-meta-item">
      <strong>Visual Architecture 3D Assets</strong>
      20 Full High-Res Isometric Cutaways
    </div>
  </div>
</div>

<!-- Rendered Content Container -->
<div id="content"></div>

<script>
  const markdownSections = %MARKDOWN_DATA_JSON%;

  marked.setOptions({
    gfm: true,
    breaks: false,
    highlight: function(code, lang) {
      if (lang === 'mermaid') {
        return '<div class="mermaid">' + code + '</div>';
      }
      if (hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    }
  });

  const contentDiv = document.getElementById('content');
  let combinedHtml = '';

  markdownSections.forEach((sec, idx) => {
    let sectionHtml = marked.parse(sec.content);
    combinedHtml += '<div class="chapter-section" id="section-' + idx + '">' + sectionHtml + '</div>';
  });

  contentDiv.innerHTML = combinedHtml;

  // Initialize Mermaid
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    fontFamily: 'Inter, sans-serif'
  });
  mermaid.run();

  // Render KaTeX Math
  renderMathInElement(contentDiv, {
    delimiters: [
      {left: '$$', right: '$$', display: true},
      {left: '$', right: '$', display: false},
      {left: '\\(', right: '\\)', display: false},
      {left: '\\[', right: '\\]', display: true}
    ],
    throwOnError: false
  });
</script>

</body>
</html>
"""

import json
json_data = json.dumps(all_sections)
final_html = HTML_TEMPLATE.replace("%MARKDOWN_DATA_JSON%", json_data)

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Generated standalone HTML at {OUTPUT_HTML} (Size: {os.path.getsize(OUTPUT_HTML)} bytes)")

# Convert to PDF via Google Chrome
chrome_cmd = [
    "google-chrome",
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--virtual-time-budget=10000",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={OUTPUT_PDF}",
    OUTPUT_HTML
]

print("Executing Google Chrome Headless to compile PDF...")
result = subprocess.run(chrome_cmd, capture_output=True, text=True)
print("Chrome Return Code:", result.returncode)

if os.path.exists(OUTPUT_PDF):
    size_mb = round(os.path.getsize(OUTPUT_PDF) / (1024 * 1024), 2)
    print(f"✅ Successfully compiled Phase 1 PDF: {OUTPUT_PDF} ({size_mb} MB)")
else:
    print("❌ PDF generation failed.")
