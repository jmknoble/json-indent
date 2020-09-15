# json-indent

This is a simple Python-based tool for parsing/indenting/formatting JSON.

Python's `json` module actually contains such a tool; it's even simpler and is
missing twiddles for specifying the amount of indent, whether to (re)compact,
and whether to sort keys when parsing.

**json-indent** can be useful:

- On the command-line
- From within [Vim][] or similar editors
- As a [pre-commit][] hook

([js-beautify][] is another such tool; it can parse JavaScript as well as
JSON, but it has no built-in [pre-commit][] hook).


[begintoc]: #

# Contents

* [Requirements](#requirements)
* [Installing](#installing)
* [How to Use](#how-to-use)
    * [Quickstart](#quickstart)
* [Advanced Topics](#advanced-topics)
    * [Pre-Commit Hook](#pre-commit-hook)
    * [Integration with Vim](#integration-with-vim)
* [References](#references)

[endtoc]: #


## Requirements

- A [Python] interpreter, version 3.6 or later (version 2.7 support is
  deprecated, but may still work)


## Installing

It is recommended to install **json-indent** either:

- In its own virtual environment (using [virtualenv][], [venv][], or
  [conda][]), or
- As a [pre-commit hook](#pre-commit-hook)

To install in a virtual environment, first activate your virtual environment,
then:

    python setup.py install


## How to Use

For a summary of all the available options:

    python -m json_indent --help

or:

    /path/to/json-indent --help

> :star: ***HINT:***
>
> _See [How to Run Your Python Scripts][run-python-scripts] for details on the
> different ways to run **json-indent**._


### Quickstart

To read JSON from a file, parse it, and write it to the standard output:

    python -m json_indent input.json

To write to a file instead:

    python -m json_indent -o output.json input.json

To read from the standard input, you can use `-` as the filename:

    python -m json_indent -o - -

Or simply:

    python -m json_indent

To modify a file in place:

    python -m json_indent --inplace input.json

To display `json-indent`'s version:

    python -m json_indent --version

See the command-line help for more options, including:

- Indent size
- "Compact" mode
- Key sorting


## Advanced Topics

### Pre-Commit Hook

**json-indent** has support for the [pre-commit][] framework for running tools
before committing to your git project.  The hook will:

1. Parse your JSON files and emit messages about any errors it encounters.
2. Format and indent your JSON files according to the `--indent`, `--compact`,
    and `--sort-keys` options you supply (or their default values if you don't
    supply one).

To add a hook for **json-indent** to your project, use the following YAML in
your project's [.pre-commit-config.yaml](examples/.pre-commit-config.yaml):

```yaml
  - repo: https://github.com/jmknoble/json-indent
    rev: v2.2.0
    hooks:
      - id: json-indent
```

> :gear: ***HOW IT WORKS:***
>
> _Under the hood this uses a [.pre-commit-hooks.yaml](.pre-commit-hooks.yaml)
> file in the root of the Git project to define the parameters of the
> pre-commit hook._
>
> _Key info:_
>
> - _**json-indent** must accept multiple input files on the command line._
> - _The `--inplace` option is needed in order to automatically indent JSON
>   source files._


### Integration with Vim

You can use **json-indent** from within [Vim][] to format JSON directly in
your editing session.

To enable this functionality, you can add the following to your [vimrc][]
file:

```viml
""""""""""""""""""""""""""""""""""""""""
" JSON parsing/indenting
" https://github.com/jmknoble/json-indent
"
" Normal mode
"
" Compact JSON stanza starting at current character (uses '%' to move to matching brace)
nmap <Leader>jc :%!json-indent -c
nmap <Leader>JC <Leader>jc
"
" Parse/indent JSON stanza contained in current line
nmap <Leader>jp 0!$json-indent<CR>j
nmap <Leader>JP <Leader>jp
"
" Parse/indent JSON stanza contained in current line with sorted keys
nmap <Leader>js 0!$json-indent -s<CR>j
nmap <Leader>JS <Leader>js
"
" Visual mode
"
" Compact JSON stanza contained in current selection
vmap <Leader>jc !json-indent -c<CR>j
vmap <Leader>JC <Leader>jc
"
" Parse/indent JSON stanza contained in current selection
vmap <Leader>jp !json-indent
vmap <Leader>JP <Leader>jp
"
" Parse/indent JSON stanza contained in current selection with sorted keys
vmap <Leader>js !json-indent -s<CR>j
vmap <Leader>JS <Leader>js
""""""""""""""""""""""""""""""""""""""""
```

> :star: ***HINTS:***
>
> _This uses the `!`_command_ feature to run an external command as a
> [filter][]._
>
> _Use the Vim command `:help mapleader` (or see [mapleader][]) for an
> explanation of `<Leader>`._


## References

- [Python][]:
    - [Virtual environments with virtualenv][virtualenv]
    - [Virtual environments with venv][venv]
    - [Virtual environments with Anaconda][conda]
    - [How to Run Your Python Scripts][run-python-scripts]
- [pre-commit][]
- [Opinionated Autoformatting][]:
    - [Black][]
    - [Prettier][]
- [Vim][]:
    - [Intro to vimrc][vimrc]
    - [Vim filters][filter]
    - [Vim's Leader key][mapleader]
- [js-beautify][]


 [Python]: https://www.python.org/
 [virtualenv]: https://virtualenv.pypa.io/en/latest/
 [venv]: https://docs.python.org/3/library/venv.html
 [conda]: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
 [run-python-scripts]: https://realpython.com/run-python-scripts/

 [pre-commit]: https://pre-commit.com/

 [Opinionated Autoformatting]: https://blog.seangransee.com/2018/09/opinions-on-opinionated-autoformatters/
 [Black]: https://black.readthedocs.io/en/stable/
 [Prettier]: https://prettier.io/

 [Vim]: http://www.vim.org/
 [vimrc]: https://vimhelp.org/usr_05.txt.html#vimrc-intro
 [filter]: https://vimhelp.org/change.txt.html#filter
 [mapleader]: https://vimhelp.org/map.txt.html#mapleader

 [js-beautify]: https://github.com/beautify-web/js-beautify
