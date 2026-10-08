# PRINT-READY NOTES — turn a finished note into a PDF in free chat (paste this after any note, summary or revision sheet)

Free chat cannot create PDF files, but it can show a styled page I print to PDF. Do this:
1. Convert the content I just received into ONE complete HTML document, shown as an artifact if artifacts are available (otherwise a single code block I can save as notes.html). Keep every word, table and heading exactly; change only presentation. Mermaid diagrams cannot print from here: redraw each as a simple HTML/CSS box-and-arrow layout or an HTML table, and label it.
2. Use exactly this stylesheet inside <style>:

@page { size: A4; margin: 22mm 22mm 20mm 22mm; }
body { font-family: "Liberation Serif", "Times New Roman", Georgia, serif; font-size: 11pt; line-height: 1.55; color: #1a1a1a; text-align: justify; }
h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 4px; color: #0f1115; }
h2 { font-size: 14pt; margin: 22px 0 8px; padding-bottom: 3px; border-bottom: 1pt solid #111; break-after: avoid; }
h3 { font-size: 12pt; font-style: italic; margin: 14px 0 4px; break-after: avoid; }
.kicker { font-family: Arial, "Liberation Sans", sans-serif; font-size: 9pt; letter-spacing: 1.3px; text-transform: uppercase; color: #555; }
.box { border-left: 1.6pt solid #1a1a1a; padding: 2px 0 2px 12px; margin: 10px 0; break-inside: avoid; text-align: left; }
.box b.label { font-style: italic; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 10px 0; break-inside: avoid; }
thead th { border-top: 1.1pt solid #000; border-bottom: 0.75pt solid #000; text-align: left; padding: 4px 6px; }
tbody td { padding: 4px 6px; vertical-align: top; text-align: left; }
tbody tr:last-child td { border-bottom: 1.1pt solid #000; }
figure { margin: 12px 0; break-inside: avoid; } figcaption { font-size: 9.4pt; font-style: italic; color: #333; text-align: left; }
ul { list-style: none; padding-left: 16px; } ul li::before { content: "– "; margin-left: -16px; }

3. Structure: <div class="kicker">CODE · SUBJECT · WEEK</div><h1>Title</h1>, then the content. Callouts (Definition — …, Mechanism — …, Worked example — …, Exam note — …) become <div class="box"><b class="label">Label.</b> text</div>. No colour, no shading, no decorative elements.
4. Tell me: "Open the artifact, then your browser's Print → Save as PDF (turn on background graphics off, margins default)."
