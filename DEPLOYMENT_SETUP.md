# Deployment Setup Guide

This guide explains how to set up automated publishing for the Dev Environment Copilot MCP server to npm, PyPI, and Docker registries.

## 🔄 Workflow Structure

The project uses four separate GitHub Actions workflows with proper dependency chains:

1. **`test-and-build.yml`** - Runs on every push/PR, tests across multiple platforms
2. **`deploy-pypi.yml`** - Runs only on releases, depends on test workflow, deploys to PyPI
3. **`deploy-npm.yml`** - Runs only on releases, depends on test workflow, deploys to npm  
4. **`docker-deploy.yml`** - Runs on releases and main branch pushes, depends on test workflow, builds and publishes Docker images

**Dependency Flow:**
```
Release Created → Test Workflow → PyPI Deployment
                              → npm Deployment  
                              → Docker Deployment
```

This ensures that deployments only happen after all tests pass successfully.

### Benefits of Separated Workflows

- **🔍 Fast Feedback**: Tests run on every push/PR without the overhead of deployment setup
- **🛡️ Security**: Deployment secrets are only used when actually deploying
- **⚡ Efficiency**: Parallel deployment to different registries after tests pass
- **🎯 Clarity**: Each workflow has a single, clear responsibility
- **🚀 Reliability**: Failed tests prevent all deployments; individual deployment failures don't affect others
- **🔗 Dependencies**: All deployments depend on the same test suite, ensuring consistency

## 🔐 Required Secrets

You need to configure the following secrets in your GitHub repository:

### 1. PyPI API Token (`PYPI_API_TOKEN`)

