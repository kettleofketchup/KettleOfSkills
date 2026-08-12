# Environment Variables: Gotchas and Common Patterns

Continuation of [environment-vars.md](environment-vars.md).

## Checking Env Var Source

```go
viper.SetEnvPrefix("APP")
viper.AutomaticEnv()

// Check if value came from env or config
if os.Getenv("APP_DEBUG") != "" {
    fmt.Println("Debug mode set via environment")
}
```

## Common Patterns

### 12-Factor App Config

```go
viper.SetEnvPrefix("APP")
viper.AutomaticEnv()
viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

// Defaults for local dev
viper.SetDefault("database.host", "localhost")
viper.SetDefault("database.port", 5432)

// In production: APP_DATABASE_HOST and APP_DATABASE_PORT override
```

### Optional Config File with Env Override

```go
viper.SetConfigName("config")
viper.AddConfigPath(".")
viper.SetEnvPrefix("APP")
viper.AutomaticEnv()

// Config file optional
_ = viper.ReadInConfig()

// Env vars always work regardless of config file
```

## Gotchas

### Empty String vs Unset

```go
// os.Setenv("APP_NAME", "")  // Set to empty string
// vs not setting APP_NAME at all

// Viper treats empty string as a value
// Use IsSet() to check if key has any value
if viper.IsSet("name") {
    name := viper.GetString("name")  // Could be ""
}
```

### BindEnv Must Be Called Before Get

```go
// This works
viper.BindEnv("port")
viper.GetInt("port")

// AutomaticEnv() is easier - no need to bind each key
viper.AutomaticEnv()
viper.GetInt("port")  // Automatically checks env
```
