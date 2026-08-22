# 101 AI Plugin

Public marketplace package for the 101 Codex plugin. It bundles workflow skills for company analytics, finance, CRM, estimates, events, reports, Wiki, and files, backed by the registered 101 MCP app.

## Install in Codex

1. Open **Settings → Plugins → Add → Add plugin marketplace**.
2. Set **Source** to `https://github.com/101-group/101-ai-plugin.git`.
3. Set **Git ref** to `main`.
4. Leave **Sparse paths** empty and add the marketplace.
5. Enable the **101** plugin and complete the 101 OAuth connection.

## Claude compatibility

The current package uses the Codex marketplace and `.codex-plugin` manifest format. The Git repository can be shared with other agent clients, but Claude requires its own supported plugin/skills manifest and installation flow. Do not treat this Codex package as directly installable in Claude until that compatibility layer is added and tested.

## Security

The repository contains no credentials. Authentication and data permissions are enforced by the remote 101 MCP server through OAuth. Never commit access tokens, passwords, private keys, or local session data.

## Version

Current Codex plugin: `1.0.0+codex.20260822085356`.
