# Platform Config Flow Skill

This skill covers implementing and reviewing `config_flow.py` for Home Assistant integrations.

## What is a Config Flow?

A config flow provides a UI-driven setup experience for integrations. It handles:
- User authentication and credential validation
- Device/service discovery
- Re-authentication when credentials expire
- Options flow for post-setup configuration

## Required Components

### ConfigFlow Class

```python
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

class MyIntegrationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
```

## Quality Scale Requirements

### Bronze
- Config flow must exist (`config_flow: true` in `manifest.json`)
- Must handle `cannot_connect` and `invalid_auth` errors
- Must use `async_create_entry` with meaningful title

### Silver
- Implement `async_step_reauth` for re-authentication support
- Use `unique_id` to prevent duplicate entries (`await self.async_set_unique_id(...)`)
- Abort if already configured: `self._abort_if_unique_id_configured()`

### Gold
- Implement `OptionsFlow` for runtime configuration changes
- Support discovery steps (`async_step_zeroconf`, `async_step_dhcp`, etc.)
- Validate all user inputs before entry creation

## Re-authentication Flow

```python
async def async_step_reauth(
    self, entry_data: Mapping[str, Any]
) -> ConfigFlowResult:
    """Handle re-authentication."""
    return await self.async_step_reauth_confirm()

async def async_step_reauth_confirm(
    self, user_input: dict[str, Any] | None = None
) -> ConfigFlowResult:
    """Handle re-authentication confirmation."""
    errors: dict[str, str] = {}
    reauth_entry = self._get_reauth_entry()

    if user_input is not None:
        try:
            await validate_input(self.hass, {**reauth_entry.data, **user_input})
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        else:
            return self.async_update_reload_and_abort(
                reauth_entry,
                data_updates=user_input,
            )

    return self.async_show_form(
        step_id="reauth_confirm",
        data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
        errors=errors,
    )
```

## Common Mistakes

- Forgetting to call `async_set_unique_id` before `_abort_if_unique_id_configured`
- Not translating error keys in `strings.json`
- Storing sensitive data (passwords) without using `data` vs `options` correctly
- Missing `config_entries_options_update_listener` when implementing options flow
