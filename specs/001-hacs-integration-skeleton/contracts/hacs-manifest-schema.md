# HACS Manifest Schema Contract

**Date**: 2026-02-16  
**Feature**: HACS Integration Skeleton

## Overview

The `hacs.json` file in the repository root provides metadata for HACS discovery and installation. This file is optional but recommended for custom integrations.

## Schema

```json
{
  "name": "Example Integration",
  "hacs": "1.6.0",
  "domains": ["example"],
  "iot_class": "Local Polling",
  "homeassistant": "2024.1.0"
}
```

## Field Descriptions

- **name**: Display name for the integration in HACS
- **hacs**: Minimum HACS version required (optional)
- **domains**: Array of integration domains (usually single domain)
- **iot_class**: IoT classification (Local Polling, Cloud Polling, Cloud Push, etc.)
- **homeassistant**: Minimum Home Assistant version required

## IoT Class Options

- **Local Polling**: Integration polls local device/API
- **Cloud Polling**: Integration polls cloud service
- **Cloud Push**: Integration receives push updates from cloud
- **Assumed State**: Integration doesn't know actual device state
- **Calculated**: Integration calculates values from other entities

For skeleton: Use **Local Polling** as default (can be updated when functionality is added).

## Complete Example

```json
{
  "name": "Example Integration",
  "hacs": "1.6.0",
  "domains": ["example"],
  "iot_class": "Local Polling",
  "homeassistant": "2024.1.0"
}
```

## Repository Structure Requirement

Files must be located at:
```
ROOT_OF_REPO/custom_components/[domain]/
```

HACS automatically discovers integrations in this location.

## Validation

- HACS validates manifest format during installation
- Domain must match the integration's actual domain
- Home Assistant version must be compatible with user's installation
