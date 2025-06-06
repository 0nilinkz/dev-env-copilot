# VS Code Extension Publishing Setup Guide

This guide explains how to set up automated publishing for the Dev Environment Copilot VS Code extension.

## 🔐 Required Secrets

You need to set up the following secrets in your GitHub repository:

### 1. VS Code Marketplace Token (`VSCE_PAT`)

1. **Get a Visual Studio Marketplace Personal Access Token:**
   - Go to [Azure DevOps](https://dev.azure.com)
   - Sign in with your Microsoft account
   - Go to User Settings > Personal Access Tokens
   - Create a new token with:
     - **Name:** VS Code Extension Publishing
     - **Organization:** All accessible organizations
     - **Scopes:** Custom defined
     - **Marketplace:** Manage

2. **Add to GitHub Secrets:**
   ```bash
   # Go to your repository: Settings > Secrets and variables > Actions
   # Add new repository secret:
   Name: VSCE_PAT
   Value: [your-marketplace-token]
   ```

### 2. Open VSX Registry Token (`OVSX_PAT`) - Optional

1. **Get an Open VSX Registry Access Token:**
   - Go to [Open VSX Registry](https://open-vsx.org)
   - Sign in with GitHub/GitLab
   - Go to User Settings > Access Tokens
   - Create a new token

2. **Add to GitHub Secrets:**
   ```bash
   Name: OVSX_PAT
   Value: [your-openvsx-token]
   ```

## 📦 Publisher Setup

Before publishing, update the `package.json`:

```json
{
  "publisher": "your-actual-publisher-name",
  "version": "1.0.0"
}
```

**To register as a publisher:**
1. Go to [Visual Studio Marketplace](https://marketplace.visualstudio.com/manage)
2. Sign in and create a publisher profile
3. Use that publisher name in `package.json`

## 🚀 Publishing Workflows

### Automatic Publishing (Recommended)

**On Release:**
1. Create a new release on GitHub
2. The workflow automatically publishes to:
   - VS Code Marketplace
   - Open VSX Registry (optional)
   - GitHub Release assets

**Manual Publishing:**
1. Go to Actions tab in GitHub
2. Select "Build and Publish VS Code Extension"
3. Click "Run workflow"
4. Check "Publish to marketplace"

### Manual Publishing (Local)

```bash
cd vscode-extension

# Install dependencies
npm install

# Build and test
npm run compile
npm test

# Package the extension
npm run package

# Publish to marketplace (requires VSCE_PAT)
npx vsce publish

# Or publish specific version
npx vsce publish 1.0.1
```

## 🧪 Testing the Workflow

### Test Build Only
```bash
# Push changes to a feature branch
git checkout -b feature/test-build
git push origin feature/test-build

# Create a pull request - this will:
# ✅ Run tests
# ✅ Build VSIX package
# ✅ Run security scans
# ❌ NOT publish to marketplace
```

### Test Full Publishing
```bash
# Method 1: Create a pre-release
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
# Create a pre-release on GitHub

# Method 2: Manual workflow dispatch
# Go to Actions > Build and Publish VS Code Extension
# Run workflow with "Publish to marketplace" checked
```

## 📋 Pre-Publishing Checklist

- [ ] Update `package.json` with correct publisher name
- [ ] Set appropriate version number
- [ ] Add/update extension icon (`icon.png`)
- [ ] Update `README.md` with installation instructions
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Test extension locally in VS Code
- [ ] Run tests: `npm test`
- [ ] Verify VSIX package: `npm run package`
- [ ] Set up GitHub secrets (`VSCE_PAT`, `OVSX_PAT`)

## 🔄 Workflow Features

### ✅ What the CI/CD Pipeline Does

1. **Testing:**
   - Runs on multiple VS Code versions (stable, insiders)
   - Executes all unit and integration tests
   - Validates TypeScript compilation
   - Runs ESLint checks

2. **Building:**
   - Compiles TypeScript to JavaScript
   - Packages extension into `.vsix` file
   - Uploads build artifacts

3. **Security:**
   - Scans for sensitive data in package
   - Runs `npm audit` for vulnerabilities
   - Validates package contents

4. **Publishing:**
   - Publishes to VS Code Marketplace
   - Publishes to Open VSX Registry
   - Attaches VSIX to GitHub releases

### 🎯 Trigger Conditions

- **Tests:** Every push and PR to `main`
- **Build:** Every push and PR affecting extension files
- **Publish:** Only on releases or manual trigger
- **Security:** All PRs and pushes

## 📝 Version Management

### Semantic Versioning
- **Major:** `1.0.0` → `2.0.0` (breaking changes)
- **Minor:** `1.0.0` → `1.1.0` (new features)
- **Patch:** `1.0.0` → `1.0.1` (bug fixes)

### Release Process
1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Commit changes
4. Create and push tag: `git tag v1.0.1 && git push origin v1.0.1`
5. Create GitHub release
6. Workflow automatically publishes

## 🛠️ Troubleshooting

### Common Issues

**1. "Publisher not found" error:**
- Verify publisher name in `package.json` matches your marketplace publisher
- Ensure you're signed in to the correct marketplace account

**2. "Authentication failed" error:**
- Check that `VSCE_PAT` secret is set correctly
- Verify token has "Marketplace > Manage" permissions
- Token might be expired - generate a new one

**3. Tests failing in CI:**
- Tests run in headless environment
- Check Xvfb display configuration
- Verify VS Code version compatibility

**4. Package too large:**
- Check `.vsixignore` file to exclude unnecessary files
- Verify `node_modules` are not included
- Use `npm run package` locally to inspect contents

### Getting Help

1. Check [VS Code Extension API docs](https://code.visualstudio.com/api)
2. Review [VSCE publishing guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
3. Check GitHub Actions logs for detailed error messages
4. Open an issue in the repository for support

## 🎉 Success!

Once set up, your extension will be automatically:
- ✅ Tested on every change
- ✅ Built and packaged
- ✅ Published to marketplace on releases
- ✅ Available for installation via VS Code

Users can install with:
```bash
# Via VS Code UI
Ctrl+Shift+X → Search "Dev Environment Copilot"

# Via command line
code --install-extension your-publisher.dev-env-copilot-extension
```
