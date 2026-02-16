# Librus

[![hacs][hacs-badge]][hacs-url]

Home Assistant integration for Librus.

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to **Integrations**
3. Click **Explore & Download Repositories**
4. Search for **Librus**
5. Click **Download**
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/librus` directory to your Home Assistant `custom_components/` directory
2. Restart Home Assistant

## Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Librus**
4. Enter your Librus **login** and **password**
5. Click **Submit** — credentials will be validated against Librus
6. On success, the integration is configured and ready

### Updating Credentials

1. Go to **Settings** → **Devices & Services**
2. Find the **Librus** integration card
3. Click the **Configure** button
4. Enter your updated **login** and **password**
5. Click **Submit** — new credentials will be validated before saving

### Troubleshooting

- **Invalid login or password**: Double-check your Librus credentials and try again
- **Could not connect to Librus**: Check your network connection and verify that Librus is accessible

## Support

If you encounter any issues, please [open an issue](https://github.com/krzysztof-cislo/librus-home-assistant/issues).

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://hacs.xyz
