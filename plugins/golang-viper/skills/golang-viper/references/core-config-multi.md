# Core Config: Multiple Files, Merging, and Settings Inspection

Continuation of [core-config.md](core-config.md).

## Multiple Config Files

Use separate Viper instances for different config files.

```go
// Main config (settings)
mainViper := viper.New()
mainViper.SetConfigName("config")
mainViper.AddConfigPath(".")
mainViper.ReadInConfig()

// Secrets config (credentials)
secretsViper := viper.New()
secretsViper.SetConfigName("secrets")
secretsViper.AddConfigPath(".")
if err := secretsViper.ReadInConfig(); err != nil {
    if _, ok := err.(viper.ConfigFileNotFoundError); ok {
        fmt.Println("Warning: secrets.yaml not found")
    } else {
        return err
    }
}

// Use both
host := mainViper.GetString("server.host")
apiKey := secretsViper.GetString("api_key")
```

## Merging Multiple Config Files

Read additional configs that merge with existing values.

```go
viper.SetConfigName("config")
viper.ReadInConfig()

// Merge in overrides (won't error if file missing)
viper.SetConfigName("config.local")
viper.MergeInConfig()
```

## Getting the Config File Used

```go
fmt.Println("Config file used:", viper.ConfigFileUsed())
```

## Get All Settings

```go
all := viper.AllSettings()  // map[string]interface{}

// Get sub-tree as map
serverSettings := viper.Sub("server").AllSettings()
```
