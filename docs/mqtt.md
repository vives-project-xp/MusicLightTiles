# MQTT Communications

This document describes the way MQTT is used in this project.

> [!NOTE]  
> This document is still in development and is not finished yet.
> This file should be removed and the information should be moved to the wiki when the project is finished.

## MQTT Topics

This project uses the following base topic:

```text
music-light-tiles/
```

Each device has a unique name/id. This name is used as a subtopic.  
For example, the device with the name `tile-1` will use the following topic:

```text
music-light-tiles/tile-1/
```

Each device has 2 main subtopics, `state` and `command`. 

### State

The `state` subtopic is used to publish the current state of the device.
Each device has 4 subtopics under `state`, `system`, `audio`, `light` and `detect`.

#### System

The `system` subtopic is used to publish the system state of the device.
The payload is a JSON object with the following properties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `firmware` | String | The firmware version of the device. |
| `hardware` | String | The hardware version of the device. |
| `mode` | String | The current mode of the device. |
| `uptime` | Number | The number of seconds the device has been running. |
| `sounds` | Array | The list od possible sounds the device can play. |

Here is an example payload from the `system` subtopic:

```json
{
  "firmware": "1.0.0",
  "hardware": "1.0.0",
  "mode": "demo",
  "uptime": 1234,
  "sounds": ["sound-1", "sound-2", "sound-3"]
}
```

#### Audio

The `audio` subtopic is used to publish the audio state of the device.
The payload is a JSON object with the following properties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `playing` | Boolean | Whether the device is playing audio or not. |
| `sound` | String | The sound the device is playing. |
| `volume` | Number | The volume of the device. |

Here is an example payload from the `audio` subtopic:

```json
{
  "playing": true,
  "sound": "sound-1",
  "volume": 50
}
```

#### Light

The `light` subtopic is used to publish the light state of the device.
The payload is a JSON object with the following properties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness of the device. |
| `sections` | Array | The list of colors of each section, should have a format of {r: 0, g: 0, b: 0, w:0} for each section. |

Here is an example payload from the `light` subtopic:

```json
{
  "brightness": 50,
  "sections": [
    {"r": 255, "g": 0, "b": 0, "w": 0},
    {"r": 0, "g": 255, "b": 0, "w": 0},
    {"r": 0, "g": 0, "b": 255, "w": 0},
    {"r": 0, "g": 0, "b": 0, "w": 255}
  ]
}
```

#### Detect

The `detect` subtopic is used to publish the detection state of the device.
The payload is a JSON object with the following properties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `detected` | Boolean | Whether the device has detected presence or not. |

Here is an example payload from the `detect` subtopic:

```json
{
  "detected": true
}
```

### Command

The `command` subtopic is used to send commands to the device.
Each device has 3 subtopics under `command`, `system`, `audio` and `light`.
The detection of the device can not be controlled.

#### System

The `system` subtopic is used to send system commands to the device.
The payload is a JSON object with the following properties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `mode` | String | The mode to set the device to. |
| `reboot` | Boolean | Whether the device should reboot or not. |

Here is an example payload for the `system` subtopic:

```json
{
  "mode": "demo",
  "reboot": false
}
```

#### Audio

The `audio` subtopic is used to send audio commands to the device.
The payload is a JSON object with the following properties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `play` | Boolean | Whether the device should play audio or not. |
| `sound` | String | The sound the device should play. |
| `volume` | Number | The volume the device should set. |

Here is an example payload for the `audio` subtopic:

```json
{
  "play": true,
  "sound": "sound-1",
  "volume": 50
}
```

#### Light

The `light` subtopic is used to send light commands to the device.
The payload is a JSON object with the following properties:

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness the device should set. |
| `sections` | Array | The list of colors of each section, should have a format of {r: 0, g: 0, b: 0, w:0} for each section. |

Here is an example payload for the `light` subtopic:

```json
{
  "brightness": 50,
  "sections": [
    {"r": 255, "g": 0, "b": 0, "w": 0},
    {"r": 0, "g": 255, "b": 0, "w": 0},
    {"r": 0, "g": 0, "b": 255, "w": 0},
    {"r": 0, "g": 0, "b": 0, "w": 255}
  ]
}
```
