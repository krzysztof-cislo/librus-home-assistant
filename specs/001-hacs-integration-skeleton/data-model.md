# Data Model: HACS Integration Skeleton

**Date**: 2026-02-16  
**Feature**: HACS Integration Skeleton

## Overview

This integration is a skeleton with minimal data requirements. The only persistent data is the configuration entry managed by Home Assistant's `config_entries` system. No custom entities, services, or data storage are required.

## Entities

### Configuration Entry

**Purpose**: Represents the single configured instance of the integration in Home Assistant.

**Attributes**:
- `entry_id` (string): Unique identifier assigned by Home Assistant
- `domain` (string): Integration domain name
- `title` (string): Display name shown in Home Assistant UI
- `data` (dict): Configuration data (empty for skeleton)
- `options` (dict): Configuration options (empty for skeleton)
- `version` (int): Config entry version (starts at 1)
- `source` (string): Configuration source (always "user" for manual setup)

**Constraints**:
- Only one configuration entry allowed per Home Assistant instance (enforced via `single_config_entry: true` in manifest.json)
- No custom data fields required (skeleton has no functionality)

**Lifecycle**:
1. **Created**: When user completes configuration flow
2. **Loaded**: When Home Assistant starts and integration is configured
3. **Updated**: Not applicable for skeleton (no reconfiguration needed)
4. **Removed**: When user uninstalls integration

**State Transitions**:
```
Not Installed → Installed (via HACS)
Installed → Configured (via config flow)
Configured → Removed (via Home Assistant UI)
```

## Data Flow

### Configuration Flow

```
User initiates config flow
  ↓
ConfigFlow.async_step_user() called
  ↓
User clicks confirmation/submit
  ↓
ConfigFlow.async_create_entry() creates entry
  ↓
Entry stored in Home Assistant config_entries
  ↓
Integration __init__.py async_setup_entry() called
  ↓
Integration ready (no entities/services for skeleton)
```

### No Runtime Data

Since this is a skeleton integration:
- No entities are created
- No services are exposed
- No sensors, switches, or other Home Assistant entities
- No external API calls
- No data collection or processing

## Validation Rules

### Configuration Entry Validation

- **Domain uniqueness**: Enforced by Home Assistant (domain must be unique)
- **Single instance**: Enforced by `single_config_entry: true` manifest option
- **No data validation**: Skeleton has no user input fields to validate

### Error Cases

- **Duplicate configuration attempt**: Prevented automatically by `single_config_entry` manifest option
- **Invalid manifest.json**: Home Assistant will reject integration during startup
- **Missing required files**: Home Assistant will fail to load integration

## Integration with Home Assistant

### Config Entries API

The integration uses Home Assistant's built-in `config_entries` system:
- No custom storage needed
- Home Assistant manages entry lifecycle
- Entries persist across Home Assistant restarts
- Entries can be removed via Home Assistant UI

### Manifest Metadata

The `manifest.json` file contains:
- `domain`: Unique integration identifier
- `name`: Display name
- `version`: Integration version (SemVer or CalVer)
- `config_flow`: `true` (enables config flow UI)
- `single_config_entry`: `true` (enforces single instance)
- `documentation`: URL to documentation
- `codeowners`: List of maintainers
- `issue_tracker`: URL to issue tracker (for HACS)

## Future Extensibility

When functionality is added later:
- Additional data fields can be added to `config_entry.data` or `config_entry.options`
- Entities can be created in `async_setup_entry()`
- Services can be registered
- Coordinators can be added for data fetching

For now, the skeleton maintains minimal state to establish the integration structure.
