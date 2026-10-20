"""Org-level governance tooling for the QM corpus.

A package so `uv run qm` has something to install. Every module here is also a
standalone script, and both facts matter: forks run `project-seed/ci/*.py` out
of the submodule with a plain interpreter and never install this, and the
workflows invoke scripts directly so a gate cannot fail for want of a venv.

Nothing in this package holds doctrine. Records hold doctrine; these read it.
"""
