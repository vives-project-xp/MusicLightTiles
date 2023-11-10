# Api communication

This document describes this project's api implementation.
This project uses a websocket api to create a connection between the control server and the client(s).
The websocket api is used to send messages between the control server and the client(s).
There are 2 types of messages:
  - server actions (messages from the server to the client)
  - client actions (messages from the client to the server).

The content of the messages is different for each action. But all messages follow the same base format.

__The base format of a message is a JSON object with the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `action` | String | The action to perform. |
| `type` | String | The type of message. |
| `tile(s)` | String | The name of the tile or a list of names of tiles. |
| `args` | Object | (optional) The arguments for the action. |

The tile(s) property can be `tile` or `tiles`, depending on the action.
The args property is optional, not all actions have arguments.

> [!NOTE]
> This document is still in development and is not finished yet.
> This file should be removed and the information should be moved to the wiki when the project is finished.

## Client Actions (client -> server)

The client actions are sent by the client to the control server.
There are 3 actions the client can perform:

### Subscribe

This action is used to subscribe to different things, like the list of tiles or the state of tiles.
The control server will respond with the current state of the tiles or the current list of tiles.

__The `subscribe` action has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `action` | String | The action to perform. In this case, `subscribe`. |
| `type` | String | The type of subscription. Can be `tiles` or `state`. |
| `tiles` | Array | (optional) A list with the names of the tiles to subscribe to, can be one or more. (only used for `state` subscriptions) |

__Example of a `subscribe` action for the list of tiles:__

```json
{
  "action": "subscribe",
  "type": "tiles"
}
```

