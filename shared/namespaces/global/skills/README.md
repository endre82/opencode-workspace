# OpenCode Skills

This directory contains shared OpenCode skills that provide specialized instructions and workflows for specific tasks.

## What are Skills?

Skills in OpenCode are reusable instruction sets that provide:
- Specialized workflows
- Domain-specific knowledge
- Bundled scripts and tools
- Code templates
- Best practices guidance

## Directory Structure

Each skill should have its own subdirectory:

```
skills/
├── refactoring/
│   ├── SKILL.md         # Skill instructions (required)
│   ├── scripts/         # Helper scripts
│   ├── templates/       # Code templates
│   └── README.md        # Documentation
│
├── debugging/
│   ├── SKILL.md
│   ├── checklists/      # Debugging checklists
│   └── README.md
│
└── optimization/
    ├── SKILL.md
    ├── benchmarks/      # Benchmark scripts
    └── README.md
```

## Creating a Skill

1. **Create directory**:
   ```bash
   mkdir -p skills/my-skill
   ```

2. **Create SKILL.md** (required):
   ```markdown
   # My Skill Name
   
   ## Purpose
   Brief description of what this skill helps with.
   
   ## When to Use
   Situations where this skill is most useful.
   
   ## Workflow
   1. Step-by-step instructions
   2. Commands to run
   3. Checks to perform
   
   ## Examples
   Concrete examples of using this skill.
   
   ## Best Practices
   Tips and recommendations.
   ```

3. **Add supporting resources**:
   - Scripts in `scripts/`
   - Templates in `templates/`
   - Documentation in `README.md`

4. **Test the skill**:
   ```bash
   # In OpenCode
   opencode load-skill /path/to/skill
   ```

## Example Skills

### refactoring

Guides through code refactoring:
- Identifies code smells
- Suggests refactoring patterns
- Provides templates for common refactorings
- Includes before/after examples

### debugging

Systematic debugging approach:
- Step-by-step debugging workflow
- Common bug patterns
- Debugging tool usage
- Log analysis techniques

### optimization

Performance optimization guidance:
- Profiling instructions
- Common optimization patterns
- Benchmark scripts
- Performance testing

### database-migration

Database schema migration:
- Migration planning workflow
- SQL scripts for common patterns
- Rollback procedures
- Testing checklists

## Best Practices

1. **Clear Instructions**: SKILL.md should be detailed and actionable
2. **Self-Contained**: Include all necessary scripts and templates
3. **Examples**: Provide concrete usage examples
4. **Testing**: Test skill in real scenarios before publishing
5. **Versioning**: Use Git to track changes

## Using Skills in OpenCode

Skills can be loaded via the OpenCode skill system:

```bash
# Load a skill from namespace
opencode load-skill /home/dev/.opencode/namespaces/global/skills/refactoring

# Or in conversation
"Load the refactoring skill and help me refactor this code"
```

## Skill Structure Guidelines

### SKILL.md Format

```markdown
# [Skill Name]

## Purpose
One-sentence description of the skill's purpose.

## When to Use
- Bullet points of when this skill is most helpful
- Specific scenarios where it applies

## Prerequisites
- Required knowledge or setup
- Dependencies or tools needed

## Workflow

### Step 1: [Step Name]
Detailed instructions for this step.

### Step 2: [Step Name]
Detailed instructions for this step.

## Commands

```bash
# Example commands to run
command --option argument
```

## Examples

### Example 1: [Scenario]
Concrete example with inputs and expected outputs.

## Tips and Best Practices
- Important tips
- Common pitfalls to avoid
- Best practices

## References
- Links to relevant documentation
- Related skills or resources
```

### Bundled Scripts

If your skill includes scripts:

```
skills/my-skill/
├── SKILL.md
└── scripts/
    ├── setup.sh         # Setup script
    ├── analyze.py       # Analysis script
    └── README.md        # Script documentation
```

Make scripts executable and document their usage.

### Templates

If your skill includes code templates:

```
skills/my-skill/
├── SKILL.md
└── templates/
    ├── component.tsx    # React component template
    ├── test.spec.ts     # Test template
    └── README.md        # Template documentation
```

## Contributing

When adding new skills to the global namespace:

1. Create skill following the structure above
2. Test in your local environment
3. Document all workflows and examples
4. Submit for review (if using Git workflow)
5. Add to global namespace once approved

## Troubleshooting

### Skill not loading

1. Verify SKILL.md exists and is properly formatted
2. Check namespace is mounted correctly
3. Ensure file permissions are correct (755 for dirs, 644 for files)

### Skill instructions unclear

1. Add more detailed steps to SKILL.md
2. Include concrete examples
3. Add troubleshooting section to the skill
4. Test with someone unfamiliar with the domain
