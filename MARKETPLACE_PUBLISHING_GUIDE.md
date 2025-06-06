# 🚀 Publishing Dev Environment Copilot to VS Code Marketplace

## Prerequisites

1. **Create Azure DevOps Account**
   - Go to https://dev.azure.com
   - Sign in with Microsoft account
   - Create organization if needed

2. **Generate Personal Access Token (PAT)**
   ```
   1. Go to Azure DevOps > User Settings > Personal Access Tokens
   2. Click "New Token"
   3. Name: "VS Code Publishing"
   4. Organization: Select your organization
   5. Scopes: Select "Marketplace" > "Manage"
   6. Click "Create"
   7. SAVE THE TOKEN - you can't see it again!
   ```

3. **Install VSCE (VS Code Extension Manager)**
   ```bash
   npm install -g @vscode/vsce
   ```

## Step-by-Step Publishing Process

### 1. Setup Extension
```bash
cd vscode-extension
npm install
```

### 2. Create Publisher Profile
```bash
# Login with your PAT
vsce login <your-publisher-name>
# Enter your PAT when prompted
```

### 3. Create Publisher (First Time Only)
```bash
# If you don't have a publisher yet
vsce create-publisher <your-publisher-name>
```

### 4. Update package.json
Edit `vscode-extension/package.json`:
```json
{
  "publisher": "your-actual-publisher-name"
}
```

### 5. Add Extension Icon
Create a 128x128 PNG icon named `icon.png` in the `vscode-extension` folder.

### 6. Build and Test
```bash
# Compile TypeScript
npm run compile

# Package extension (creates .vsix file)
npm run package

# Test locally (optional)
code --install-extension dev-env-copilot-extension-1.0.0.vsix
```

### 7. Publish to Marketplace
```bash
# Publish extension
npm run publish

# Or manually with vsce
vsce publish
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish-extension.yml`:

```yaml
name: Publish VS Code Extension

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: |
        cd vscode-extension
        npm install
        
    - name: Compile
      run: |
        cd vscode-extension
        npm run compile
        
    - name: Publish Extension
      run: |
        cd vscode-extension
        npx vsce publish -p ${{ secrets.VSCE_PAT }}
      env:
        VSCE_PAT: ${{ secrets.VSCE_PAT }}
```

## Required Repository Secrets

Add to GitHub Repository Settings > Secrets:
- `VSCE_PAT`: Your Personal Access Token from Azure DevOps

## Pre-Publishing Checklist

- [ ] Extension icon created (128x128 PNG)
- [ ] Publisher name set in package.json
- [ ] README.md is complete and helpful
- [ ] CHANGELOG.md documents all features
- [ ] Extension compiles without errors
- [ ] All features tested manually
- [ ] Screenshots/GIFs for marketplace (optional but recommended)

## Post-Publishing

1. **Verify on Marketplace**: Check https://marketplace.visualstudio.com/publishers/your-publisher-name
2. **Test Installation**: `code --install-extension your-publisher.dev-env-copilot-extension`
3. **Update Documentation**: Add marketplace badge to main README
4. **Monitor**: Watch for user feedback and issues

## Version Updates

For future updates:
```bash
# Update version in package.json
npm version patch  # or minor/major

# Publish new version
vsce publish
```

## Marketplace Categories

Your extension will appear in:
- Extensions > Other
- Extensions > Machine Learning  
- Extensions > Chat

## Tips for Success

1. **Good Description**: Clear, concise explanation of what it does
2. **Keywords**: Use relevant search terms
3. **Screenshots**: Show the extension in action
4. **Documentation**: Comprehensive README and examples
5. **Responsiveness**: Respond to user issues quickly
