#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2html.py - Minimal, dependency-free Markdown to HTML converter.

Pure Python standard library. No pip install required. Works on Windows / macOS / Linux / Android (Termux).

Supports:
  - Headings  # .. ######
  - Bold **text** / __text__, Italic *text* / _text_, Inline code `code`
  - Links [text](url) and bare URLs (http/https)
  - Unordered lists - / * / + and ordered lists 1.
  - Fenced code blocks ``` ... ```
  - Blockquotes > text
  - Horizontal rules --- / ***
  - Paragraphs and hard line breaks (two trailing spaces)
  - HTML escaping for safety

Usage:
  python md2html.py input.md                  -> prints HTML to stdout
  python md2html.py input.md -o out.html      -> writes file
  python md2html.py input.md --title "Doc" --css  -> full HTML document
  python md2html.py input.md --fragment      -> body only (no <html> wrapper)

License: MIT
"""
import sys
import re
import html
import argparse

VERSION = "1.0.0"


def escape(text):
    return html.escape(text, quote=True)


def _inline(text):
    """Render inline markdown (bold, italic, code, links)."""
    # Protect inline code first
    codes = []

    def stash_code(m):
        codes.append(m.group(1))
        return "\x00CODE%d\x00" % (len(codes) - 1)

    text = re.sub(r"`([^`]+)`", stash_code, text)

    # Links [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: '<a href="%s">%s</a>' % (escape(m.group(2)), escape(m.group(1))),
        text,
    )

    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"<em>\1</em>", text)

    # Bare URLs
    text = re.sub(
        r"(?<![\"'>])(https?://[^\s<]+)",
        lambda m: '<a href="%s">%s</a>' % (escape(m.group(1)), escape(m.group(1))),
        text,
    )

    # Restore code
    def restore(m):
        idx = int(m.group(1))
        return "<code>%s</code>" % escape(codes[idx])

    text = re.sub(r"\x00CODE(\d+)\x00", restore, text)
    return text


def convert(md, title="Document", css=True, fragment=False):
    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)

    list_stack = []  # stack of ('ul'|'ol', indent)

    def close_lists():
        while list_stack:
            tag, _ = list_stack.pop()
            out.append("</%s>" % tag)

    while i < n:
        line = lines[i]

        # Fenced code block
        m = re.match(r"^\s*```(.*)$", line)
        if m:
            lang = m.group(1).strip()
            buf = []
            i += 1
            while i < n and not re.match(r"^\s*```\s*$", lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            close_lists()
            cls = ' class="language-%s"' % escape(lang) if lang else ""
            code = escape("\n".join(buf))
            out.append("<pre><code%s>%s</code></pre>" % (cls, code))
            continue

        # Blank line
        if not line.strip():
            close_lists()
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*([-*_])\s*(\1\s*){2,}$", line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, _inline(m.group(2).strip()), level))
            i += 1
            continue

        # Blockquote
        if re.match(r"^\s*>\s?", line):
            close_lists()
            buf = []
            while i < n and re.match(r"^\s*>\s?", lines[i]):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % _inline(" ".join(buf)))
            continue

        # List item
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if m:
            indent = len(m.group(1))
            ordered = bool(re.match(r"\d+\.", m.group(2)))
            tag = "ol" if ordered else "ul"

            # Adjust list stack by indent
            if list_stack and list_stack[-1][1] < indent:
                # nested: open new at same level relative
                if list_stack[-1][0] != tag:
                    close_lists()
                    list_stack.append((tag, indent))
                    out.append("<%s>" % tag)
            elif not list_stack:
                list_stack.append((tag, indent))
                out.append("<%s>" % tag)
            elif list_stack[-1][0] != tag:
                close_lists()
                list_stack.append((tag, indent))
                out.append("<%s>" % tag)

            out.append("<li>%s</li>" % _inline(m.group(3)))
            i += 1
            continue

        # Paragraph (collect consecutive non-blank, non-special lines)
        close_lists()
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(
            r"^\s*(#{1,6}\s|>\s?|[-*+]\s|\d+\.\s|```|\s*([-*_])\s*(\1\s*){2,}$)",
            lines[i],
        ):
            buf.append(lines[i])
            i += 1
        para = " ".join(buf).strip()
        # hard break on two trailing spaces
        para = para.replace("  \n", "<br>\n")
        out.append("<p>%s</p>" % _inline(para))

    close_lists()

    body = "\n".join(out)
    if fragment:
        return body

    style = (
        "<style>\n"
        "body{max-width:760px;margin:40px auto;padding:0 20px;"
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,"
        "'Helvetica Neue',Arial,'PingFang SC','Microsoft YaHei',sans-serif;"
        "line-height:1.7;color:#24292f;background:#fff}\n"
        "code{background:#f6f8fa;padding:.2em .4em;border-radius:6px;"
        "font-family:Consolas,Menlo,monospace;font-size:85%}\n"
        "pre{background:#f6f8fa;padding:16px;border-radius:8px;overflow:auto}\n"
        "pre code{background:none;padding:0}\n"
        "a{color:#0969da;text-decoration:none}a:hover{text-decoration:underline}\n"
        "blockquote{border-left:4px solid #d0d7de;margin:0;padding:0 16px;color:#57606a}\n"
        "h1,h2{border-bottom:1px solid #d8dee4;padding-bottom:.3em}\n"
        "hr{border:none;border-top:1px solid #d8dee4;margin:24px 0}\n"
        "img{max-width:100%}\n"
        "</style>\n"
        if css
        else ""
    )
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        "<title>%s</title>\n%s</head>\n<body>\n%s\n</body>\n</html>\n"
        % (escape(title), style, body)
    )


def main():
    ap = argparse.ArgumentParser(
        description="Dependency-free Markdown to HTML converter."
    )
    ap.add_argument("input", help="input .md file")
    ap.add_argument("-o", "--output", help="write to file instead of stdout")
    ap.add_argument("--title", default="Document", help="HTML <title>")
    ap.add_argument("--no-css", action="store_true", help="omit built-in CSS")
    ap.add_argument("--fragment", action="store_true", help="output body only")
    ap.add_argument("--version", action="version", version="md2html %s" % VERSION)
    args = ap.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            md = f.read()
    except OSError as e:
        sys.stderr.write("error: %s\n" % e)
        sys.exit(1)

    result = convert(
        md,
        title=args.title,
        css=not args.no_css,
        fragment=args.fragment,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        sys.stderr.write("written: %s (%d bytes)\n" % (args.output, len(result)))
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
