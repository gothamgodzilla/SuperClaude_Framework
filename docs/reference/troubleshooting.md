# SuperClaude Troubleshooting Guide 🔧

Quick fixes to advanced diagnostics for SuperClaude Framework issues.

## Quick Fixes (90% of problems)

**Installation Verification:**
```bash
superclaude --version                # Should show 4.3.1
superclaude doctor                   # Health check: pytest plugin, skills, config
superclaude install --list           # Lists /sc: commands and whether each is installed
```

**Command Issues:**
```bash
# Test in Claude Code:
/sc:brainstorm "test project"        # Should ask discovery questions

# If no response: Restart Claude Code session
```

**Resolution Checklist:**
- [ ] `superclaude --version` shows 4.3.1
- [ ] `superclaude doctor` reports no failures
- [ ] `/sc:` commands respond in Claude Code
- [ ] MCP servers listed: `claude mcp list`

## Common Issues

### Installation Problems

**Package Installation Fails:**
```bash
# For pipx users
pipx uninstall superclaude
pipx install superclaude

# For pip users
pip uninstall superclaude
pip install --upgrade pip
pip install superclaude
```

**Permission Denied / PEP 668 Error:**
```bash
# Option 1: Use pipx (recommended)
pipx install superclaude

# Option 2: Use pip with --user flag
pip install --user superclaude

# Option 3: Fix permissions
sudo chown -R $USER ~/.claude

# Option 4: Force installation (use with caution)
pip install --break-system-packages superclaude
```

**Commands Missing or Outdated:**
```bash
superclaude install --force          # Reinstall all /sc: commands
superclaude update                   # Same as install --force
superclaude install-skill confidence-check --force  # Reinstall a skill
```

### Command Issues

**Commands Not Recognized:**
1. Verify the files exist: `ls ~/.claude/commands/sc/`
2. If empty or missing: `superclaude install --force`
3. Restart Claude Code completely
4. Test: `/sc:brainstorm "test"`

**Agents Not Activating:**
- Use specific keywords: `/sc:implement "secure JWT authentication"`
- Manual activation: `@agent-security-engineer "review auth code"`
- Verify agent files exist: `ls ~/.claude/agents/`

**Slow Performance:**
```bash
/sc:analyze . --no-mcp               # Test without MCP servers
/sc:analyze src/ --scope file        # Limit scope
```

### MCP Server Issues

**Server Connection Fails:**
```bash
claude mcp list                      # Check what Claude Code has registered
node --version                       # Most servers run via npx and need Node.js
superclaude mcp --list               # Show servers SuperClaude can install
superclaude mcp --servers context7   # Reinstall a specific server
superclaude mcp --dry-run            # Preview without installing
```

**API Key Required (Magic/Morphllm):**
```bash
export TWENTYFIRST_API_KEY="your_key"
export MORPH_API_KEY="your_key"
# Or use: /sc:command --no-mcp
```

## Advanced Diagnostics

**System Analysis:**
```bash
superclaude doctor --verbose         # Detailed diagnostics
python3 -c "import superclaude; print(superclaude.__file__)"  # Which install is active
```

**Component Analysis:**
```bash
ls -la ~/.claude/commands/sc/        # Installed slash commands
ls -la ~/.claude/agents/             # Installed agents
ls -la ~/.claude/skills/             # Installed skills
```

**Reset Installation:**
```bash
cp -r ~/.claude ~/.claude.backup     # Backup first
rm -rf ~/.claude/commands/sc         # Remove installed commands
pipx uninstall superclaude
pipx install superclaude
superclaude install
```

## Get Help

**Documentation:**
- [Installation Guide](../getting-started/installation.md) - Setup issues
- [Commands Guide](../user-guide/commands.md) - Usage issues

**Community:**
- [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)
- Include: OS, Python version, `superclaude doctor --verbose` output, error message, steps to reproduce