1. **Create a PyPI account** at [pypi.org](https://pypi.org/)
2. **Generate an API token**:
   - Go to Account Settings > API Tokens
   - Create a new token with scope "Entire account" or specific to your project
   - Copy the token (starts with `pypi-`)

3. **Add to GitHub Secrets**:
   - Go to your repository: Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-AgENdGVzdC5weXBpLm9yZw...` (your token)

### 2. npm Access Token (`NPM_TOKEN`)

1. **Create an npm account** at [npmjs.com](https://www.npmjs.com/)
2. **Generate an access token**:
   - Go to Account Settings > Access Tokens
   - Create a new "Automation" token
   - Copy the token

3. **Add to GitHub Secrets**:
   - Name: `NPM_TOKEN`
   - Value: `npm_1234567890abcdef...` (your token)

### 3. Docker Hub Credentials (Optional)

For Docker Hub publishing:

1. **Create Docker Hub account** at [hub.docker.com](https://hub.docker.com/)
2. **Generate access token**:
   - Go to Account Settings > Security > Access Tokens
   - Create new token with "Read, Write, Delete" permissions

3. **Add to GitHub Secrets**:
   - Name: `DOCKER_HUB_USERNAME` - Your Docker Hub username
   - Name: `DOCKER_HUB_TOKEN` - Your access token

## 🏗️ GitHub Actions "Stages" Implementation

### Understanding GitHub Actions Workflow Dependencies

GitHub Actions doesn't have a dedicated "stages" keyword like some CI/CD systems. Instead, it implements stages through **job dependencies** and **reusable workflows**:

#### Key Concepts:
- **Job Dependencies**: Use `needs` keyword to make jobs wait for other jobs
- **Reusable Workflows**: Use `workflow_call` to create shared workflows  
- **Sequential Execution**: Jobs run in dependency order, not parallel

#### Our Architecture:
```
Test Stage (test-and-build.yml)
├── Trigger: push, pull_request, workflow_call
├── Matrix: Multiple OS + Python versions
└── Tests: MCP server + Node.js wrapper

Deploy Stage (triggered on release)
├── deploy-pypi.yml (needs: test)
├── deploy-npm.yml (needs: test)  
└── docker-deploy.yml (needs: test)
```

#### How It Works:
1. **Test Workflow** (`test-and-build.yml`) is **reusable** via `workflow_call`
2. **Deploy Workflows** call the test workflow using `uses: ./.github/workflows/test-and-build.yml`
3. **Deploy Jobs** use `needs: test` to wait for tests to pass
4. **Only on Success**: Deployments only run if all tests pass

#### Benefits:
- ✅ **Reliable**: No deployment without passing tests
- 🔧 **Modular**: Each deployment type is independent
- ⚡ **Efficient**: Reuses test workflow, avoids duplication
- 🎯 **Flexible**: Can deploy to specific registries independently
- 📊 **Clear**: Easy to see which stage failed

## 📋 Workflow Details

The project uses a **modular workflow architecture** for better control and reliability:

### 1. **Test & Build** (`.github/workflows/test-and-build.yml`)
- ⚡ Runs on every push and pull request
- 🧪 Tests across multiple platforms (Ubuntu, Windows, macOS)
- 🐍 Tests across multiple Python versions (3.8-3.12)
- 🔍 Validates code quality and functionality
- 🔄 **Reusable** - Can be called by other workflows via `workflow_call`
- **No deployments** - keeps CI fast and focused

### 2. **PyPI Deployment** (`.github/workflows/deploy-pypi.yml`)
- 🚀 Runs only on GitHub releases
- ✅ Calls test workflow first (`uses: ./.github/workflows/test-and-build.yml`)
- 📦 Builds Python package after tests pass (`needs: test`)
- 🐍 Publishes to PyPI

### 3. **npm Deployment** (`.github/workflows/deploy-npm.yml`)
- 🚀 Runs only on GitHub releases  
- ✅ Calls test workflow first (`uses: ./.github/workflows/test-and-build.yml`)
- 📦 Updates package version from release tag after tests pass (`needs: test`)
- 📋 Publishes to npm registry

### 4. **Docker Deployment** (`.github/workflows/docker-deploy.yml`)
- 🚀 Runs only on GitHub releases
- ✅ Calls test workflow first (`uses: ./.github/workflows/test-and-build.yml`)
- 🏗️ Multi-architecture builds (amd64, arm64, arm/v7) after tests pass (`needs: test`)
- 🐳 Publishes to Docker Hub and GitHub Container Registry
- 🔒 Includes security scanning

**Key Architecture Benefits:**
- ⚡ **Faster CI**: Tests run independently from deployments
- 🎯 **Targeted failures**: Easy to identify if test vs deployment issues
- 🔄 **Independent releases**: Can release to specific registries if needed
- 🛡️ **Better security**: Each workflow has minimal required permissions
- 📊 **Clear dependencies**: Visual representation of test → deploy flow

## 📦 Publishing Process

### Automatic Publishing (Recommended)

Publishing happens automatically when you create a GitHub release:

1. **Create a release tag**:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

2. **Create GitHub release**:
   - Go to your repository > Releases > Create a new release
   - Choose the tag you just created
   - Add release notes
   - Click "Publish release"

3. **Automated publishing**:
   - ✅ **PyPI**: `deploy-pypi.yml` runs tests and publishes Python package
   - ✅ **npm**: `deploy-npm.yml` runs tests and publishes Node.js package  
   - ✅ **Docker**: `docker-deploy.yml` builds and publishes multi-arch images
   - 🎯 Each deployment is **independent** - if one fails, others continue

### Manual Publishing

If you need to publish manually:

#### PyPI (Python)
```bash
# Build and upload to PyPI
python -m build
twine upload dist/*
```

#### npm (Node.js)
```bash
# Update version and publish
npm version patch  # or minor/major
npm publish
```

#### Docker
```bash
# Build and push to Docker Hub
docker build -t 0nilinkz/dev-env-copilot:latest .
docker push 0nilinkz/dev-env-copilot:latest

# Tag and push specific version
docker tag 0nilinkz/dev-env-copilot:latest 0nilinkz/dev-env-copilot:v1.0.1
docker push 0nilinkz/dev-env-copilot:v1.0.1
```

## 🎯 Installation After Publishing

Once published, users can install via:

### PyPI
```bash
pip install dev-env-copilot
python -m dev_environment_mcp.server
```

### npm
```bash
npx dev-env-copilot
# or
npm install -g dev-env-copilot
dev-env-copilot
```

### Docker Hub
```bash
docker run -i 0nilinkz/dev-env-copilot:latest
```

### GitHub Container Registry
```bash
docker run -i ghcr.io/0nilinkz/dev-env-copilot:latest
```

## 🔍 Verification

Test that publishing worked:

1. **Check PyPI**: Visit `https://pypi.org/project/dev-env-copilot/`
2. **Check npm**: Visit `https://www.npmjs.com/package/dev-env-copilot`
3. **Check Docker Hub**: Visit `https://hub.docker.com/r/0nilinkz/dev-env-copilot`
4. **Test installation**: Try installing from each registry

## 🚨 Troubleshooting

### Common Issues

- **PyPI upload fails**: Check if package name is available and version number is new
- **npm publish fails**: Ensure you're logged in (`npm login`) and package name is available
- **Docker push fails**: Verify Docker Hub credentials and repository exists
- **GitHub Actions fails**: Check secrets are correctly set and have proper permissions

### Debug Commands

```bash
# Test PyPI credentials
twine check dist/*

# Test npm credentials  
npm whoami

# Test Docker credentials
docker login
```

## 📋 Checklist

Before first deployment:

- [ ] Set up PYPI_API_TOKEN secret
- [ ] Set up NPM_TOKEN secret
- [ ] Set up Docker Hub credentials (optional)
- [ ] Update repository URLs in package.json
- [ ] Update Docker image names in workflows
- [ ] Test workflow with a pre-release
- [ ] Create first release

Your MCP server is now ready for automated deployment! 🚀
