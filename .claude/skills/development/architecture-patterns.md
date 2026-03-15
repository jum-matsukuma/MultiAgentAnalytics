# Architecture Patterns

Software architecture patterns and design principles available for implementation.

## Application Architecture

### Layered Architecture
- Presentation layer (UI components, controllers)
- Business logic layer (services, domain models)
- Data access layer (repositories, DAOs)
- Clean separation of concerns

### Component-Based Architecture
- Modular, reusable components
- Props and data flow patterns
- Composition over inheritance
- Single responsibility principle

### Microservices Patterns
- Service decomposition strategies
- API gateway patterns
- Service discovery and communication
- Data consistency across services

## Design Patterns

### Creational Patterns
- **Factory Pattern**: Object creation abstraction
- **Builder Pattern**: Complex object construction
- **Singleton Pattern**: Single instance management
- **Dependency Injection**: Loose coupling and testability

### Behavioral Patterns
- **Observer Pattern**: Event-driven architectures
- **Strategy Pattern**: Algorithm encapsulation
- **Command Pattern**: Action encapsulation
- **State Pattern**: State-dependent behavior

### Structural Patterns
- **Adapter Pattern**: Interface compatibility
- **Decorator Pattern**: Behavior extension
- **Facade Pattern**: Simplified interfaces
- **Repository Pattern**: Data access abstraction

## API Design Patterns

### RESTful APIs
- Resource-oriented design
- HTTP method semantics
- Status code conventions
- Pagination and filtering
- HATEOAS principles

### GraphQL
- Schema-first design
- Query optimization
- Subscription patterns
- Federation and stitching

### Event-Driven Architecture
- Event sourcing patterns
- CQRS (Command Query Responsibility Segregation)
- Message queues and pub/sub
- Saga patterns for distributed transactions

## Frontend Architecture

### State Management
- **Flux/Redux**: Unidirectional data flow
- **Context + Reducer**: React state patterns
- **Reactive State**: Observable-based state management
- **Atomic State**: Granular state management (Recoil, Jotai)

### Component Architecture
- Container vs Presentational components
- Higher-Order Components (HOCs)
- Render Props pattern
- Custom Hook patterns

## Backend Architecture

### Domain-Driven Design
- Bounded contexts and aggregates
- Domain models and value objects
- Application services and repositories
- Event-driven domain models

### Clean Architecture
- Dependency inversion principle
- Use case driven design
- Infrastructure independence
- Testable business logic

### Data Patterns
- **Active Record**: Object-relational mapping
- **Data Mapper**: Separation of domain and persistence
- **Unit of Work**: Transaction management
- **Specification Pattern**: Query encapsulation

## Security Patterns

### Authentication Patterns
- JWT (JSON Web Tokens)
- OAuth 2.0 and OpenID Connect
- Session-based authentication
- Multi-factor authentication

### Authorization Patterns
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Policy-based authorization
- Resource-level permissions

## Performance Patterns

### Caching Strategies
- Application-level caching
- Database query caching
- CDN and edge caching
- Cache invalidation patterns

### Optimization Patterns
- Lazy loading and code splitting
- Database connection pooling
- Asynchronous processing
- Load balancing strategies

## Testing Architecture

### Test Patterns
- Test doubles (mocks, stubs, fakes)
- Test data builders
- Page Object Model (for E2E tests)
- Contract testing patterns

### Testing Strategies
- Test pyramid (unit, integration, E2E)
- Test-driven development (TDD)
- Behavior-driven development (BDD)
- Property-based testing