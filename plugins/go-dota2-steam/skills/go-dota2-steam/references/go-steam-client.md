# go-steam Client Reference

Go library implementing Valve's Steam network protocol. Repository: `github.com/paralin/go-steam`

## Core Architecture

```go
import "github.com/paralin/go-steam"

client := steam.NewClient()
go func() {
    for event := range client.Events() {
        switch e := event.(type) {
        case *steam.LoggedOnEvent:
            // Handle login success
        case *steam.DisconnectedEvent:
            // Handle disconnect
        case error:
            // Handle error
        }
    }
}()
client.Connect()
```

## Client Type

```go
type Client struct {
    Auth          *Auth           // Authentication module
    Social        *Social         // Friends/groups/chat
    Web           *Web            // Web session
    Notifications *Notifications  // User notifications
    Trading       *Trading        // Trade requests
    GC            *GameCoordinator// Game coordinator bridge
}
```

**Key Methods:**
- `NewClient() *Client` - Create client
- `Connect() error` - Connect to random Steam server
- `ConnectTo(addr *PortAddr) error` - Connect to specific server
- `Disconnect()` - Graceful disconnect
- `Events() <-chan interface{}` - Event channel
- `RegisterPacketHandler(handler PacketHandler)` - Custom handler

## Authentication

```go
// Username + Password
client.Auth.LogOn(&steam.LogOnDetails{
    Username: "user",
    Password: "pass",
})

// With 2FA
client.Auth.LogOn(&steam.LogOnDetails{
    Username: "user",
    Password: "pass",
    AuthCode: "123456",
})

// With Login Key (persistent)
client.Auth.LogOn(&steam.LogOnDetails{
    Username: "user",
    LoginKey: "saved_key",
})

// With Machine Auth (device whitelist)
client.Auth.LogOn(&steam.LogOnDetails{
    Username:       "user",
    Password:       "pass",
    SentryFileHash: machineAuthHash,
})
```

## Social Module

```go
s := client.Social

// Friends
s.AddFriend(steamId)
s.RemoveFriend(steamId)
s.RequestFriendInfo([]SteamId)

// Messaging
s.SendMessage(steamId, steam.EChatEntryType_ChatMsg, "Hello")

// Chat Rooms
s.JoinChat(chatId)
s.LeaveChat(chatId)
s.KickChatMember(chatId, userId)
s.BanChatMember(chatId, userId)

// Cached data
s.Friends  // *socialcache.FriendsList
s.Groups   // *socialcache.GroupsList
s.Chats    // *socialcache.ChatsList
```

## Trading Module

```go
t := client.Trading
t.RequestTrade(otherSteamId)
t.RespondRequest(requestId, true/false)
t.CancelRequest(otherSteamId)
```

## Web Session

```go
// After WebSessionIdEvent
client.Web.LogOn()

// After WebLoggedOnEvent - cookies available:
client.Web.SessionId        // Web session cookie
client.Web.SteamLogin       // HTTP auth cookie
client.Web.SteamLoginSecure // HTTPS auth cookie
```

## Game Coordinator

```go
gc := client.GC
gc.SetGamesPlayed(570)  // 570 = Dota 2 AppID
gc.RegisterPacketHandler(handler)
gc.Write(protoMessage)
```

## SteamID Utilities

```go
import "github.com/paralin/go-steam/steamid"

id := steamid.NewId("[U:1:12345]")    // Steam3
id := steamid.NewId("STEAM_0:1:6172") // Steam2
id := steamid.NewId("76561198012345") // Decimal

id.ToUint64()
id.ToSteam2()   // STEAM_X:Y:Z
id.ToSteam3()   // [U:1:...]
id.ClanToChat()
id.ChatToClan()
```
