# go-dota2 SOCache, Events, and Generated API

## SOCache (Shared Object Cache)

Real-time tracking of lobbies, parties, items. Subscribe to object type events:

```go
cache := d.GetCache()

// Subscribe to lobby events
eventCh, cancel, err := cache.SubscribeType(cso.Lobby)
if err != nil {
    return err
}
defer cancel()

for event := range eventCh {
    lobby := event.Object.(*protocol.CSODOTALobby)
    switch event.EventType {
    case socache.EventTypeCreate:
        // Lobby created
    case socache.EventTypeUpdate:
        // Lobby updated
    case socache.EventTypeDestroy:
        // Lobby destroyed
    }
}
```

**CSO Types (cso package):**
- `cso.Lobby` - Lobby state
- `cso.Party` - Party state
- `cso.PartyInvite` - Party invitations
- `cso.LobbyInvite` - Lobby invitations
- `cso.EconItem` - Inventory items

## Events Reference

**Connection:**
- `GCConnectionStatusChanged` - GC connection state change
- `ClientWelcomed` - GC welcome with account data
- `UnhandledGCPacket` - Unknown message received

**Chat:**
- `ChatMessage` - Chat message received
- `JoinedChatChannel` - Joined channel

**Invitations:**
- `InvitationCreated` - New invite received

**Ready Check:**
- `PartyReadyCheckRequest` - Ready check initiated

## Generated API Methods

The library auto-generates 200+ methods in `client_generated.go`. Common patterns:

**Fire-and-forget (no response):**
```go
d.SomeAction(param1, param2)
```

**Request/Response (with context):**
```go
ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()
response, err := d.SomeQuery(ctx, param1)
```

### Lobby Methods
- `CreateLobby`, `LeaveLobby`, `DestroyLobby`
- `SetLobbyTeamSlot`, `KickLobbyMember`, `AbandonLobby`
- `ApplyTeamToLobby`, `ClearTeamFromLobby`
- `RespondLobbyInvite`, `InviteToLobby`

### Party Methods
- `LeaveParty`, `RespondPartyInvite`
- `SendPartyReadyCheck`, `AckPartyReadyCheck`
- `SetPartyLeader`, `SetPartyOpen`, `CancelPartyInvites`

### Match/Profile Methods
- `GetMatchDetails`, `GetPlayerMatches`
- `GetProfile`, `GetBattleReportInfo`

### Spectator Methods
- `FindTopSourceTVGames`, `WatchGame`, `CancelWatchGame`

### Guild Methods
- `CreateGuild`, `EditGuildDetails`
- `InviteToGuild`, `RespondGuildInvite`

### Battle Pass/Events
- `ClaimEventAction`, `GetEventPoints`
- `ClaimBingoRow`, `GetBingoUserData`

### Fantasy/Tournaments
- `SubmitFantasyTeamSelection`, `GetFantasyPlayerStats`
- `JoinWeekendTourney`

## MakeRequest Pattern

For custom request/response calls:

```go
response := &protocol.CMsgSomeResponse{}
err := d.MakeRequest(
    ctx,
    uint32(protocol.EDOTAGCMsg_k_EMsgSomeRequest),
    &protocol.CMsgSomeRequest{/* ... */},
    uint32(protocol.EDOTAGCMsg_k_EMsgSomeResponse),
    response,
)
```
