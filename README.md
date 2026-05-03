# 📺 Bravia REST API

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg?style=for-the-badge)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/cmos486/Bravia-REST-API?style=for-the-badge)](https://github.com/cmos486/Bravia-REST-API/releases)

> A full-featured Home Assistant custom integration for **Sony Bravia** displays, built on top of the [Sony Bravia Pro REST API](https://pro-bravia.sony.net/remote-display-control/rest-api/reference/).
>
> Significantly more capable than the built-in `braviatv` integration — exposes **all** available API functionality as native Home Assistant entities.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 **Media Player** | Power, volume (absolute slider + step), mute, input source selection, app launching, media browser |
| 🎮 **Remote Control** | Send any IRCC command by name or raw base64 code |
| 🔘 **19 Buttons** | System (reboot, blank screen) + 15 IRCC remote buttons (Home, Back, D-pad, OK, Volume, Channels, Netflix, Play/Pause/Stop) |
| 🎚️ **Selects** | Sound output, screen rotation, picture mode, sleep timer |
| 📊 **Sensors** | Model, firmware, serial number, MAC address |
| 🔀 **Switches** | LED indicator, Wake-on-LAN toggle |
| 📡 **SSDP Discovery** | TV auto-detected on your network — no manual IP needed |
| 🌐 **Wake-on-LAN** | Power on from standby via magic packet |
| 🔍 **Runtime Discovery** | Detects available features and IRCC codes per TV model |
| 📱 **Media Browser** | Browse and launch installed Android apps visually |

---

## 📋 Prerequisites

Before installing, make sure your TV is configured:

| Step | Setting |
|------|---------|
| 1️⃣ | TV on the **same local network** as Home Assistant |
| 2️⃣ | **PSK enabled**: Settings > Network & Internet > Local network setup > IP control > Authentication |
| 3️⃣ | **Remote control enabled**: Settings > Network & Internet > Remote device settings > Control remotely |
| 4️⃣ | **Home Assistant 2024.1** or newer |

---

## 🚀 Installation

### HACS (Recommended)

1. Open **HACS** in your Home Assistant
2. Click **⋮** (top right) → **Custom repositories**
3. Add: `https://github.com/cmos486/Bravia-REST-API`
4. Category: **Integration**
5. Click **Add** → Search for **Bravia REST API** → **Install**
6. **Restart** Home Assistant

### Manual Installation

1. Download the [latest release](https://github.com/cmos486/Bravia-REST-API/releases)
2. Copy `custom_components/bravia_rest_api/` to your HA `config/custom_components/`
3. Restart Home Assistant

---

## ⚙️ Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **Bravia REST API** (or it may appear automatically via SSDP discovery!)
3. Enter the TV's **IP address** and **Pre-Shared Key**
4. The integration auto-discovers the TV model and creates all entities
5. Click **Submit**

<p align="center">
  <img src="https://raw.githubusercontent.com/cmos486/Bravia-REST-API/main/images/integration_installed.jpg" alt="Integration installed in Home Assistant" width="600"/>
</p>

### Excluded Sources

Optionally hide specific apps or inputs from the source list dropdown. Excluded sources
are still launchable via the `bravia_rest_api.open_app` service and remain visible in the
`installed_apps` attribute.

**Option A: UI (Options Flow)**

1. Go to **Settings > Devices & Services > Bravia REST API**
2. Click **Configure**
3. Select the sources you want to exclude from the dropdown
4. Click **Submit**

> If the TV is off when you open the options, a text field is shown instead — enter one source name per line.

**Option B: YAML**

```yaml
bravia_rest_api:
  excluded_sources:
    - "Timers & Clock"
    - "Eco Dashboard"
```

> If both UI and YAML are configured, the UI selection takes priority.

---

## 🎮 Entities Created

The integration creates **30+ entities** for full TV control:

### 🎬 Media Player

| Entity | Description |
|--------|-------------|
| `media_player.<tv_model>` | Main TV entity — power, volume slider, source selection, app launching |

> **Source list** combines HDMI inputs + installed Android apps in one unified dropdown.

### 📡 Remote

| Entity | Description |
|--------|-------------|
| `remote.<tv_name>_remote` | Send IRCC remote commands (always-on, doesn't control power) |

### 🔘 Buttons — System

| Entity | Icon | Description |
|--------|------|-------------|
| `button._reboot` | 🔄 | Reboot the TV |
| `button._terminate_apps` | ❌ | Close all foreground apps |
| `button._picture_off` | 🖥️ | Blank the screen (audio continues) |
| `button._picture_on` | 💡 | Restore the screen |

### 🎮 Buttons — Remote IRCC

| Entity | Command | Icon |
|--------|---------|------|
| `button._ircc_home` | Home | 🏠 |
| `button._ircc_back` | Back / Return | ◀️ |
| `button._ircc_up` | D-pad Up | ⬆️ |
| `button._ircc_down` | D-pad Down | ⬇️ |
| `button._ircc_left` | D-pad Left | ⬅️ |
| `button._ircc_right` | D-pad Right | ➡️ |
| `button._ircc_confirm` | OK / Enter | ✅ |
| `button._ircc_options` | Options / Menu | ⚙️ |
| `button._ircc_volume_up` | Volume Up | 🔊 |
| `button._ircc_volume_down` | Volume Down | 🔉 |
| `button._ircc_mute` | Mute | 🔇 |
| `button._ircc_channel_up` | Channel Up | 📺⬆️ |
| `button._ircc_channel_down` | Channel Down | 📺⬇️ |
| `button._ircc_netflix` | Netflix | 🎬 |
| `button._ircc_play` | Play | ▶️ |
| `button._ircc_pause` | Pause | ⏸️ |
| `button._ircc_stop` | Stop | ⏹️ |
| `button._ircc_input` | Input selector | 🔌 |

### 🔢 Numbers

| Entity | Description |
|--------|-------------|
| `number._brightness` | Picture brightness slider (range discovered per TV model) |

> Only created if the TV supports `getPictureQualitySettings` for the `brightness` target.

### 🎚️ Selects

| Entity | Options |
|--------|---------|
| `select._sound_output` | Speaker, HDMI, Speaker + HDMI, Audio System |
| `select._screen_rotation` | 0°, 90°, 180°, 270° |
| `select._picture_mode` | Standard, Vivid, Cinema, Custom, Game, Graphics, Photo, Sports |
| `select._sleep_timer` | Off, 15 min, 30 min, 45 min, 60 min, 90 min, 120 min |
| `select._brightness_preset` | Min, Low, Medium, High, Max (mapped to % of brightness range) |

### 📊 Sensors (Diagnostic)

| Entity | Value |
|--------|-------|
| `sensor._model` | e.g. KD-65XH9096 |
| `sensor._firmware` | Firmware version |
| `sensor._serial_number` | Serial number |
| `sensor._mac_address` | MAC address |

### 🔀 Switches

| Entity | Description |
|--------|-------------|
| `switch._led_indicator` | Toggle the front LED indicator |
| `switch._wake_on_lan` | Enable/disable Wake-on-LAN |

---

## 🔧 Services

### `bravia_rest_api.send_ircc`

Send an IRCC remote control command by name or raw base64 code.

```yaml
service: bravia_rest_api.send_ircc
target:
  entity_id: remote.kd_65xh9096_remote
data:
  command: VolumeUp
```

### `bravia_rest_api.open_app`

Open an app by name (case-insensitive) or URI.

```yaml
service: bravia_rest_api.open_app
target:
  entity_id: media_player.kd_65xh9096
data:
  app_name: Netflix
```

### `bravia_rest_api.set_audio_output`

Change audio output target.

```yaml
service: bravia_rest_api.set_audio_output
target:
  entity_id: media_player.kd_65xh9096
data:
  output: speaker  # speaker | hdmi | speaker_hdmi | audioSystem
```

### `bravia_rest_api.blank_screen`

Turn the screen off (picture off) or back on.

```yaml
service: bravia_rest_api.blank_screen
target:
  entity_id: media_player.kd_65xh9096
data:
  enable: true  # true = blank, false = restore
```

### `bravia_rest_api.get_installed_apps`

Force refresh the installed apps list.

```yaml
service: bravia_rest_api.get_installed_apps
target:
  entity_id: media_player.kd_65xh9096
```

### `remote.send_command` (HA built-in)

Send multiple IRCC commands in sequence:

```yaml
service: remote.send_command
target:
  entity_id: remote.kd_65xh9096_remote
data:
  command:
    - Home
    - Down
    - Down
    - Confirm
  num_repeats: 1
```

---

## 🎯 Known IRCC Codes

Common commands auto-discovered at setup. Check the `available_commands` attribute on the remote entity for your TV's full list. See [COMMANDS.md](COMMANDS.md) for the complete reference.

| Command | Description | Command | Description |
|---------|-------------|---------|-------------|
| `PowerOff` | Power off | `Home` | Home screen |
| `Input` | Input selector | `Return` | Back/return |
| `Num0`-`Num9` | Number keys | `Confirm` | Enter/OK |
| `VolumeUp` | Volume up | `Options` | Options menu |
| `VolumeDown` | Volume down | `Play` | Play |
| `Mute` | Toggle mute | `Pause` | Pause |
| `ChannelUp` | Channel up | `Stop` | Stop |
| `ChannelDown` | Channel down | `Netflix` | Launch Netflix |
| `Up`/`Down`/`Left`/`Right` | D-pad navigation | `Next`/`Prev` | Track skip |

---

## 🔍 Troubleshooting

<details>
<summary><b>TV not responding / cannot connect</b></summary>

- Verify the **IP address** is correct and TV is on the same network
- Check that **IP Control** and **Remote control** are enabled in TV settings
- Make sure the **PSK** matches what's configured on the TV
</details>

<details>
<summary><b>TV in standby — limited functionality</b></summary>

- In **standby**, most API calls fail (Sony limitation)
- The integration handles this gracefully — entities go to "off" / "unavailable"
- Enable **Wake-on-LAN** to power on from standby
</details>

<details>
<summary><b>TV in suspend — completely unreachable</b></summary>

- In **suspend mode**, the TV's HTTP server stops entirely
- Use Wake-on-LAN to wake the TV, then the API becomes available
</details>

<details>
<summary><b>Netflix / YouTube not showing as current source</b></summary>

- `getPlayingContentInfo` returns empty data for native Android apps — **known Sony API limitation**
- The integration shows the last known input or "Unknown" for streaming apps
</details>

<details>
<summary><b>IRCC commands not working</b></summary>

- Check the `available_commands` attribute on the remote entity
- Not all TVs support all IRCC codes — auto-discovered at setup
</details>

<details>
<summary><b>Some settings not applying</b></summary>

- Sound output, screen rotation, and picture mode are **model-specific**
- If a setting fails silently, it may not be supported on your TV
</details>

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push and open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 📚 References

- [Sony Bravia Pro REST API Reference](https://pro-bravia.sony.net/remote-display-control/rest-api/reference/)
- [Sony Bravia Pro REST API Guide](https://pro-bravia.sony.net/remote-display-control/rest-api/guide/)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [IRCC Commands Reference](COMMANDS.md)
