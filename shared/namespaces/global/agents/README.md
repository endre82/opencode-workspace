# OpenCode Agents

This directory contains shared OpenCode agent definitions that can be used across multiple environments.

## What are Agents?

Agents in OpenCode are specialized AI assistants configured for specific tasks. They have:
- Custom prompts and instructions
- Specific tool access
- Predefined workflows
- Specialized knowledge

## Directory Structure

Each agent should have its own subdirectory:

```
agents/
├── code-reviewer/
│   ├── agent.yaml       # Agent configuration
│   ├── prompts/         # Custom prompts
│   └── README.md        # Documentation
│
├── test-writer/
│   ├── agent.yaml
│   └── README.md
│
└── docs-generator/
    ├── agent.yaml
    ├── templates/       # Documentation templates
    └── README.md
```

## Creating an Agent

1. **Create directory**:
   ```bash
   mkdir -p agents/my-agent
   ```

2. **Create agent.yaml**:
   ```yaml
   name: my-agent
   description: Description of what this agent does
   model: claude-sonnet-4.5
   temperature: 0.7
   system_prompt: |
     You are a specialized agent for...
   tools:
     - read
     - write
     - bash
   ```

3. **Add documentation**:
   Create `README.md` explaining:
   - What the agent does
   - When to use it
   - Example usage
   - Limitations

4. **Test the agent**:
   - Mount namespace in test environment
   - Verify agent appears in OpenCode
   - Test with real scenarios

## Example Agents

### code-reviewer

An agent specialized in code review:
- Checks code quality
- Identifies bugs and security issues
- Suggests improvements
- Follows team coding standards

### test-writer

An agent that writes comprehensive tests:
- Generates unit tests
- Creates integration tests
- Ensures code coverage
- Follows testing best practices

### docs-generator

An agent for technical documentation:
- Generates API documentation
- Creates user guides
- Updates README files
- Maintains changelog

## Best Practices

1. **Single Responsibility**: Each agent should have one clear purpose
2. **Documentation**: Include README.md with usage examples
3. **Versioning**: Use Git to track changes to agent configurations
4. **Testing**: Always test agents in dev environment before deploying to global namespace
5. **Naming**: Use descriptive names with hyphens (e.g., `api-designer`, not `designer`)

## Contributing

When adding new agents to the global namespace:

1. Create agent in your local environment first
2. Test thoroughly
3. Document usage and limitations
4. Submit for review (if using Git workflow)
5. Add to global namespace once approved

## Usage in OpenCode

Once mounted, agents are available in OpenCode conversations:

```bash
# List available agents
opencode agents list

# Use an agent
opencode chat --agent code-reviewer

# Or in conversation
"Use the code-reviewer agent to review this file"
```

## Troubleshooting

### Agent not appearing

1. Verify namespace is mounted: `ls /home/dev/.opencode/namespaces/global/agents`
2. Check agent.yaml syntax
3. Restart OpenCode or container

### Agent not working correctly

1. Check system_prompt is clear and specific
2. Verify required tools are listed
3. Test with simple examples first
4. Review OpenCode logs for errors
