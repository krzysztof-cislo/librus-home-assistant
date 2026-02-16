# Config Flow Schema Contract

**Date**: 2026-02-16  
**Feature**: HACS Integration Skeleton

## Overview

The configuration flow for this skeleton integration uses a minimal single-step confirmation flow. No user input fields are required - only a confirmation step.

## Config Flow Steps

### Step: `user`

**Purpose**: Single confirmation step to complete integration setup

**Schema**: No input fields required

**Flow**:
1. User initiates config flow from Home Assistant integrations UI
2. Config flow displays confirmation screen
3. User clicks "Submit" or "Finish" button
4. Configuration entry is created
5. Integration setup completes

## Implementation Contract

### Python Code Structure

```python
from homeassistant import config_entries
from .const import DOMAIN

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Create entry
            return self.async_create_entry(
                title="Integration Name",
                data={}
            )
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})  # Empty schema for confirmation only
        )
```

### Error Handling

- **Duplicate configuration**: Prevented automatically by `single_config_entry: true` in manifest.json
- **User cancellation**: Handled by Home Assistant UI (user can cancel at any time)

## Validation

- No user input to validate (skeleton only)
- Single instance enforcement handled by manifest option

## Future Extensibility

When functionality is added:
- Add input fields to `data_schema` as needed
- Add validation logic in `async_step_user`
- Add additional steps using `async_step_<step_name>` pattern
- Store user input in `data` or `options` dictionary
