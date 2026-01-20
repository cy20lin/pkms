# favicon guide

## Prompot for generating favicon

- Following prompt is coauthored with chatgpt
- Image is generated with copilot

```text
Design a minimalist icon representing an anchor stabilizing information.

Visual concept:
- A simple anchor symbol positioned above or partially embedded into
- A stack of abstract information layers (e.g. flat rectangles, slabs, or sheets)
- The anchor visually connects to or presses down on the information stack

Style:
- Flat, geometric, minimal
- No text, no letters, no numbers
- Clear silhouette
- Symmetrical or visually balanced

Information layers:
- Abstract (not realistic paper)
- No visible text or icons on them
- Represent accumulated knowledge, not documents UI

Anchor:
- Simplified, iconic shape
- Not nautical-detailed
- More symbolic than literal

Color & contrast:
- Monochrome or two-tone
- Must work inverted (light/dark mode)
- No gradients, no shadows

Scale:
- Must remain legible as a favicon (16x16, 32x32, 64x64)
```

## How to make a icon

- Start gimp
- Create a new layer: 
  - Click `Layer` on Menu
  - Click `New Layer` on Menu item
  - Set New Layer Settings
    - Layer name: `Back`
    - Color tag: None
  - Click `OK` Button
- Set Horizontal Center Guide Line
  - Image > Guide > New Guide, 50% horizontal
- Set Vertical Center Guide Line
  - Image > Guide > New Guide, 50% vertical
- Create a circle
  - Left Top Panel: Ellipse Select Tool (E)
  - Drag a rectangle
  - Set position x=0,y=0,width=1024,height=1024
  - Drag a color Top left from foreground/background pattle
- Scale Image
  - Image > Scale Image > 
    - a.
      - ImageSize: Weight=64,Height=64
      - Interpolation: None
    - b.
      - ImageSize: Weight=64,Height=64
      - Interpolation: LoHalo
    - c.
      - ImageSize: Weight=512,Height=512
      - Interpolation: None
- Export icon
  - File > Export
  - Filename=\<filename\>-lohalo.ico
    - 8 bpp, 1-bit alpha, 256 slot palette
    - for 64x64 icon
  - Filename=\<filename\>.ico
    - 4 bpp, 1-bit alpha, 16 slot palette
    - for 64x64 icon
  - Filename=\<filename\>.png
    - Pixel format: 8 bpc gray
    - Compression level: 3
    - Save color values from transparent pixels
    - Metadata
      - Save bacakground Color
      - Save creation time
      - Save resolution
    - for 512x512 icon
  - Click `Export` button

## Notes for filename

- wcbg: white-circle-background
- lohalo: for using `LoHalo` Interpolation
