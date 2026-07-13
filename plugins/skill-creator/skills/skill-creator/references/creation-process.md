# Skill Creation Process (Detailed)

Follow these steps in order, skipping only when clearly inapplicable.

## Step 1: Understand the Skill with Concrete Examples

Skip only when usage patterns are already clearly understood.

Use `AskUserQuestion` to gather feedback. Example questions for an `image-editor` skill:
- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

Avoid asking too many questions at once. Conclude when functionality is clear.

## Step 2: Research on the Internet

Effective skills reflect real professional workflows. Activate `/docs-seeker` for documentation.

Use multiple `WebFetch` tools and `Explore` subagents in parallel for large volumes of URLs.

Activate `/research` to find:
- Best practices & industry standards
- Existing CLI tools (via `npx`, `bunx`, `pipx`) and usage patterns
- Workflows, success case studies, common patterns, edge cases

Write research reports to use in the next step.

## Step 3: Plan Reusable Skill Contents

Analyze each concrete example:
1. Consider how to execute it from scratch
2. Prefer existing CLI tool execution over writing custom code
3. Identify what scripts, references, and assets help when repeating these workflows
4. Check the skills catalog to avoid duplicating existing functionality

**Examples:**
- `pdf-editor` → rotating PDFs requires rewriting code → `scripts/rotate_pdf.py`
- `frontend-webapp-builder` → same HTML/React boilerplate → `assets/hello-world/` template
- `big-query` → re-discovering table schemas → `references/schema.md`

Produce a list of reusable resources to include.

Scripts must: respect `.env` resolution order (see `references/skill-anatomy.md`), have tests, and pass all tests.

## Step 4: Initialize the Skill

Skip if the skill already exists (go to Step 5).

Run the init script:
```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script creates the skill directory, generates a `SKILL.md` template with frontmatter and TODO placeholders, and adds example resource directories (`scripts/`, `references/`, `assets/`).

After initialization, customize or remove generated example files as needed.

## Step 5: Edit the Skill

The skill is created for another Claude instance. Include information that is beneficial and non-obvious.

### Start with Reusable Skill Contents

Implement `scripts/`, `references/`, and `assets/` first. Some steps may require user input (e.g., brand assets for a `brand-guidelines` skill). Delete example files/dirs not needed.

### Update SKILL.md

Write in **imperative/infinitive form** (verb-first, objective, instructional language).

Answer these questions:
1. What is the purpose of this skill?
2. When should it be used?
3. How should Claude use it? Reference all reusable resources so Claude knows about them.

## Step 5 (cont.): Package the Skill

```bash
scripts/package_skill.py <path/to/skill-folder>
# With output dir:
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script validates first (frontmatter, naming, structure, description ≤200 chars, resource references), then creates a distributable zip. Fix any validation errors and re-run.

## Step 6: Iterate

After testing, incorporate user feedback:
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Notice token usage and performance
4. Identify updates to SKILL.md or bundled resources
5. Implement changes and test again
