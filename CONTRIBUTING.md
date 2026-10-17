# Contributing

Empyrical Reloaded accepts bug, security, and compatibility fixes. Direct new feature
requests to the current ML4T libraries. The [shared contribution guide](https://github.com/ml4t/ecosystem/blob/main/CONTRIBUTING.md)
describes repository ownership and reporting requirements; the requirements below
apply to contributions here.

## One problem per issue and pull request

Search existing issues before opening one. Include the package version, environment,
expected and observed behavior, and a small, complete reproduction for a bug.
Discuss substantial changes in the owning issue before implementing them. Follow
the shared guide's private reporting process for suspected vulnerabilities.

Use [GitHub Flow](https://guides.github.com/introduction/flow/): create a branch,
commit the change, and [open a focused pull request](https://github.com/stefan-jansen/empyrical-reloaded/compare/)
with a closing reference such as `Closes #123`. Keep unrelated fixes, refactors,
and formatting changes separate. Automated dependency updates and administrative
metadata changes do not require a separate issue.

For a bug fix, include a regression through the public API or affected workflow that
fails on the relevant base revision and passes with the fix. Report both revisions,
commands, and results. Correct verified numerical defects even when existing outputs
change. Agree on changes to intended definitions, annualization, sign conventions,
or defaults in the owning issue, and document their compatibility impact.

## Verification

Run the relevant native checks and report their results, including existing failures.
The test entry point is `uv run --extra test pytest tests/`; the CI version matrix
and tox configuration are defined in `pyproject.toml` and `.github/workflows/ci_tests.yml`.
CI also checks flake8 and Black 24.4.2. Match those checks rather than introducing
another formatter or test matrix in a focused fix.

For documentation changes, run `uv run --extra doc make -C docs html` and inspect
the affected output. Preserve the existing README and Sphinx API documentation.
A documentation-only change does not require an artificial numerical regression.
Report missing dependency or runner evidence explicitly rather than claiming a pass.

## AI assistance and accountability

Disclose whether you used AI tools and which parts they helped produce. Review and
test the submission yourself, and be able to explain the code, evidence, and review
responses. An automated reply does not replace understanding a review question.

Wait for feedback on your first focused contribution before opening a large series
of similar PRs. Maintainers may ask for bundled changes to be split or incomplete
submissions to be completed, or close them pending a focused resubmission.
