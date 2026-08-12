# go-steam Events, TF2, and Inventory

## Events Reference

**Authentication:**
- `LoggedOnEvent` - Login success (SteamId, Result)
- `LogOnFailedEvent` - Login failed (Result code)
- `LoginKeyEvent` - New persistent login key
- `LoggedOffEvent` - Disconnected by server
- `MachineAuthUpdateEvent` - Machine auth hash needed
- `AccountInfoEvent` - Account details received

**Social:**
- `FriendsListEvent` - Friends list updated
- `FriendStateEvent` - Friend status changed
- `FriendAddedEvent` - Friend added
- `PersonaStateEvent` - Friend persona changed
- `ChatMsgEvent` - Message received
- `ChatEnterEvent` - Joined chat
- `ChatInviteEvent` - Chat invite received
- `ProfileInfoEvent` - Profile info received

**Trading:**
- `TradeProposedEvent` - Trade proposal received
- `TradeResultEvent` - Trade result
- `TradeSessionStartEvent` - Trade session started

**Web:**
- `WebSessionIdEvent` - Web session ready (call Web.LogOn())
- `WebLoggedOnEvent` - Web login success
- `WebLogOnErrorEvent` - Web login failed

**Connection:**
- `ConnectedEvent` - Connected to Steam
- `DisconnectedEvent` - Disconnected
- `FatalErrorEvent` - Fatal error
- `ClientCMListEvent` - Server list (cache for reconnection)

## Common Event Handling Pattern

```go
case *steam.LogOnFailedEvent:
    if e.Result == steam.EResult_AccountLogonDenied {
        // Need 2FA code
    }
case *steam.MachineAuthUpdateEvent:
    // Save sentry hash for future logins
    ioutil.WriteFile("sentry.bin", e.Hash, 0600)
case *steam.LoginKeyEvent:
    // Save login key for persistent auth
    saveLoginKey(e.UniqueId, e.LoginKey)
```

## TF2 Module

```go
import "github.com/paralin/go-steam/tf2"

tf2Client := tf2.New(client)
tf2Client.SetPlaying(true)

// Wait for GCReadyEvent, then:
tf2Client.SetItemPosition(assetId, position)
tf2Client.DeleteItem(assetId)
tf2Client.NameItem(assetId, "New Name")
tf2Client.CraftItems(recipe, item1, item2)
```

## Inventory Access

```go
import "github.com/paralin/go-steam/economy/inventory"

// Fetch inventory (requires web session)
inv, err := inventory.GetFullInventory(apiGetFunc, steamId, appId, contextId)

inv.Items        // map[uint64]Item
inv.Descriptions // map[string]ItemDescription
inv.Items.Get(assetId)
inv.Descriptions.Get(classId, instanceId)
```
