# Workflows

This directory contains shared workflow templates, guides, and checklists for common development tasks.

## What are Workflows?

Workflows are documented procedures and checklists for:
- Development processes (PR reviews, deployments)
- Team conventions (commit messages, branch naming)
- Quality assurance (testing, security checks)
- Project management (sprint planning, retrospectives)

## Contents

Common workflow types stored here:

```
workflows/
├── pr-checklist.md       # Pull request review checklist
├── deployment.md         # Deployment procedures
├── code-review.md        # Code review guidelines
├── testing.md            # Testing workflows
├── security-check.md     # Security review checklist
├── git-workflow.md       # Git branching and commit conventions
└── onboarding.md         # Team onboarding process
```

## Creating a Workflow

1. **Create markdown file**:
   ```bash
   touch workflows/my-workflow.md
   ```

2. **Document the workflow**:
   ```markdown
   # [Workflow Name]
   
   ## Purpose
   What this workflow accomplishes.
   
   ## When to Use
   Specific situations for this workflow.
   
   ## Steps
   1. Detailed step-by-step instructions
   2. Include commands, tools, or checkpoints
   3. Link to relevant documentation
   
   ## Checklist
   - [ ] Item 1
   - [ ] Item 2
   - [ ] Item 3
   
   ## Examples
   Concrete examples of the workflow in action.
   ```

## Example Workflows

### pr-checklist.md

```markdown
# Pull Request Checklist

## Before Creating PR

- [ ] Code follows team coding standards
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] No debugging code or console.logs
- [ ] Branch is up to date with main

## PR Description

- [ ] Clear title summarizing changes
- [ ] Description explains WHY (not just what)
- [ ] Links to relevant issues
- [ ] Screenshots/videos for UI changes

## Review Process

1. Self-review the diff
2. Request review from team members
3. Address feedback promptly
4. Resolve all conversations
5. Squash commits if needed
6. Merge when approved
```

### deployment.md

```markdown
# Deployment Workflow

## Pre-Deployment

1. Verify all tests pass on CI
2. Review staging environment
3. Create deployment checklist
4. Notify team of deployment window

## Deployment Steps

1. Tag release: `git tag v1.0.0`
2. Push to production branch
3. Monitor deployment logs
4. Run smoke tests
5. Verify critical paths

## Post-Deployment

1. Monitor error rates
2. Check performance metrics
3. Update changelog
4. Communicate deployment success

## Rollback Procedure

If issues occur:
1. Revert to previous version
2. Document what went wrong
3. Fix issue
4. Re-deploy when ready
```

## Usage

Reference workflows in:

1. **Pull Request Templates**:
   ```markdown
   Please review the [PR Checklist](pr-checklist.md)
   ```

2. **Documentation**:
   Link to workflows in project README or wiki

3. **OpenCode Conversations**:
   ```
   "Review this PR following our team's pr-checklist workflow"
   ```

4. **CI/CD Pipelines**:
   Automate checks based on workflow requirements

## Best Practices

1. **Keep Updated**: Review and update workflows regularly
2. **Be Specific**: Include exact commands and tools to use
3. **Add Examples**: Show concrete examples of good/bad practices
4. **Make Discoverable**: Link workflows from main project documentation
5. **Version Control**: Use Git to track changes to workflows

## Contributing

When updating workflows:

1. Propose changes in team meeting or via PR
2. Get consensus from team
3. Update relevant documentation
4. Communicate changes to all team members
5. Archive old versions if significantly changed

## Tips

- **Checklists**: Use GitHub-style checkboxes `- [ ]` for actionable items
- **Visual Aids**: Include diagrams or flowcharts for complex workflows
- **Links**: Reference external docs, tools, or related workflows
- **Examples**: Provide both good and bad examples
- **Automations**: Note which steps can be automated

## Common Workflows to Include

Consider creating these workflows:

- **Development**:
  - Feature development workflow
  - Bug fix workflow
  - Hotfix procedure

- **Quality Assurance**:
  - Testing strategy
  - Code review guidelines
  - Security review checklist

- **Operations**:
  - Deployment procedure
  - Rollback procedure
  - Incident response

- **Process**:
  - Sprint planning
  - Retrospectives
  - Onboarding new team members

## Integration with OpenCode

Workflows can be referenced in OpenCode conversations:

```
"Help me create a pull request following our team's pr-checklist workflow"
"Guide me through the deployment procedure"
"Review my code following the code-review workflow"
```

OpenCode can read these workflows and help enforce team standards.
