# md2html

> Dependency-free Markdown → HTML converter. Pure Python standard library. No `pip install`. Works on Windows / macOS / Linux / Android (Termux).

Turn `.md` notes, READMEs and docs into clean, styled HTML in one command — no internet, no dependencies, fully offline.

[![Sponsor](https://img.shields.io/badge/sponsor-afdian-ff69b4)](https://afdian.com/a/Zhiyilang)

## Why

- **Zero dependencies** — only the Python standard library. Drop the single file anywhere and run.
- **Offline** — nothing is sent to any server.
- **Portable** — one `md2html.py` file, ~10 KB, runs on Python 3.6+.
- **Pretty by default** — ships a clean, responsive GitHub-like stylesheet.

## Features

| Feature | Supported |
| --- | --- |
| Headings `#` … `######` | ✅ |
| Bold `**x**` / Italic `*x*` | ✅ |
| Inline code `` `x` `` | ✅ |
| Links `[t](url)` + bare URLs | ✅ |
| Unordered / ordered lists | ✅ |
| Fenced code blocks ```` ``` ```` | ✅ |
| Blockquotes `>` | ✅ |
| Horizontal rules `---` | ✅ |
| Paragraphs + hard breaks | ✅ |
| HTML escaping (safe output) | ✅ |

## Install

Just download `md2html.py`. That's it.

```bash
# no pip, no setup
python md2html.py your_file.md
```

## Usage

```bash
# Print HTML to stdout
python md2html.py note.md

# Write to a file
python md2html.py note.md -o note.html

# Custom page title
python md2html.py note.md --title "My Notes" -o note.html

# Body fragment only (for embedding)
python md2html.py note.md --fragment

# No built-in CSS
python md2html.py note.md --no-css -o plain.html
```

## Example

Input (`doc.md`):

```markdown
# Hello

This is **bold** and `code`.

- one
- two
```

Output:

```html
<h1>Hello</h1>
<p>This is <strong>bold</strong> and <code>code</code>.</p>
<ul>
<li>one</li>
<li>two</li>
</ul>
```

## License

MIT — free to use, modify and ship.

---

### 👋 Like this tool?

If `md2html` saved you time, consider supporting my open-source work via
[爱发电 (afdian)](https://afdian.com/a/Zhiyilang). Every bit funds more
zero-dependency tools like this one. Thank you! ⭐
