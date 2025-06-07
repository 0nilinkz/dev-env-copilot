# Docker Registry Deployment Setup

## 🐳 Automated Docker Deployment

This project includes automated Docker image building and deployment to multiple registries:

- **Docker Hub**: `devenvcopilot/dev-env-copilot`
- **GitHub Container Registry**: `ghcr.io/yourusername/dev-env-copilot`

## 🔐 Required Secrets

To enable automated deployment, set up these secrets in your GitHub repository:

### 1. Docker Hub Deployment

1. **Create Docker Hub Account** (if you don't have one):
   - Go to [Docker Hub](https://hub.docker.com/)
   - Create account and verify email

2. **Create Docker Hub Repository**:
   - Go to "Create Repository"
   - Name: `dev-env-copilot`
   - Description: "MCP server for development environment detection"
   - Visibility: Public

3. **Generate Access Token**:
   - Go to Account Settings > Security > New Access Token
   - Name: "GitHub Actions"
   - Permissions: Read, Write, Delete

4. **Add GitHub Secrets**:
   ```
   Repository Settings > Secrets and variables > Actions > New repository secret:
   
   Name: DOCKERHUB_USERNAME
   Value: your-dockerhub-username
   
   Name: DOCKERHUB_TOKEN  
   Value: your-dockerhub-access-token
   ```

### 2. GitHub Container Registry (Automatic)

GitHub Container Registry is automatically configured using `GITHUB_TOKEN` (no additional setup needed).

## 🚀 Deployment Triggers

The workflow automatically triggers on:

- **Push to `main`**: Builds and pushes `latest` tag
- **Pull Requests**: Builds only (no push) 
- **Git Tags** (`v*`): Builds and pushes versioned tags
- **Releases**: Builds and pushes release versions

## 📋 Multi-Architecture Support

The deployment builds for multiple architectures:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM 64-bit, Apple Silicon, AWS Graviton)
- `linux/arm/v7` (ARM 32-bit, Raspberry Pi)

## 🔒 Security Features

- **Vulnerability Scanning**: Trivy security scanner
- **Multi-stage Builds**: Minimal final image size
- **Non-root User**: Runs as dedicated `mcp-user`
- **Read-only Filesystem**: Enhanced security

## 📖 Usage After Deployment

Once deployed, users can easily install and run:

### Docker Hub
```bash
# Pull and run latest
docker run -i devenvcopilot/dev-env-copilot

# Specific version
docker run -i devenvcopilot/dev-env-copilot:v1.0.0

# With MCP client configuration
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | docker run -i devenvcopilot/dev-env-copilot
```

### GitHub Container Registry
```bash
# Pull and run latest
docker run -i ghcr.io/yourusername/dev-env-copilot

# Specific version  
docker run -i ghcr.io/yourusername/dev-env-copilot:v1.0.0
```

### VS Code MCP Configuration
```json
{
  "mcp.servers": {
    "dev-env-copilot": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "devenvcopilot/dev-env-copilot"],
      "transport": "stdio"
    }
  }
}
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "dev-env-copilot": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "devenvcopilot/dev-env-copilot"]
    }
  }
}
```

## 🎯 Benefits of Docker Registry Deployment

1. **Easy Installation**: No Python/Node.js setup required
2. **Consistent Environment**: Same container everywhere
3. **Cross-Platform**: Works on any system with Docker
4. **Version Control**: Tagged releases for stability
5. **Security**: Isolated container environment
6. **Zero Dependencies**: Everything bundled in the image

## 🔄 Manual Deployment

If you need to manually build and push:

```bash
# Build multi-architecture image
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t devenvcopilot/dev-env-copilot:latest \
  -t devenvcopilot/dev-env-copilot:v1.0.0 \
  --push .

# Build for GitHub Container Registry
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t ghcr.io/yourusername/dev-env-copilot:latest \
  -t ghcr.io/yourusername/dev-env-copilot:v1.0.0 \
  --push .
```

## 📈 Monitoring Deployment

- **GitHub Actions**: Monitor builds in Actions tab
- **Docker Hub**: View pulls and tags at hub.docker.com
- **Security**: Review scan results in Security tab
- **Registry**: Monitor GHCR usage in Packages tab

---

This setup provides **professional-grade Docker deployment** with automated builds, security scanning, and multi-registry publishing! 🚀
