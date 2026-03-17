# Context

This directory contains shared knowledge bases, documentation, and reference materials that provide context for OpenCode conversations.

## What is Context?

Context files are reference materials that help OpenCode understand:
- System architecture and design decisions
- Team coding standards and conventions
- Domain-specific knowledge
- Project history and rationale
- Technical specifications

## Contents

Common context types:

```
context/
├── architecture.md         # System architecture overview
├── coding-standards.md     # Team coding conventions
├── onboarding.md          # New team member guide
├── glossary.md            # Domain terminology
├── tech-stack.md          # Technologies used
├── design-decisions.md    # ADRs (Architecture Decision Records)
└── api-conventions.md     # API design standards
```

## Creating Context Documents

1. **Create markdown file**:
   ```bash
   touch context/my-context.md
   ```

2. **Structure the document**:
   ```markdown
   # [Topic Name]
   
   ## Overview
   High-level summary of the topic.
   
   ## Details
   Comprehensive information organized by subtopics.
   
   ## Examples
   Concrete examples demonstrating concepts.
   
   ## References
   Links to related documentation or resources.
   ```

## Example Context Documents

### architecture.md

```markdown
# System Architecture

## Overview

Our system uses a microservices architecture with:
- Backend: Node.js + Express
- Frontend: React + TypeScript
- Database: PostgreSQL
- Cache: Redis
- Message Queue: RabbitMQ

## Service Diagram

```
┌─────────┐     ┌─────────┐     ┌──────────┐
│ Frontend│────▶│   API   │────▶│ Database │
└─────────┘     └─────────┘     └──────────┘
                     │
                     ▼
                ┌─────────┐
                │  Cache  │
                └─────────┘
```

## Services

### API Service
- RESTful API
- Authentication via JWT
- Rate limiting enabled
- Hosted on: api.example.com

### Frontend
- Single Page Application (SPA)
- Server-side rendering for SEO
- Hosted on: www.example.com

## Data Flow

1. User request → Frontend
2. Frontend → API (with JWT)
3. API → Database/Cache
4. Response flows back

## Infrastructure

- Cloud provider: AWS
- Container orchestration: Kubernetes
- CI/CD: GitHub Actions
- Monitoring: Datadog
```

### coding-standards.md

```markdown
# Coding Standards

## General Principles

1. Write code for humans, not machines
2. Clarity over cleverness
3. Consistent style across codebase
4. Test-driven development (TDD)

## Naming Conventions

### Variables
- camelCase for variables and functions
- PascalCase for classes and components
- UPPER_SNAKE_CASE for constants

```typescript
const userName = "John";           // Good
const user_name = "John";          // Bad

class UserProfile { }              // Good
class userProfile { }              // Bad

const MAX_RETRY_COUNT = 3;         // Good
const maxRetryCount = 3;           // Bad (should be const)
```

### Files
- kebab-case for file names
- Component files: PascalCase.tsx
- Utility files: kebab-case.ts

```
user-profile.component.tsx    // Good
UserProfile.tsx               // Good for components
user_profile.component.tsx    // Bad
```

## Code Structure

### Functions
- Single responsibility
- Max 50 lines
- Max 4 parameters (use options object if more)

```typescript
// Good: Single responsibility, clear purpose
function calculateTotalPrice(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Bad: Too many responsibilities
function processOrder(order, validate, save, notify, log) {
  // Too many things happening
}
```

### Comments
- Write WHY, not WHAT
- Use JSDoc for public APIs
- Avoid obvious comments

```typescript
// Good: Explains WHY
// Using exponential backoff to handle rate limiting
await retryWithBackoff(apiCall);

// Bad: Explains WHAT (obvious)
// Increment counter by 1
counter++;
```

## Testing

- Write tests first (TDD)
- One assertion per test
- Clear test names describing behavior

```typescript
// Good: Clear, specific test name
test('should return 404 when user not found', async () => {
  const response = await request(app).get('/users/999');
  expect(response.status).toBe(404);
});

// Bad: Vague test name
test('user test', () => {
  // ...
});
```

## Git Conventions

### Commit Messages
Format: `type(scope): description`

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance

```bash
# Good commits
feat(auth): add JWT token refresh
fix(api): handle null response in getUserById
docs(readme): update installation instructions

# Bad commits
fixed stuff
wip
asdf
```

### Branch Names
Format: `type/description`

```bash
# Good branches
feat/user-authentication
fix/memory-leak-in-cache
refactor/simplify-payment-logic

# Bad branches
new-feature
johns-work
fix
```

## Code Review

Before submitting PR:
- [ ] All tests pass
- [ ] Code follows style guide
- [ ] No console.log or debugger statements
- [ ] Documentation updated
- [ ] Self-reviewed the diff

## References

- [TypeScript Style Guide](https://github.com/basarat/typescript-book/blob/master/docs/styleguide/styleguide.md)
- [Clean Code Principles](https://github.com/ryanmcdermott/clean-code-javascript)
```

## Usage in OpenCode

Context documents help OpenCode understand your project:

```
"Review this code following our coding standards"
"Design an API endpoint following our api-conventions"
"Explain our system architecture"
"Help onboard me to the project using the onboarding guide"
```

OpenCode can read these context files from the mounted namespace and apply the knowledge.

## Best Practices

1. **Keep Updated**: Review and update context regularly
2. **Be Comprehensive**: Include all important information
3. **Use Examples**: Show concrete examples, not just descriptions
4. **Link Resources**: Reference external documentation
5. **Version Control**: Use Git to track changes

## Document Types

### Architecture Decision Records (ADRs)

Document important decisions:

```markdown
# ADR-001: Use PostgreSQL for Database

## Status
Accepted

## Context
We need a reliable database for our application with ACID guarantees.

## Decision
We will use PostgreSQL as our primary database.

## Consequences
- Pros: ACID compliance, mature, great JSON support
- Cons: Harder to scale horizontally than NoSQL
```

### Glossary

Define domain-specific terms:

```markdown
# Glossary

## Business Terms

**SKU** (Stock Keeping Unit): Unique identifier for each product variant

**Fulfillment**: Process of receiving, packaging, and shipping orders

**Churn Rate**: Percentage of customers who cancel subscriptions

## Technical Terms

**Circuit Breaker**: Design pattern that prevents cascading failures

**Event Sourcing**: Storing state changes as sequence of events
```

## Contributing

When adding context documents:

1. Ensure information is accurate and current
2. Use clear, concise language
3. Include examples where possible
4. Link to related documents
5. Get review from team members familiar with the topic

## Tips

- **Diagrams**: Include architecture diagrams (Mermaid, ASCII art)
- **Examples**: Show good and bad examples
- **Updates**: Date stamp major updates
- **Index**: Maintain a table of contents for large documents
- **Search**: Use descriptive headings for easy searching
