# Manifest Schema Contract

**Date**: 2026-02-16  
**Feature**: HACS Integration Skeleton

## Overview

The `manifest.json` file defines integration metadata and capabilities. This contract specifies the required and optional fields for both Home Assistant core and HACS compatibility.

## Required Fields

### Home Assistant Core Requirements

```json
{
  "domain": "example",
  "name": "Example Integration",
  "integration_type": "hub|service|device",
  "documentation": "https://example.com/docs",
  "codeowners": ["@github_username"],
  "requirements": [],
  "dependencies": []
}
```

### HACS Additional Requirements

```json
{
  "version": "1.0.0",
  "issue_tracker": "https://github.com/user/repo/issues"
}
```

## Single Instance Configuration

For single instance enforcement:

```json
{
  "single_config_entry": true
}
```

## Config Flow Enablement

To enable configuration flow UI:

```json
{
  "config_flow": true
}
```

## Complete Example Manifest

```json
{
  "domain": "example",
  "name": "Example Integration",
  "integration_type": "hub",
  "version": "1.0.0",
  "config_flow": true,
  "single_config_entry": true,
  "documentation": "https://example.com/docs",
  "issue_tracker": "https://github.com/user/repo/issues",
  "codeowners": ["@github_username"],
  "requirements": [],
  "dependencies": []
}
```

## Field Descriptions

- **domain**: Unique short identifier (lowercase, alphanumeric + underscores)
- **name**: Human-readable display name
- **integration_type**: Type of integration (hub, service, device, etc.)
- **version**: Semantic version (SemVer) or Calendar version (CalVer)
- **config_flow**: Boolean to enable configuration flow UI
- **single_config_entry**: Boolean to enforce single instance (Home Assistant 2024.3+)
- **documentation**: URL to integration documentation
- **issue_tracker**: URL to issue tracker (required for HACS)
- **codeowners**: List of GitHub usernames for code ownership
- **requirements**: List of Python package dependencies
- **dependencies**: List of other Home Assistant integrations required

## Validation Rules

- Domain must be unique across all integrations
- Version must follow SemVer or CalVer format
- All URLs must be valid and accessible
- Codeowners must be valid GitHub usernames
