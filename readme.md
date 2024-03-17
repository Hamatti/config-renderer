# config-renderer

config-renderer is a Python CLI utility that reads a configuration file and optional CSS stylesheet and renders a nice looking HTML page from it.

See example documentation page in https://hamatti.github.io/config-renderer/

## Motivation

I like to document my configuration files well so I can understand and remember them well. I also like sharing my configurations in the web and I wanted a way to write configuration files that are human-readable and computer-understandable. With this renderer, I can run a single command to generate an HTML page from the source file so I don't need to maintain two separate documentations.

## Usage

You can run config-renderer with `pipx run config-renderer`

```
Configuration renderer

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
```

## Custom markup

First line needs to start with `# TITLE` that is turned into `<h1>TITLE</h1>` and `<title>TITLE</title>`

| Markup                         | Output                                                  | Notes                                                              |
| ------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------------ |
| `# [Heading 2]`                | `<h2>Heading 2</h2>`                                    |                                                                    |
| `#> class`                     | `<div class="class>`                                    |                                                                    |
| `#<`                           | `</div>`                                                |                                                                    |
| `#~`                           | (nothing, lines are ignored)                            |                                                                    |
| `# anything else`              | `<p>anything else</p>`                                  | Multiple consecutive lines with # are combined into same paragraph |
| `any line not starting with #` | `<pre><code>any line not starting with #</pre></code>`  | Multiple consecutive lines are combined into same code block       |
| `[Website title](website url)` | `<a href="website url">Website title</a>`               |                                                                    |
| `https://example.com`          | `<a href="https://example.com">https://example.com</a>` |                                                                    |

## Custom styling

You can provide your own CSS file with `--style FILENAME` option. The styles get added to the `<head>` of the document so the end result is self-standing package.

The tags are marked with following classes:

| Tag        | Class                   |
| ---------- | ----------------------- |
| `h1`, `h2` | configuration-heading   |
| `a`        | configuration-link      |
| `pre`      | configuration-pre       |
| `p`        | configuration-paragraph |
| `div`      | configuration-container |

You can customize these with the `--class-prefix PREFIX` option where `PREFIX` replaces `configuration` in above examples.

## Example

File called `example.conf`

```
#+ Juhis' tmux configuration

# [Install plugins]
#~ A list of the plugins

# [Tmux Plugin Manager](https://github.com/tmux-plugins/tpm) to install other plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-resurrect'
```

ran with

```
pipx run config-renderer.py example.conf
```

results in

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Juhis' tmux configuration</title>
    <style></style>
  </head>
  <body>
    <main>
      <h1>Juhis' tmux configuration</h1>
      <h2>Install plugins</h2>
      <p>
        <a href="https://github.com/tmux-plugins/tpm">Tmux Plugin Manager</a> to
        install other plugins
      </p>
      <pre><code><span>set -g @plugin 'tmux-plugins/tpm'</span>
<span>set -g @plugin 'tmux-plugins/tmux-resurrect'</span>
</code></pre>
    </main>
  </body>
</html>
```
