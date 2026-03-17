# OpenCode Namespace System

This directory contains shared agents, skills, workflows, and context that can be mounted into multiple OpenCode environments.

## Directory Structure

```
namespaces/
├── global/              # Company-wide resources (available to all environments)
│   ├── agents/         # Shared OpenCode agents
│   ├── skills/         # Shared OpenCode skills
│   ├── workflows/      # Workflow templates and guides
│   └── context/        # Shared knowledge bases and documentation
│
└── team-*/             # Team-specific namespaces (future expansion)
    ├── agents/
    ├── skills/
    ├── workflows/
    └── context/
```

## How Namespaces Work

### Mounting in Environments

Namespaces are mounted read-only into environments via Docker volumes:

```yaml
# In docker-compose.yml
volumes:
  - ../../shared/namespaces/global:/home/dev/.opencode/namespaces/global:ro
```

### Configuration

Each environment's `.env` file controls which namespaces are mounted:

```bash
# Enable/disable namespace mounting
MOUNT_NAMESPACE_GLOBAL=true
NAMESPACE_GLOBAL_DIR=../../shared/namespaces/global
```

## Using Namespaces

### For Agents

Place agent definitions in `global/agents/<agent-name>/`:

```
global/agents/code-reviewer/
├── agent.yaml           # Agent configuration
├── prompts/             # Custom prompts
└── README.md           # Agent documentation
```

OpenCode will auto-discover agents in mounted namespaces.

### For Skills

Place skill definitions in `global/skills/<skill-name>/`:

```
global/skills/refactoring/
├── SKILL.md            # Skill instructions
├── scripts/            # Bundled scripts
└── templates/          # Code templates
```

Skills can be loaded via the OpenCode skill system.

### For Workflows

Store workflow templates and guides in `global/workflows/`:

```
global/workflows/
├── pr-checklist.md     # Pull request checklist
├── deployment.md       # Deployment guide
└── code-review.md      # Code review workflow
```

Reference these in your development process.

### For Context

Store shared knowledge in `global/context/`:

```
global/context/
├── architecture.md     # System architecture docs
├── coding-standards.md # Team coding standards
└── onboarding.md       # Onboarding guide
```

Use these as reference material for OpenCode conversations.

## Version Control

**Recommended:** Initialize each namespace as a Git repository:

```bash
cd shared/namespaces/global
git init
git add .
git commit -m "Initial namespace structure"
```

Benefits:
- Track who added/modified agents and skills
- Rollback broken changes
- Branch-based development (test new agents before merging)
- Share across teams via Git remotes

## Creating Team Namespaces

To create team-specific namespaces:

1. Create directory structure:
   ```bash
   mkdir -p shared/namespaces/team-backend/{agents,skills,workflows,context}
   ```

2. Update environment `.env`:
   ```bash
   NAMESPACE_TEAM=team-backend
   ```

3. Add volume mount in `docker-compose.yml`:
   ```yaml
   volumes:
     - ../../shared/namespaces/team-backend:/home/dev/.opencode/namespaces/team:ro
   ```

## Best Practices

1. **Read-Only Mounts**: Always mount namespaces as read-only (`:ro`) to prevent accidental modifications

2. **Documentation**: Include README.md in each agent/skill directory explaining its purpose and usage

3. **Testing**: Test new agents/skills in a development environment before adding to global namespace

4. **Naming Conventions**:
   - Use lowercase with hyphens: `code-reviewer`, `test-writer`
   - Be descriptive: `api-designer` not `designer`
   - Avoid generic names: `python-linter` not `linter`

5. **Versioning**: Use Git tags for stable releases:
   ```bash
   git tag -a v1.0 -m "Stable release with code-reviewer and test-writer"
   ```

6. **Access Control**: Use Git permissions to control who can modify global namespace

## Examples

See the individual README files in each subdirectory for specific examples:

- [Agents README](global/agents/README.md)
- [Skills README](global/skills/README.md)
- [Workflows README](global/workflows/README.md)
- [Context README](global/context/README.md)

## Troubleshooting

### Namespace not visible in environment

1. Check `.env` has `MOUNT_NAMESPACE_GLOBAL=true`
2. Verify volume is mounted: `docker compose exec <container> ls /home/dev/.opencode/namespaces/global`
3. Restart container: `docker compose restart`

### Permission errors

Ensure namespace directory has correct permissions:
```bash
chmod -R 755 shared/namespaces/global
```

### Changes not reflected

Namespaces are mounted at container startup. Restart the container to see changes:
```bash
docker compose restart
```
