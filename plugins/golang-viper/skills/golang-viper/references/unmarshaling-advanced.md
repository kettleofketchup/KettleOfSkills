# Unmarshaling: Sub-Configs, Strict Mode, and Gotchas

Continuation of [unmarshaling.md](unmarshaling.md).

## Sub-Configs

Extract a subtree as a new Viper instance.

```go
dbViper := viper.Sub("database")
host := dbViper.GetString("host")  // Was "database.host"

var dbCfg DatabaseConfig
dbViper.Unmarshal(&dbCfg)
```

## Strict Unmarshaling

Error on unknown fields.

```go
err := viper.Unmarshal(&cfg, func(dc *mapstructure.DecoderConfig) {
    dc.ErrorUnused = true
})
```

## Default Values Gotcha

Viper defaults override struct field values. Set Viper defaults explicitly.

```go
// Wrong - struct default gets overwritten
var cfg Config
cfg.Port = 8080
viper.Unmarshal(&cfg)  // Port becomes 0 if not in config

// Right - use Viper defaults
viper.SetDefault("port", 8080)
viper.Unmarshal(&cfg)
```
