# SVG Logo Design Patterns

Ready-to-use templates for each logo type. Customize colors, proportions, and elements.

## Wordmark

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80"
     role="img" aria-labelledby="wm-title">
  <title id="wm-title">Brand Name</title>
  <defs><style>
    .wordmark { font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                font-size: 48px; font-weight: 700; fill: #1F2937; }
  </style></defs>
  <text x="150" y="55" text-anchor="middle" class="wordmark">BRAND</text>
</svg>
```

Wordmark tips: use `letter-spacing` for tracking, `font-weight: 300` for light/elegant.

## Lettermark

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"
     role="img" aria-labelledby="lm-title">
  <title id="lm-title">BN Lettermark</title>
  <defs><style>
    .letter { font-family: 'Inter', Arial, sans-serif;
              font-size: 56px; font-weight: 800; fill: #FFFFFF; }
  </style></defs>
  <rect width="100" height="100" rx="16" fill="#4F46E5"/>
  <text x="50" y="65" text-anchor="middle" class="letter">BN</text>
</svg>
```

## Pictorial Mark (Icon)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"
     role="img" aria-labelledby="pm-title">
  <title id="pm-title">Mountain Icon</title>
  <defs>
    <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#06B6D4"/>
      <stop offset="100%" style="stop-color:#2563EB"/>
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="48" fill="url(#sky)"/>
  <polygon points="50,25 75,70 25,70" fill="#FFFFFF"/>
  <polygon points="38,45 55,70 21,70" fill="#E0F2FE" opacity="0.7"/>
</svg>
```

## Abstract Mark

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"
     role="img" aria-labelledby="am-title">
  <title id="am-title">Abstract Mark</title>
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4F46E5"/>
      <stop offset="100%" style="stop-color:#7C3AED"/>
    </linearGradient>
  </defs>
  <!-- Overlapping circles -->
  <circle cx="38" cy="42" r="30" fill="#4F46E5" opacity="0.8"/>
  <circle cx="62" cy="42" r="30" fill="#7C3AED" opacity="0.8"/>
  <circle cx="50" cy="62" r="30" fill="#06B6D4" opacity="0.8"/>
</svg>
```

## Geometric Icon

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"
     role="img" aria-labelledby="gi-title">
  <title id="gi-title">Hexagon Icon</title>
  <defs>
    <linearGradient id="hex-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4F46E5"/>
      <stop offset="100%" style="stop-color:#7C3AED"/>
    </linearGradient>
  </defs>
  <polygon points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5"
           fill="url(#hex-grad)" stroke="#312E81" stroke-width="2"/>
  <circle cx="50" cy="50" r="20" fill="#FFFFFF"/>
</svg>
```

## Combination Mark (Horizontal)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 80"
     role="img" aria-labelledby="cm-title">
  <title id="cm-title">Brand Logo</title>
  <defs><style>
    .brand-text { font-family: 'Inter', Arial, sans-serif;
                  font-size: 28px; font-weight: 700; fill: #1F2937; }
  </style></defs>
  <!-- Icon -->
  <circle cx="40" cy="40" r="32" fill="#4F46E5"/>
  <path d="M28,38 L36,48 L54,28" stroke="#FFF" stroke-width="4"
        fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Text -->
  <text x="90" y="48" class="brand-text">BRANDNAME</text>
</svg>
```

## Combination Mark (Vertical)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 140"
     role="img" aria-labelledby="cmv-title">
  <title id="cmv-title">Brand Logo</title>
  <defs><style>
    .brand-text-v { font-family: 'Inter', Arial, sans-serif;
                    font-size: 20px; font-weight: 700; fill: #1F2937; }
  </style></defs>
  <!-- Icon centered -->
  <circle cx="60" cy="50" r="38" fill="#4F46E5"/>
  <path d="M45,48 L55,60 L78,35" stroke="#FFF" stroke-width="4"
        fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Text below -->
  <text x="60" y="115" text-anchor="middle" class="brand-text-v">BRAND</text>
</svg>
```

## Emblem

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"
     role="img" aria-labelledby="em-title">
  <title id="em-title">Brand Emblem</title>
  <defs><style>
    .emblem-text { font-family: 'Georgia', serif;
                   font-size: 14px; font-weight: 700; fill: #FFFFFF;
                   letter-spacing: 0.15em; }
  </style></defs>
  <!-- Outer circle -->
  <circle cx="60" cy="60" r="56" fill="#1F2937" stroke="#EFC07B" stroke-width="3"/>
  <!-- Inner circle -->
  <circle cx="60" cy="60" r="44" fill="none" stroke="#EFC07B" stroke-width="1"/>
  <!-- Central icon -->
  <polygon points="60,28 68,48 90,48 72,60 80,80 60,68 40,80 48,60 30,48 52,48"
           fill="#EFC07B"/>
  <!-- Text on circular path -->
  <text x="60" y="105" text-anchor="middle" class="emblem-text">ESTABLISHED 2024</text>
</svg>
```

## Monochrome Variations

For any logo, create monochrome versions by replacing all fills:

```xml
<!-- Monochrome Dark (for light backgrounds) -->
<style>.primary, .secondary, .accent { fill: #1F2937; }</style>

<!-- Monochrome Light (for dark backgrounds) -->
<style>.primary, .secondary, .accent { fill: #FFFFFF; }</style>
```
