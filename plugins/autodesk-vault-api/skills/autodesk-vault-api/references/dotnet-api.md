# Vault .NET SDK (Web Services + VDF)

The on-premise, full-coverage surface. SOAP under the hood, exposed as .NET assemblies.
Install via the Vault client installer (select **SDK** under optional components) or from
the Autodesk Developer Network. Local docs land at `<SDK install dir>\docs\VaultSDK.chm`.

## Project setup

- Target **.NET Framework 4.8** — the assemblies are not .NET Core / .NET 5+ compatible.
- Set `Copy Local = True` on every SDK reference; unlike AutoCAD, Vault assemblies are not
  preloaded into the host process and must ship with the application.
- The SDK version must match the server version. A 2025 SDK will not talk to a 2024 server.

## Two layers, one connection

| Layer | Assembly / namespace | Use for |
|-------|----------------------|---------|
| Web Services | `Autodesk.Connectivity.WebServices` | Everything; raw, complete, verbose |
| Web Services tools | `Autodesk.Connectivity.WebServicesTools` | `WebServiceManager`, credential classes |
| VDF | `Autodesk.DataManagement.Client.Framework` (alias `VDF`) | File transfer, working folders, property dictionaries |

VDF wraps the web services and handles the tedious parts (relationship gathering, local file
placement, checkout state). Prefer VDF for file transfer; drop to `WebServiceManager` for
anything VDF does not expose. A VDF `Connection` always exposes
`connection.WebServiceManager`, so the two mix freely in one session.

## Connect

```csharp
using Autodesk.Connectivity.WebServices;
using Autodesk.Connectivity.WebServicesTools;
using VDF = Autodesk.DataManagement.Client.Framework;

// Raw web services
var cred = new UserPasswordCredentials("localhost", "Vault", "Administrator", "", true);
var webSvc = new WebServiceManager(cred);

// VDF connection (preferred entry point)
VDF.Vault.Currency.Connections.Connection connection =
    VDF.Vault.Library.ConnectionManager.LogIn(
        "localhost", "Vault", "Administrator", "",
        VDF.Vault.Currency.Connections.AuthenticationFlags.Standard, null).Connection;
```

Credential classes: `UserPasswordCredentials`, `WinAuthCredentials` (Windows SSO),
`AutodeskAuthCredentials` (Autodesk ID / APS token), `SessionCredentials` (reuse a ticket),
`ContainerCredentials`, `WebServiceCredentials`. Always `ConnectionManager.LogOut(connection)`
in a `finally` — Vault licences are seat-bound and leaked sessions exhaust them.

## Services on WebServiceManager

| Service | Covers |
|---------|--------|
| `DocumentService` (+ `DocumentServiceExtensions`) | Files, folders, check-in/check-out, lifecycle state, links |
| `PropertyService` | Property definitions, UDPs, property values, entity associations |
| `FilestoreService` | Low-level byte upload/download (VDF wraps this) |
| `SecurityService` | Users, groups, roles, ACLs, sessions |
| `ItemService` / `ChangeOrderService` / `CustomEntityService` | Items and BOMs, ECOs, custom objects — **Professional only** |
| `JobService` | Job queue submit/dequeue |
| `KnowledgeVaultService` | Vault list, server info, licensing |

Edition gates matter: Vault **Basic** has the Web Service API only. The **Vault Client API**
(custom commands/tabs) and **Job Processor API** require Workgroup or Professional. Item,
change order, and custom entity services are Professional-only — calling them against Basic
throws rather than returning empty.

## Search: never hardcode property IDs

Property definition IDs differ per Vault. Resolve them at runtime.

```csharp
PropDef[] defs = webSvc.PropertyService.GetPropertyDefinitionsByEntityClassId("FILE");
PropDef nameDef = defs.Single(d => d.SysName == "Name");

var cond = new SrchCond {
    PropDefId = nameDef.Id,
    PropTyp   = PropertySearchType.SingleProperty,
    SrchOper  = 3,                       // 1 contains, 3 equals, 5 is not empty
    SrchRule  = SearchRuleType.Must,
    SrchTxt   = "bracket.ipt"
};
```

Valid `SrchOper` codes are property-type dependent — read them off the `PropDef` rather than
assuming. Results are paged; loop on the bookmark until `TotalHits` is reached, and break on
an empty page or the loop spins forever:

```csharp
var found = new List<File>(); string bookmark = string.Empty; SrchStatus status = null;
while (status == null || found.Count < status.TotalHits)
{
    File[] page = webSvc.DocumentService.FindFilesBySearchConditions(
        new[] { cond }, null, null, true, true, ref bookmark, out status);
    if (page == null || page.Length == 0) break;   // required guard
    found.AddRange(page);
}
```

## Download / check out via VDF

```csharp
var fileIter = new VDF.Vault.Currency.Entities.FileIteration(connection, found[0]);

var settings = new VDF.Vault.Settings.AcquireFilesSettings(connection) {
    LocalPath = new VDF.Currency.FolderPathAbsolute(@"C:\Vault\Work"),
    OrganizeFilesRelativeToCommonVaultRoot = true };
settings.OptionsRelationshipGathering.FileRelationshipSettings.IncludeChildren = true;
settings.DefaultAcquisitionOption =
    VDF.Vault.Settings.AcquireFilesSettings.AcquisitionOption.Download |
    VDF.Vault.Settings.AcquireFilesSettings.AcquisitionOption.Checkout;
settings.AddEntityToAcquire(fileIter);

var results = connection.FileManager.AcquireFiles(settings);
foreach (var r in results.FileResults)
    if (r.Exception != null) Console.WriteLine($"{r.File.EntityName}: {r.Exception.Message}");
```

`AcquireFiles` never throws for per-file failures — inspect `FileResults[].Exception` and
`.Status`. Member names shift between SDK releases; verify against the installed `VaultSDK.chm`.

## Extensions: job handlers and client plugins

Extensions live under `%allusersprofile%\Autodesk\Vault <year>\Extensions\<MyExtension>\` and
need a `*.vcet.config` beside the DLL, or they silently fail to load. The file may be named
anything, so long as it ends `.vcet.config`:

```xml
<configuration>
  <connectivity.ExtensionSettings2>
    <assembly>JobHandlerSample</assembly>
    <extensionType>JobProcessor</extensionType>   <!-- or VaultClient / WebService -->
  </connectivity.ExtensionSettings2>
</configuration>
```

```csharp
public class JobHandlerSample : IJobHandler
{
    public bool CanProcess(string strJobType) => strJobType.Equals("jobhandlersample");
    public JobOutcome Execute(IJobProcessorServices context, IJob job) => JobOutcome.Success;
}
```

Load requirements, all of which fail closed: exactly **one** public type implementing
`IJobHandler` per assembly; an assembly-level
`Autodesk.Connectivity.Extensibility.Framework.ApiVersionAttribute` matching the running Vault
API version. `CanProcess` is asked once at startup — restart the Job Processor to re-evaluate.
Sample handlers ship in the SDK under `JobProcessorApiSamples`.
