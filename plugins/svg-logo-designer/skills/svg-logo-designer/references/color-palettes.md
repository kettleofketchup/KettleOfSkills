# Color Palettes for Logo Design

## Color Psychology

| Color | Hex Examples | Conveys | Industries |
|-------|-------------|---------|------------|
| Blue | `#0066CC`, `#4F46E5`, `#2563EB` | Trust, professionalism, stability | Finance, tech, healthcare |
| Green | `#10B981`, `#059669`, `#3A6B35` | Growth, health, eco-friendly | Environment, wellness, finance |
| Red | `#DC2626`, `#EF4444` | Energy, passion, urgency | Food, entertainment, retail |
| Purple | `#7C3AED`, `#8B5CF6` | Creativity, luxury, spirituality | Beauty, tech, creative |
| Orange | `#F97316`, `#FB923C` | Friendly, energetic, affordable | Retail, food, entertainment |
| Yellow | `#FBBF24`, `#FCD34D` | Optimism, clarity, warmth | Food, children, energy |
| Black/Gray | `#1F2937`, `#6B7280` | Sophisticated, modern, classic | Luxury, fashion, technology |

## Industry-Specific Palettes

### Tech / SaaS
- Electric Blue + Silver: `#00C4FF`, `#B0BEC5`, `#ECEFF1`
- Dark Mode: `#0F172A` bg, `#06B6D4` teal accent, `#8B5CF6` violet
- AI Gradient: `#7C3AED` to `#2563EB` (purple-to-blue)
- 59% of tech logos use blue; 61% of top tech company logos feature it

### Healthcare / Wellness
- Emerald Trust: `#0D4C3C`, `#2D5A4A`, `#7BA05B`, `#F4F1EB`
- Calm Clinical: `#1E40AF`, `#FFFFFF`, `#F0FDF4`

### Finance / Luxury
- Midnight & Gold: `#1A1A2E`, `#16213E`, `#0F3460`, `#EFC07B`
- Desaturated Metallics: matte gold, champagne silver, rusted bronze

### Sustainability / Natural
- Earthy: `#E3B448` mustard, `#CBD18F` sage, `#3A6B35` forest
- Terracotta + Cream: `#C45B28`, `#F5E6D3`

### Creative / Startup
- Bold Contrast: `#FF3366` pink, `#003366` navy
- Orange + Blue: `#FF6B35`, `#2563EB`

## Brand Reference Colors

| Brand | Primary | Category |
|-------|---------|----------|
| Discord | `#5865F2` | Communication |
| GitHub | `#4078C0` | Developer |
| Docker | `#0DB7ED` | DevOps |
| Dropbox | `#007EE5` | Cloud |
| Google | `#4285F4`, `#34A853`, `#FBBC05`, `#EA4335` | Multi |
| Facebook | `#1877F2` | Social |
| LinkedIn | `#0A66C2` | Professional |
| GitLab | `#FCA326` | Developer |
| AWS | `#FF9900` | Cloud |
| Auth0 | `#16214D` | Security |
| DigitalOcean | `#008BCF` | Cloud |

## 2024-2025 Trends

1. **Soft bolds** -- apricot and lavender tones (62% of top digital ads use these)
2. **Restrained gradients** -- layered purples, pinks, blues for AI/SaaS
3. **Earthy muted tones** -- terracottas, deep naturals for sustainability
4. **High-chroma accents** -- ultra-saturated single pops against neutrals
5. **Limit logos to 2-3 colors maximum**

## WCAG Accessibility

| Standard | Normal Text | Large Text | Non-Text UI |
|----------|------------|------------|-------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | -- |

Note: text in logos has no WCAG contrast requirement, but accessible design is best practice.

High-contrast pairs passing AA:
- `#1A1A2E` on `#FFFFFF` -- exceeds 7:1
- `#2563EB` on `#FFFFFF` -- ~4.6:1, passes AA
- `#FFFFFF` on `#0F172A` -- exceeds 7:1

Contrast ratios cannot be rounded: 4.47:1 fails 4.5:1.

## Gradient Patterns

```xml
<!-- Linear gradient -->
<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" style="stop-color:#4F46E5"/>
  <stop offset="100%" style="stop-color:#7C3AED"/>
</linearGradient>

<!-- Radial gradient -->
<radialGradient id="grad2" cx="50%" cy="50%" r="50%">
  <stop offset="0%" style="stop-color:#06B6D4"/>
  <stop offset="100%" style="stop-color:#2563EB"/>
</radialGradient>
```

Always design a single-color fallback -- gradients fail in monochrome contexts.
