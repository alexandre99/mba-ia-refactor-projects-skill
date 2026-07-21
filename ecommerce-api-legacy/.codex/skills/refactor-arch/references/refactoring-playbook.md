# Refactoring Playbook

Apply only transformations linked to proven findings.

1. **Dynamic SQL → parameterized repository query**
   - Before: concatenate request values into SQL.
   - After: repository method with placeholders/bind parameters.
2. **Hardcoded secret → runtime configuration**
   - Before: token/key literal in source.
   - After: environment-backed config that fails closed when required.
3. **Weak password handling → adaptive hashing**
   - Before: plaintext/Base64/custom hash.
   - After: established password hasher with verify function.
4. **God Class → composition root + controllers + services + repositories**
   - Move one responsibility at a time and preserve route contracts.
5. **Fat route → thin transport adapter**
   - Parse input, invoke controller/use case, map result.
6. **Multi-step writes → transaction**
   - Commit all state changes atomically; rollback on failure.
7. **Mutable global → injected dependency**
   - Replace global cache/counter with an interface owned by composition root.
8. **N+1 → join/eager/batch loading**
   - Fetch related data in bounded queries and map once.
9. **Duplicated validation → schema/domain validator**
   - Reuse named policies across create/update.
10. **Scattered errors → typed errors + central handler**
    - Keep internal details in logs and stable errors in responses.
11. **Deprecated API → documented modern equivalent**
    - Confirm installed version, migrate call, add regression coverage.

For each transformation: record before/after files, compatibility risk and validation command.