Responds for this action can be found [here](#send-list-of-tiles).

__Example of a `subscribe` action for the state of tiles:__

```json
{
  "action": "subscribe",
  "type": "state",
  "tiles": ["tile-1", "tile-2"]
}
```

Responds for this action can be found [here](#send-state-updates-to-client).

### Unsubscribe

This action is used to unsubscribe from different things, like the list of tiles or the state of tiles.
The control server will stop sending updates for the specified subscription.

__The `unsubscribe` action has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `action` | String | The action to perform. In this case, `unsubscribe`. |
| `type` | String | The type of subscription. Can be `tiles` or `state`. |
| `tiles` | Array | (optional) A list with the names of the tiles to unsubscribe from, can be one or more. (only used for `state` subscriptions) |

__Example of a `unsubscribe` action for the list of tiles:__

```json
{
  "action": "unsubscribe",
  "type": "tiles"
}
```

__Example of a `unsubscribe` action for the state of tiles:__

```json
{
  "action": "unsubscribe",
  "type": "state",
  "tiles": ["tile-1", "tile-2"]
}
```

The control server will not respond to these actions, but will stop sending updates for the specified subscription.

### Command

This action is used to send commands to tiles.
The control server will send these commands to the tiles.
There are multiple types of commands, but they all have the same base.

__The base command has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `action` | String | The action to perform. In this case, `command`. |
| `type` | String | The type of command to send. Can be `system`, `audio` or `light`. |
| `tiles` | Array | A list with the names of the tiles to send the command to (can be one or more). |
| `args` | Object | The arguments for the command. Each command type has its own arguments. |

__Example of a base command:__

```json
{
  "action": "command",
  "type": "command_type",
  "tiles": ["tile-1", "tile-2"],
  "args": {}
}
```

#### System

The `system` command type is used to send system commands to the tiles.

__The `args` object for the `system` command type has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `reboot` | Boolean | Whether the device should reboot or not. |
| `ping` | Boolean | Whether the device should send its uptime every change or not. |

These properties are optional. If a property is not specified, the server will not change the value of that property.

__Example of a `system` command:__

```json
{
  "action": "command",
  "type": "system",
  "tiles": ["tile-1", "tile-2"],
  "args": {
    "reboot": false,
    "ping": false
  }
}
```

#### Audio

The `audio` command type is used to send audio commands to the tiles.

__The `args` object for the `audio` command type has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `mode` | Number | The mode the device should set. 1 = play, 2 = pause, 3 = resume, 4 = stop. |
| `loop` | Boolean | Whether the device should loop the audio or not. |
| `sound` | String | The sound the device should play. |
| `volume` | Number | The volume the device should set. (0 - 100%) |

These properties are optional. If a property is not specified, the server will not change the value of that property.

__Example of an `audio` command:__

```json
{
  "action": "command",
  "type": "audio",
  "tiles": ["tile-1", "tile-2"],
  "args": {
    "mode": 1,
    "loop": false,
    "sound": "sound-1",
    "volume": 50
  }
}
```

#### Light

The `light` command type is used to send light commands to the tiles.

__The `args` object for the `light` command type has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness the device should set. (0 - 255) |
| `pixels` | Array | The list of colors of each pixel, should have a format of {r: 0, g: 0, b: 0, w:0} for each pixel. |

These properties are optional. If a property is not specified, the server will not change the value of that property.

__Example of a `light` command:__

```json
{
  "action": "command",
  "type": "light",
  "tiles": ["tile-1", "tile-2"],
  "args": {
    "brightness": 50,
    "pixels": [
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
    ]
  }
}
```

## Server Actions (server -> client)

The server actions are sent by the control server to the client.
There are 2 actions the server can perform:

### Tiles

This action is used to send a list of all tiles connected to the control server.
When the client connects to the control server, the control server will send a list of all available tiles. (This also includes tiles that are offline)
After the client has received this list, the control server will only send updates when a tile is added or removed.

__The `tiles` action has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `action` | String | The action to perform. In this case, `tiles`. |
| `type` | String | The type of update. Can be `list`, `add` or `remove`. |
| `tiles` | Array | A list with the names of the tile(s). |

__Example of the initial `tiles` action:__

```json
{
  "action": "tiles",
  "type": "list",
  "tiles": ["tile-1", "tile-2"]
}
```

__Example of a `tiles` action when a tile is added:__

```json
{
  "action": "tiles",
  "type": "add",
  "tiles": ["tile-1", "tile-2", "tile-3"]
}
```

__Example of a `tiles` action when a tile is removed:__

```json
{
  "action": "tiles",
  "type": "remove",
  "tiles": ["tile-1"]
}
```

This action is sent as a response to a [subscribe](#subscribe) action with the `type` set to `tiles`.

### Tile

This action is used to send updates about the state of the tiles.
The control server will send these updates when a tile changes its state.
There are multiple types of updates, but they all have the same base.

__The tile state is sent as a JSON object with the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `action` | String | The action to perform. In this case, `tile`. |
| `type` | String | The type of update. Can be `system`, `audio`, `light`, `presence` or `full` |
| `tile` | String | The name of the tile. |
| `args` | Object | The arguments for the update. Each update type has its own arguments. |

__Example of a base state update:__

```json
{
  "action": "tile",
  "type": "full",
  "tile": "tile-1",
  "args": {}
}
```

#### System

The `system` update type is used to send system updates to the client.
This update type is sent when the system state of the tile changes.

__The `state` object for the `system` update type has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `firmware` | String | The firmware version of the device. |
| `hardware` | String | The hardware version of the device. |
| `ping` | Boolean | Whether the device is pinging or not. |
| `uptime` | Number | The number of seconds the device has been running. |
| `sounds` | Array | The list of possible sounds the device can play. |

__Example of a `system` state update:__

```json
{
  "action": "tile",
  "type": "system",
  "tile": "tile-1",
  "args": {
    "firmware": "1.0.0",
    "hardware": "1.0.0",
    "ping": false,
    "uptime": 0,
    "sounds": ["sound-1", "sound-2"]
  }
}
```

#### Audio

The `audio` update type is used to send audio updates to the client.
This update type is sent when the audio state of the tile changes.

__The `state` object for the `audio` update type has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `state` | Number | The mode the device is in. 0 = idle, 1 = playing, 2 = paused. |
| `looping` | Boolean | Whether the device is looping the audio or not. |
| `sound` | String | The sound the device is playing. |
| `volume` | Number | The volume of the device. |

__Example of an `audio` state update:__

```json
{
  "action": "tile",
  "type": "audio",
  "tile": "tile-1",
  "args": {
    "state": 0,
    "looping": false,
    "sound": "sound-1",
    "volume": 50
  }
}
```

#### Light

The `light` update type is used to send light updates to the client.
This update type is sent when the light state of the tile changes.

__The `state` object for the `light` update type has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `brightness` | Number | The brightness of the device. |
| `pixels` | Array | The list of colors of each pixel, should have a format of {r: 0, g: 0, b: 0, w:0} for each pixel. |

__Example of a `light` state update:__

```json
{
  "action": "tile",
  "type": "light",
  "tile": "tile-1",
  "args": {
    "brightness": 50,
    "pixels": [
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
      {"r": 255, "g": 0, "b": 0, "w": 0},
      {"r": 0, "g": 255, "b": 0, "w": 0},
      {"r": 0, "g": 0, "b": 255, "w": 0},
      {"r": 0, "g": 0, "b": 0, "w": 255},
    ]
  }
}
```

#### Full

The `full` update type is used to send the full state of the tile.
This update type is sent when the client first subscribes to the state of a tile.

__The `state` object for the `full` update type has the following properties:__

| Property | Type | Description |
| -------- | ---- | ----------- |
| `system` | Object | The system state of the device. can be found [here](#system). |
| `audio` | Object | The audio state of the device. can be found [here](#audio). |
| `light` | Object | The light state of the device. can be found [here](#light). |
| `presence` | Object | The presence state of the device. can be found [here](#presence). |

__Example of a `full` state update:__

```json
{
  "action": "tile",
  "type": "full",
  "tile": "tile-1",
  "args": {
    "system": {
      "firmware": "1.0.0",
      "hardware": "1.0.0",
      "ping": false,
      "uptime": 0,
      "sounds": ["sound-1", "sound-2"]
    },
    "audio": {
      "state": 0,
      "looping": false,
      "sound": "sound-1",
      "volume": 50
    },
    "light": {
      "brightness": 50,
      "pixels": [
        {"r": 255, "g": 0, "b": 0, "w": 0},
        {"r": 0, "g": 255, "b": 0, "w": 0},
        {"r": 0, "g": 0, "b": 255, "w": 0},
        {"r": 0, "g": 0, "b": 0, "w": 255},
        {"r": 255, "g": 0, "b": 0, "w": 0},
        {"r": 0, "g": 255, "b": 0, "w": 0},
        {"r": 0, "g": 0, "b": 255, "w": 0},
        {"r": 0, "g": 0, "b": 0, "w": 255},
        {"r": 255, "g": 0, "b": 0, "w": 0},
        {"r": 0, "g": 255, "b": 0, "w": 0},
        {"r": 0, "g": 0, "b": 255, "w": 0},
        {"r": 0, "g": 0, "b": 0, "w": 255},
      ]
    },
    "presence": {
      "detected": false
    }
  }
}
```
