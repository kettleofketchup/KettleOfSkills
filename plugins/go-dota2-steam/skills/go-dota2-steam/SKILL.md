---
name: go-dota2-steam
description: Go libraries for Steam and Dota 2 GC development. Use for paralin/go-steam, paralin/go-dota2, Steam bots, Dota 2 lobby managers, GC communication, SOCache events, parties/lobbies, or Steam account automation.
---

# go-dota2 and go-steam Development

Go libraries for Steam protocol and Dota 2 Game Coordinator integration.

## When to Use

- Building Steam bots or automation tools
- Creating Dota 2 lobby management systems
- Implementing Game Coordinator (GC) communication
- Handling SOCache (Shared Object Cache) events
- Managing Dota 2 parties, lobbies, or matches
- Steam authentication and session management
- Trading system integration

## Quick Start

```go
import (
    "github.com/paralin/go-steam"
    "github.com/paralin/go-dota2"
    "github.com/sirupsen/logrus"
)

// 1. Create Steam client and connect
client := steam.NewClient()
go func() {
    for event := range client.Events() {
        // Handle events
    }
}()
client.Connect()

// 2. Authenticate
client.Auth.LogOn(&steam.LogOnDetails{
    Username: "user",
    Password: "pass",
})

// 3. After LoggedOnEvent, initialize Dota 2
d := dota2.New(client, logrus.New())
d.SetPlaying(true)
d.SayHello()

// 4. Wait for GC connection, then use APIs
```

## Key Concepts

### Event-Driven Architecture
Both libraries use channels for events. Always listen in a goroutine:
```go
for event := range client.Events() {
    switch e := event.(type) {
    case *steam.LoggedOnEvent:
        // Handle login
    }
}
```

### SOCache for Real-Time State
Dota 2 uses SOCache for lobbies, parties, items. Subscribe to changes:
```go
eventCh, cancel, _ := d.GetCache().SubscribeType(cso.Lobby)
defer cancel()
for event := range eventCh {
    lobby := event.Object.(*protocol.CSODOTALobby)
    // React to lobby changes
}
```

### Context-Based Requests
Methods returning responses require context:
```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()
err := d.LeaveCreateLobby(ctx, details, true)
```

## Common Tasks

### Create Dota 2 Lobby
```go
details := &protocol.CMsgPracticeLobbySetDetails{
    GameName:     proto.String("My Lobby"),
    GameMode:     proto.Uint32(uint32(protocol.DOTA_GameMode_DOTA_GAMEMODE_AP)),
    ServerRegion: proto.Uint32(1),
}
d.CreateLobby(details)
```

### Handle Authentication
```go
case *steam.LogOnFailedEvent:
    if e.Result == steam.EResult_AccountLogonDenied {
        // Need 2FA code
    }
case *steam.MachineAuthUpdateEvent:
    // Save sentry hash for future logins
```

## References

Detailed API documentation in references/:
- `references/go-steam-client.md` - Steam client, auth, social, trading, web sessions, SteamID
- `references/go-steam-events.md` - Steam events reference, TF2 module, inventory access
- `references/go-dota2-client.md` - Dota 2 client, lobbies, parties, state, protocol types
- `references/go-dota2-api.md` - SOCache, events, generated API methods, MakeRequest

## External Resources

- go-steam: https://github.com/paralin/go-steam
- go-dota2: https://github.com/paralin/go-dota2
- Protocol buffers: See `protocol/` package in go-dota2
