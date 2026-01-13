# Commit Message Style Guide for Tests

## Always use plural tests in commit subjects  

Even if you only add a single test, write tests.
This saves cognitive load for reviewers and keeps commit history consistent.

Example:

```text
test(searcher): add concurrent search tests for Sqlite3Searcher
```

Use concise, imperative verbs  
Prefer short, action‑oriented verbs like add, update, remove, fix.
Avoid longer or passive forms like Introduce, Implemented, Adding.

Example:

```text
test(upserter): add FTS trigger tests
```

Keep subjects short and clear  
Describe what changed, not how many.
Let the commit body explain details if needed.

### ✅ Good Examples

```text
test(api): add authentication tests
test(db): update migration tests for schema changes
test(searcher): remove obsolete FTS tests
```

### 🚫 Avoid

```text
test(searcher): Introduce a new test for Sqlite3Searcher
test(upserter): Added one test for triggers
```

👉 This way, your team doesn’t have to think about singular vs plural, and commit history stays clean and predictable.

## Commit Message Verb Guidelines

- Use concise, imperative verbs  
- Always write commit subjects as commands, not descriptions.

Examples: add, update, remove, fix, refactor, rename.

Avoid: added, introduces, implemented, adding.

### Keep verbs short and clear  

Prefer simple one‑word verbs over longer phrases.

- ✅ add tests for searcher  
- 🚫 introduce a new set of tests for searcher

Consistency across all commit types  
Whether it’s feat, fix, refactor, test, or docs, the verb style stays the same.

Example:

```text
feat(api): add user authentication endpoint
fix(db): update migration script for schema change
refactor(core): rename helper function for clarity
test(upserter): add FTS trigger tests
docs(readme): update installation instructions
```

Avoid passive or narrative tone  
Don’t write commit subjects like sentences or explanations.
✅ remove deprecated config option  
🚫 this commit removes a deprecated config option

✅ Good Examples

```text
feat(searcher): add Sqlite3Searcher implementation
fix(upserter): update trigger logic for FTS
refactor(test/upserter): rename helper for clarity
test(searcher): add concurrent search tests
docs(contributing): update commit message guidelines
```

🚫 Avoid

```text
feat(searcher): Introduced Sqlite3Searcher as implementation
fix(upserter): Fixed trigger logic
refactor(test/upserter): Added docstring
test(searcher): Adding one test
docs(contributing): This commit updates guidelines
```

👉 This way, every commit subject is short, imperative, and consistent, which makes your history easy to scan and understand.
