# Conventional Commit Decision Tree

## 1. Does the change add new user-facing functionality?

Yes → feat

Example: feat(auth): add two-factor authentication

No → go to step 2.

## 2. Does the change fix a bug?

Yes → fix

Example: fix(parser): handle null input correctly

No → go to step 3.

## 3. Does the change improve internal code structure/design without changing behavior?

Yes → refactor

Example: refactor(globber): make Config explicit for future extension

No → go to step 4.

## 4. Is the change about tooling, build system, CI/CD, or devops scripts?

Yes → chore

Example: chore(justfile): migrate from Makefile to Justfile

No → go to step 5.

## 5. Is the change about documentation only?

Yes → docs

Example: docs(readme): add installation instructions

No → go to step 6.

## 6. Is the change about formatting, whitespace, or style (no logic change)?

Yes → style

Example: style(core): reformat code with Prettier

No → go to step 7.

## 7. Is the change about performance optimization?

Yes → perf

Example: perf(query): improve search speed by caching results

No → go to step 8.

## 8. Is the change about tests?

Yes → test

Example: test(globber): add unit tests for Config subclass

No → go to step 9.

## 9. Is the change about dependencies or version bumps?

Yes → chore(deps)

Example: chore(deps): update lodash to v5.0.0

No → default to chore for miscellaneous non-code changes.

## Quick Summary

- feat → new functionality
- fix → bug fix
- refactor → code restructuring without behavior change
- chore → tooling/devops/build/deps
- docs → documentation only
- style → formatting only
- perf → performance improvements
- test → test-related changes
