# Open WebUI Functions Overview

## What Are Functions?

Functions are plugins for Open WebUI. They extend its capabilities -- adding support for new AI model providers like Anthropic or Vertex AI, tweaking how messages are processed, or introducing custom buttons to the interface.

Unlike external tools that may require complex integrations, **Functions are built-in and run within the Open WebUI environment.** They are fast, modular, and don't rely on external dependencies. Written in **pure Python**.

## Types of Functions

### 1. Pipe Function -- Create Custom "Agents/Models"

A Pipe Function creates **custom agents/models** or integrations, which appear in the interface as standalone models.

- Pipes let you define complex workflows. For instance, send data to **Model A** and **Model B**, process their outputs, and combine results.
- Pipes don't even have to use AI -- they can be setups for search APIs, weather data, or Home Assistant.
- When enabled, **Pipe Functions show up as their own selectable model**.

### 2. Filter Function -- Modify Inputs and Outputs

A Filter Function tweaks data before it gets sent to the AI **or** after it comes back.

- **Inlet**: Adjust the input sent to the model (add instructions, keywords, formatting).
- **Outlet**: Modify the output from the model (clean up, adjust tone, format data).
- Filters are **linked to specific models** or can be enabled **globally** for all models.

### 3. Action Function -- Add Custom Buttons

An Action Function adds **custom buttons** to the chat interface.

- Actions define **interactive shortcuts** that trigger specific functionality directly from the chat.
- Buttons appear underneath individual chat messages.

## How to Use Functions

### 1. Install Functions
Install via the Open WebUI interface or by importing manually. Community functions at [openwebui.com/search](https://openwebui.com/search).

### 2. Enable Functions
- **Pipe Function**: becomes available as its own model in the interface.
- **Filter and Action Functions**: must be assigned to specific models or enabled globally.

### 3. Assign Filters or Actions to Models
- Navigate to `Workspace => Models` and assign.
- Or enable globally via `Workspace => Functions`, select "..." menu, toggle **Global** switch.

## Quick Summary

- **Pipes** appear as standalone models you can interact with.
- **Filters** modify inputs/outputs for smoother AI interactions.
- **Actions** add clickable buttons to individual chat messages.
