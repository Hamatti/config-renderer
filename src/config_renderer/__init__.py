"""Configuration renderer

Renders a configuration file into an HTML page based on custom minimal markup language.

Supports any config file where comments start with #.

Usage:
    config-renderer.py <configfile> [-s <stylesheet> | -b] [-o <outfile>] [--class-prefix <prefix>]

Options:
    -s --style <file>  Filename of a stylesheet to be added
    -b --body-only  Don't add html, head and body elements. Meant for embedding to existing sites.
    -o --output <file>  Filename for where to write the file [default: config.html]
    --class-prefix <prefix>  Customize CSS class prefix [default: configuration]

Markup:
    - First line should start with "# HEADING" where heading gets added to <h1> and <title>
    - # [Heading 2] -> <h2>Heading 2</h2>
    - #> class -> <div class="class">
    - #< <- </div>
    - #~ Any line starting with #~ is ignored by the parser.
    - # Any line starting with a # that does not match any of above, will be added into a <p>paragraph</p>. An empty line, a config line or any of the above will wrap up the paragraph.
"""

import re
import sys
from docopt import docopt

# Match a "# [Heading]" line and capture the text inside the square brackets
HEADING_PATTERN = r"^# ?\[(.*)\]$"

# Match URLs that are not prepended by "(" (to avoid double rendering Markdown links)
URL_PATTERN = r"(?<!\()https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"

# Match Markdown style URL pattern ([Title](url))
MARKDOWN_URL_PATTERN = r"\[(.*)\]\((.*)\)"

LINE_BREAK = "\n"
EMPTY_LINE = ""


def render_isolated_link(match, class_prefix):
    """re.sub callable to replace an isolated link with an HTML anchor tag"""
    url = match.group()
    return f'<a class="{class_prefix}-link" href="{url}">{url}</a>'


def render_markdown_link(match, class_prefix):
    """re.sub callable to replace Markdown style link [title](url) with an HTML anchor tag"""
    title, url = match.groups()
    return f'<a class="{class_prefix}-link" href="{url}">{title}</a>'


def render_config_file(filename, class_prefix):
    """Renders HTML markup for a configuration file provided as argument"""
    try:
        output = []
        with open(filename, "r") as config:
            in_code_block = False
            in_paragraph_block = False

            title = next(config)[2:].strip()
            output.append(f'<h1 class="{class_prefix}-heading">{title}</h1>')

            for line in config:
                if (
                    line == LINE_BREAK or line == EMPTY_LINE
                ):  # Empty line, end tags if needed
                    if in_code_block:
                        output.append("</code></pre>")
                        in_code_block = False
                    elif in_paragraph_block:
                        output.append("</p>")
                        in_code_block = False
                elif line.startswith("#"):  # Markup
                    # End any code tags if open
                    if in_code_block:
                        output.append("</code></pre>")
                        in_code_block = False

                    # Match custom markup

                    # Ignore lines that start #~
                    if line.startswith("#~"):
                        continue

                    # Heading level 2
                    elif match := re.match(HEADING_PATTERN, line):
                        if in_paragraph_block:
                            output.append("</p>")
                            in_paragraph_block = False
                        output.append(
                            f'<h2 class="{class_prefix}-heading">{match.groups()[0]}</h2>'
                        )
                        in_paragraph_block = False

                    # <hr> divider
                    elif line.startswith("#=") or line.startswith("# ="):
                        if in_paragraph_block:
                            output.append("</p>")
                            in_paragraph_block = False
                        output.append('<hr class="{class_prefix}-divider" />')

                    # Start <div> tag
                    elif line.startswith("#> "):
                        if in_paragraph_block:
                            output.append("</p>")
                            in_paragraph_block = False
                        output.append(
                            f'<div class="{class_prefix}-container {line[3:]}">'
                        )

                    # End </div> tag
                    elif line.startswith("#<"):
                        if in_paragraph_block:
                            output.append("</p>")
                            in_paragraph_block = False
                        output.append("</div>")

                    # Add text to paragraph tags
                    else:
                        if not in_paragraph_block:
                            output.append(f'<p class="{class_prefix}-paragraph">')
                        line = line[1:].strip()
                        output.append(line)
                        in_paragraph_block = True

                # Code lines in configuration
                else:
                    if in_paragraph_block:
                        output.append("</p>")
                        in_paragraph_block = False
                    if in_code_block:
                        output.append(f"<span>{line.strip()}</span>")
                    else:
                        in_code_block = True
                        output.append(
                            f'<pre class="{class_prefix}-pre"><code><span>{line.strip()}</span>'
                        )

            # Close any code or paragraph tags that are still open
            if in_code_block:
                output.append("</code></pre>")
            elif in_paragraph_block:
                output.append("</p>")

            html = "\n".join(output)

            # Change URLs to anchor tags

            ## Using these two wrappers to pass class_prefix to the callable
            def isolated_callable_wrapper(match):
                return render_isolated_link(match, class_prefix)

            def markdown_callable_wrapper(match):
                return render_markdown_link(match, class_prefix)

            html = re.sub(URL_PATTERN, isolated_callable_wrapper, html)
            html = re.sub(MARKDOWN_URL_PATTERN, markdown_callable_wrapper, html)

            return title, html

    except FileNotFoundError:
        print(f"Error: could not open file '{filename}'")
        sys.exit(1)


def main():
    # Initialize arguments based on docstring
    arguments = docopt(__doc__, version="config-renderer 1.0")

    # Render HTML
    title, body = render_config_file(
        arguments["<configfile>"], class_prefix=arguments.get("--class-prefix")
    )

    # Read styles if passed with --style (or -s)
    styles = ""
    if stylesheet := arguments.get("--style"):
        try:
            with open(stylesheet, "r") as stylefile:
                styles = stylefile.read()
        except FileNotFoundError:
            print(f"Error: stylesheet file '{stylesheet}' not found")
            sys.exit(1)

    # If --body-only is provided, don't add styles and don't wrap body into html and body tags.
    if arguments.get("--body-only", False):
        html = body
    else:
        html = f"<!doctype html><html><head><title>{title}</title><style>{styles}</style></head><body><main>{body}</main></body></html>"

    # Get output filename
    output_filename = arguments.get("--output", "config.html")

    # Write HTML to the output file
    with open(output_filename, "w") as outfile:
        outfile.write(html)
        print(f"Successfully wrote the config html page to {output_filename}")
