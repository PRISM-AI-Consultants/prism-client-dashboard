# Workflow Conventions

All workflows in this directory follow these shared conventions:

## Structure

Every workflow file must include:
1. **Purpose** — One sentence describing what the workflow accomplishes
2. **Inputs** — Parameters the workflow requires
3. **Steps** — Ordered list referencing agents and/or tools by name
4. **Outputs** — What the workflow produces
5. **Error Handling** — How failures in each step are managed

## Naming

- Files use `kebab-case` with verb-noun format (e.g., `generate-report.md`)
- Workflows are stateless across runs; state is passed via context or memory files

## Execution

- Steps are executed sequentially unless marked as parallelizable
- Each step references tools or agents using `[Tool: name]` or `[Agent: name]` syntax
- On failure, follow the error handling rules defined in the workflow or fall back to the framework defaults in CLAUDE.md
