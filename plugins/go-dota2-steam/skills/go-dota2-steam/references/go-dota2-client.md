# go-dota2 Client Reference

DOTA 2 Game Coordinator client plugin for go-steam. Repository: `github.com/paralin/go-dota2`

## Setup and Initialization

```go
import (
    "github.com/paralin/go-steam"
    "github.com/paralin/go-dota2"
    "github.com/paralin/go-dota2/protocol"
    "github.com/paralin/go-dota2/cso"
    "github.com/paralin/go-dota2/events"
    "github.com/sirupsen/logrus"
)

// After steam client connected and logged in
client := steam.NewClient()
logger := logrus.New()

d := dota2.New(client, logger)
d.SetPlaying(true)   // Tell Steam we're playing Dota 2
d.SayHello()         // Initiate GC connection
```

## Client Type

```go
type Dota2 struct {
    client  *steam.Client
    cache   *socache.SOCache
    state   state.Dota2State
}
```

**Key Methods:**
- `New(client, logger) *Dota2` - Create client
- `SetPlaying(bool)` - Toggle Dota 2 playing status
- `SayHello(versions...)` - Initiate GC hello
- `GetCache() *SOCache` - Get shared object cache

## Connection Events

```go
// Listen for GC connection
client.On(func(e *events.GCConnectionStatusChanged) {
    if e.NewState == protocol.GCConnectionStatus_GCConnectionStatus_HAVE_SESSION {
        // GC session established
    }
})

// Welcome event with account data
client.On(func(e *events.ClientWelcomed) {
    // e.Msg contains welcome data
})
```

## Lobby Operations

```go
// Create lobby
details := &protocol.CMsgPracticeLobbySetDetails{
    GameName:   proto.String("My Lobby"),
    GameMode:   proto.Uint32(uint32(protocol.DOTA_GameMode_DOTA_GAMEMODE_AP)),
    ServerRegion: proto.Uint32(1), // US West
}
d.CreateLobby(details)

// Create with context (leaves current lobby first)
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()
err := d.LeaveCreateLobby(ctx, details, true)

// Other lobby operations
d.LeaveLobby()
d.DestroyLobby(ctx)
d.KickLobbyMember(memberId, team)
d.ApplyTeamToLobby(teamID)
d.ClearTeamFromLobby()
d.RespondLobbyInvite(inviteId, accept)
```

## Party Operations

```go
d.LeaveParty()
d.RespondPartyInvite(partyId, accept)
d.SendPartyReadyCheck()
d.AckPartyReadyCheck(status)
```

## Chat Operations

```go
d.SendChannelMessage(channelID, "message")
```

## State Access

```go
state := d.GetState()
state.ConnectionStatus  // GCConnectionStatus
state.Lobby            // *CSODOTALobby
state.Party            // *CSODOTAParty
state.PartyInvite      // *CSODOTAPartyInvite
```

## Protocol Types

Key protobuf types in `protocol` package:

```go
// Lobby
*protocol.CSODOTALobby
*protocol.CMsgPracticeLobbySetDetails

// Party
*protocol.CSODOTAParty
*protocol.CSODOTAPartyInvite

// Connection
protocol.GCConnectionStatus_GCConnectionStatus_HAVE_SESSION

// Game Modes
protocol.DOTA_GameMode_DOTA_GAMEMODE_AP  // All Pick
protocol.DOTA_GameMode_DOTA_GAMEMODE_CM  // Captains Mode
```
