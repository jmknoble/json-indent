# https://www.pyinvoke.org/
from invoke import call, task


@task
def install_mark_toc(context):
    """Install mark-toc tool with uv"""
    context.run("uv tool install mark-toc")


@task
def install_yamllint(context):
    """Install yamllint tool with uv"""
    context.run("uv tool install yamllint")


@task(pre=[install_yamllint])
def yamllint(context):
    """Run yamllint"""
    context.run("uv tool run yamllint .")


@task
def isort_python(context, fix=True):
    """Sort imports in Python source files"""
    fix_flag = "--fix" if fix else ""
    context.run(f"uv run ruff check --config 'lint.select = [\"I\"]' {fix_flag}")


@task
def check_python(context, fix=False):
    """Run lint checks on Python source files"""
    fix_flag = "--fix" if fix else ""
    context.run(f"uv run ruff check {fix_flag}")


@task
def format_python(context, fix=True):
    """Automatically format Python source files"""
    diff_flag = "" if fix else "--diff"
    context.run(f"uv run ruff format {diff_flag}")


@task(
    pre=[
        yamllint,
        call(isort_python, fix=False),
        check_python,
        call(format_python, fix=False),
    ]
)
def lint(context):
    """Run all lint checks"""
    pass


@task(pre=[install_mark_toc])
def mark_toc(context):
    """Generate tables of contents for Markdown documents"""
    context.run(r"""
find . \( \
    -type d \
    \( -name .git -o -name .ruff_cache -o -name .venv \) \
    -prune \
\) -o \( \
    -type f \
    -name '*.md' \
    -exec uvx mark-toc --heading-level 2 --skip-level 1 --pre-commit '{}' ';' \
\)
""")


@task(pre=[lint, mark_toc])
def checks(context):
    """Run all checks"""
    pass


@task
def clean_docs(context):
    """Clean up documentation artifacts"""
    context.run("rm -r -f docs/build docs/sphinx")


@task(pre=[clean_docs])
def clean(context):
    """Clean up build artifacts, etc."""
    context.run("rm -r -f build dist")
    context.run("rm -r -f .eggs *.egg-info")
    context.run("find . -depth -type d -name '__pycache__' -exec rm -r -f '{}' ';'")
    context.run("find . -type f -name '*.py[co]' -exec rm -f '{}' ';'")


@task
def build(context, clean=False):
    """Build Python source and wheel distributions"""
    context.run("uv build --no-cache")


@task(iterable=["test_name_pattern"])
def tests(
    context, test_name_pattern, quiet=False, failfast=False, catch=False, buffer=False
):
    """Run tests using `python3 -m unittest discover`"""
    unittest_args = []
    unittest_args.append("-q" if quiet else "-v")
    if failfast:
        unittest_args.append("--failfast")
    if catch:
        unittest_args.append("--catch")
    if buffer:
        unittest_args.append("--buffer")
    if test_name_pattern:
        unittest_args.append("-k")
        unittest_args.extend(test_name_pattern)
    context.run(
        "uv run python3 -m unittest discover -s tests -t . {}".format(
            " ".join(unittest_args)
        )
    )


@task
def version(
    context, bump=False, dry_run=True, go=False, patch=False, minor=False, major=False
):
    """Show or update this project's current version"""
    args = []
    if not bump:
        args.append("show")
    else:
        args.append("update")
        if go:
            dry_run = False  # alias for --no-dry-run
        if dry_run:
            args.append("--dry")
        if major:
            args.append("--major")
        if minor:
            args.append("--minor")
        if patch:
            args.append("--patch")
    context.run("uv run bumpver {}".format(" ".join(args)))
