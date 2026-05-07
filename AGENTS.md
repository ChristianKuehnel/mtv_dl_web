# Development Process & Agent Configuration

## Overview
This document defines the development process and agent configurations for implementing the MTV Downloader Web Interface according to the established architecture and implementation plan.

## Development Approach

### Core Principles
1. **Modular Implementation**: Follow the phased approach outlined in the implementation plan
2. **Integration First**: Reuse existing mtv_dl functionality rather than reimplementing
3. **Container Native**: Design all components to work in containerized environments
4. **Quality Assurance**: Implement rigorous testing at each development stage
5. **Standards Compliance**: Maintain consistent code formatting and validation standards

### Development Workflow
1. **Phase-based Development**: Execute tasks in sequential phases as defined in implementation plan
2. **Definition of Done**: Each task must meet all specified quality criteria before completion
3. **Continuous Integration**: Automated testing and linting at each stage
4. **Container Testing**: Every phase must include container smoke tests

## Agent Configuration

### Project Structure
```
mtv_dl_web/
├── src/
│   ├── main.py              # Main FastAPI application
│   ├── frontend/            # Static frontend files
│   └── mtv_dl/             # Integrated mtv_dl modules
├── spec/
│   ├── sw_architecture.md   # Software architecture specification
│   ├── implementation_plan.md # Implementation plan
│   └── product_design.md    # Product requirements
├── tests/                   # Unit tests
├── docker/                  # Docker configuration
├── .dockerignore           # Docker ignore rules
└── Dockerfile              # Container build configuration
```

### Required Agents

#### 1. Development Assistant Agent
**Purpose**: Guided implementation assistant
**Capabilities**:
- Provides code examples based on architecture specifications
- Ensures compliance with Definition of Done criteria
- Verifies integration with existing mtv_dl modules
- Assists with container configuration and testing

**Usage**: 
```bash
# Run development assistant for specific task
opencode agent --name=dev-assistant --task="Implement search API endpoint"
```

#### 2. Code Quality Agent
**Purpose**: Enforces code quality standards
**Capabilities**:
- Runs black formatter on Python code
- Validates Python type annotations with mypy
- Lints Dockerfiles with hadolint
- Formats HTML and JavaScript code with Prettier
- Lints shell scripts with ShellCheck
- Ensures all tests pass

**Usage**:
```bash
# Run code quality checks
opencode agent --name=code-quality --check="all"
```

#### 3. Container Deployment Agent
**Purpose**: Manages container deployment and testing
**Capabilities**:
- Builds container images for Alpine Linux
- Runs smoke tests for backend health
- Deploys containers with Podman
- Tests volume mounting and persistence
- Verifies environment variable configuration

**Usage**:
```bash
# Deploy container and run smoke tests
opencode agent --name=container-deploy --action="deploy-and-test"
```

#### 4. Integration Verification Agent
**Purpose**: Validates mtv_dl integration
**Capabilities**:
- Ensures proper module imports from mtv_dl
- Verifies database connection patterns
- Confirms filter logic compatibility
- Tests download functionality with mtv_dl backend

**Usage**:
```bash
# Verify mtv_dl integration
opencode agent --name=integration-verifier --test="database-connection"
```

### Configuration Files

#### Dockerfile Configuration
- Base image: Alpine Linux 3.18+
- Python 3.10+ with uv for dependency management
- Production-ready optimizations
- Multi-stage build for minimal image size

#### Environment Configuration
```yaml
# /config/mtv_dl_web.yaml
port: 8000
database_path: /data/.mtv_dl_web
target_dir: /downloads
series_target_dir: /downloads/series
log_level: INFO
scheduler_cron: "0 2 * * *"
```

### Testing Requirements

#### Unit Test Suite
- All API endpoints must have unit tests
- Database operations must be tested
- Search functionality must cover all filter operators
- Queue management must be validated
- Scheduler functionality must be tested

#### Integration Test Suite
- Container deployment verification
- Health check endpoint testing
- Database persistence validation
- mtv_dl module integration testing

#### Smoke Test Suite
- Backend startup validation
- Port binding verification
- Configuration loading test
- Container deployment with Podman

## Development Process Flow

### Phase 1: Basic Implementation
1. Create basic FastAPI application
2. Implement health check endpoint
3. Setup frontend serving
4. Configure basic container image
5. Run smoke tests

### Phase 2: mtv_dl Integration
1. Import and integrate mtv_dl modules
2. Implement database operations
3. Create search API endpoint
4. Test integration with mtv_dl functionality

### Phase 3: Feature Implementation
1. Develop search UI
2. Implement download logic
3. Add queue management
4. Build scheduling features
5. Complete all tests and validations

### Phase 4: Container Deployment
1. Final container builds
2. Comprehensive smoke testing
3. Podman deployment verification
4. Production configuration validation

## Quality Gates
Each phase must pass the following quality gates:
1. ✅ All unit tests pass
2. ✅ Code formatting with black
3. ✅ Type validation with mypy
4. ✅ Dockerfile linting
5. ✅ Backend health check passes
6. ✅ Container deployment with Podman works
7. ✅ All Definition of Done criteria met