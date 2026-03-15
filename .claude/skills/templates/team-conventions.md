# Team Conventions Template

Copy this template to `.claude/skills/your-project/` and customize for your team's coding standards and conventions.

## Code Style and Standards

### General Principles
- **[Principle 1]**: [Description and rationale]
- **[Principle 2]**: [Description and rationale]
- **[Principle 3]**: [Description and rationale]

### Naming Conventions

#### Variables and Functions
```[language]
// Preferred patterns
const [namingPattern] = [example];
function [namingPattern]([parameters]) {
  // [convention description]
}
```

#### Files and Directories
- **Files**: [naming convention, e.g., kebab-case, camelCase]
- **Directories**: [naming convention]
- **Components**: [component naming pattern]

#### Database
- **Tables**: [naming convention]
- **Columns**: [naming convention]
- **Indexes**: [naming pattern]

### Code Organization

#### File Structure
```
src/
├── [directory]/          # [purpose]
├── [directory]/          # [purpose]
└── [directory]/          # [purpose]
```

#### Import/Export Patterns
```[language]
// Preferred import style
import { [pattern] } from '[location]';

// Export conventions
export const [pattern] = [example];
```

## Git Workflow

### Branch Naming
- **Feature branches**: `[prefix]/[description]`
- **Bug fixes**: `[prefix]/[description]`
- **Releases**: `[prefix]/[version]`

### Commit Messages
```
[type]([scope]): [description]

[optional body]

[optional footer]
```

**Types**: [feat, fix, docs, style, refactor, test, chore]
**Scopes**: [component, module, or area of change]

### Pull Request Process
1. **[Step 1]**: [Description]
2. **[Step 2]**: [Description]
3. **[Step 3]**: [Description]

## Code Review Standards

### What to Review
- **Functionality**: [Specific aspects to check]
- **Performance**: [Performance considerations]
- **Security**: [Security checklist items]
- **Tests**: [Testing requirements]

### Review Checklist
- [ ] [Checklist item]
- [ ] [Checklist item]
- [ ] [Checklist item]

### Feedback Guidelines
- **Constructive**: [How to give helpful feedback]
- **Specific**: [Provide concrete suggestions]
- **Respectful**: [Maintain professional tone]

## Testing Standards

### Test Structure
```[language]
// Test naming convention
describe('[component/function] [scenario]', () => {
  it('should [expected behavior]', () => {
    // Arrange
    [setup]
    
    // Act
    [action]
    
    // Assert
    [verification]
  });
});
```

### Coverage Requirements
- **Minimum Coverage**: [percentage]%
- **Critical Paths**: [coverage requirement]
- **New Code**: [coverage requirement]

### Test Categories
- **Unit Tests**: [What to test at unit level]
- **Integration Tests**: [What to test at integration level]
- **E2E Tests**: [What to test end-to-end]

## Documentation Standards

### Code Documentation
```[language]
/**
 * [Function description]
 * @param {[type]} [paramName] [description]
 * @returns {[type]} [description]
 * @example
 * [usage example]
 */
```

### API Documentation
- **Endpoints**: [Documentation format]
- **Parameters**: [How to document parameters]
- **Examples**: [Include request/response examples]

### README Structure
```markdown
# [Project Name]

## [Section]
[Content requirements]

## [Section]
[Content requirements]
```

## Error Handling

### Error Patterns
```[language]
// Preferred error handling
try {
  [operation]
} catch ([errorType]) {
  [error handling pattern]
}
```

### Logging Standards
- **Log Levels**: [when to use each level]
- **Format**: [log message structure]
- **Sensitive Data**: [what not to log]

## Performance Guidelines

### Optimization Principles
- **[Principle]**: [Description and examples]
- **[Principle]**: [Description and examples]

### Code Patterns to Avoid
- **[Anti-pattern]**: [Why to avoid and alternative]
- **[Anti-pattern]**: [Why to avoid and alternative]

## Security Guidelines

### Security Practices
- **[Practice]**: [How to implement]
- **[Practice]**: [How to implement]

### Common Vulnerabilities
- **[Vulnerability]**: [How to prevent]
- **[Vulnerability]**: [How to prevent]

## Deployment Standards

### Environment Management
- **Development**: [Environment standards]
- **Staging**: [Environment standards]
- **Production**: [Environment standards]

### Release Process
1. **[Step]**: [Description and requirements]
2. **[Step]**: [Description and requirements]
3. **[Step]**: [Description and requirements]

## Monitoring and Maintenance

### Monitoring Requirements
- **[Metric]**: [How to monitor and thresholds]
- **[Metric]**: [How to monitor and thresholds]

### Maintenance Tasks
- **Daily**: [Regular tasks]
- **Weekly**: [Regular tasks]
- **Monthly**: [Regular tasks]

## Onboarding Checklist

### New Team Member Setup
- [ ] [Setup task]
- [ ] [Setup task]
- [ ] [Setup task]

### Knowledge Areas
- [ ] [Area to learn]
- [ ] [Area to learn]
- [ ] [Area to learn]

## Tools and IDE Configuration

### Required Extensions
- **[Tool/Extension]**: [Purpose and configuration]
- **[Tool/Extension]**: [Purpose and configuration]

### Workspace Settings
```json
{
  "[setting]": "[value]",
  "[setting]": "[value]"
}
```