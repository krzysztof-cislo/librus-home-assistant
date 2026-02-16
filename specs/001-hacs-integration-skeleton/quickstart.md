# Quick Start Guide: HACS Integration Skeleton

**Date**: 2026-02-16  
**Feature**: HACS Integration Skeleton

## Overview

This guide provides step-by-step instructions for setting up and testing the HACS integration skeleton.

## Prerequisites

- Home Assistant instance running (version 2024.1.0 or later)
- HACS installed and configured
- Python 3.11+ (for development)
- Git (for repository management)

## Development Setup

### 1. Create Repository Structure

```bash
# Create repository root
mkdir hacs-integration-skeleton
cd hacs-integration-skeleton

# Create integration directory (replace [domain] with your domain)
mkdir -p custom_components/[domain]
mkdir -p tests
```

### 2. Create Integration Files

#### `custom_components/[domain]/__init__.py`

```python
"""The [domain] integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up [domain] from a config entry."""
    # Skeleton: no setup needed
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Skeleton: no cleanup needed
    return True
```

#### `custom_components/[domain]/manifest.json`

```json
{
  "domain": "[domain]",
  "name": "[Display Name]",
  "integration_type": "hub",
  "version": "1.0.0",
  "config_flow": true,
  "single_config_entry": true,
  "documentation": "https://github.com/user/repo",
  "issue_tracker": "https://github.com/user/repo/issues",
  "codeowners": ["@github_username"],
  "requirements": [],
  "dependencies": []
}
```

#### `custom_components/[domain]/const.py`

```python
"""Constants for the [domain] integration."""
DOMAIN = "[domain]"
```

#### `custom_components/[domain]/config_flow.py`

```python
"""Config flow for [domain]."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for [domain]."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="[Display Name]",
                data={}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})
        )
```

### 3. Create HACS Manifest

#### `hacs.json` (repository root)

```json
{
  "name": "[Display Name]",
  "hacs": "1.6.0",
  "domains": ["[domain]"],
  "iot_class": "Local Polling",
  "homeassistant": "2024.1.0"
}
```

### 4. Create README

#### `README.md` (repository root)

```markdown
# [Display Name]

Home Assistant integration for [description].

## Installation

Install via HACS:
1. Open HACS
2. Go to Integrations
3. Click "Explore & Download Repositories"
4. Search for "[Display Name]"
5. Click "Download"

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "[Display Name]"
4. Click "Submit" to complete setup

## Support

[Support information]
```

## Testing

### Manual Testing

1. **Install Integration**:
   - Copy `custom_components/[domain]/` to your Home Assistant `custom_components/` directory
   - Restart Home Assistant
   - Verify integration appears in Settings → Devices & Services → Add Integration

2. **Configure Integration**:
   - Click "Add Integration"
   - Select your integration
   - Click "Submit"
   - Verify integration appears in configured integrations list

3. **Verify Single Instance**:
   - Try to add integration again
   - Verify it's prevented (should not show in list or show error)

### Automated Testing

Create `tests/test_config_flow.py`:

```python
"""Test config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.[domain].config_flow import ExampleConfigFlow


async def test_user_step(hass: HomeAssistant):
    """Test user step."""
    flow = ExampleConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user()
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await flow.async_step_user({})
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "[Display Name]"
```

## HACS Installation Testing

1. **Create GitHub Repository**:
   - Push code to GitHub
   - Create a release tag (e.g., `v1.0.0`)

2. **Add to HACS**:
   - In HACS, add custom repository
   - Enter repository URL
   - Select "Integration" category
   - Install

3. **Verify Installation**:
   - Check that files are in `custom_components/[domain]/`
   - Verify integration appears in Home Assistant

## Next Steps

Once skeleton is working:
1. Add functionality to `__init__.py`
2. Add entities/services as needed
3. Update config flow to collect required data
4. Add tests for new functionality

## Troubleshooting

- **Integration not appearing**: Check `manifest.json` syntax and restart Home Assistant
- **Config flow not working**: Verify `config_flow: true` in manifest.json
- **Duplicate configuration allowed**: Verify `single_config_entry: true` in manifest.json
- **HACS not finding integration**: Check repository structure and `hacs.json` format
