# Map to Area — Project Specification

> GPS field area measurement app. Single-page web application packaged as an Android APK via Apache Capacitor.

---

## 1. Overview

| Property | Value |
|---|---|
| **Platform** | Android (Capacitor 5) + Web (PWA) |
| **Rendering** | Leaflet.js 1.9.4 |
| **Geospatial** | Turf.js 7 (area), custom Haversine (distance) |
| **Tile layers** | ESRI World Imagery (base), CARTO Dark Only Labels (overlay) |
| **Geocoding** | Nominatim (OpenStreetMap) |
| **Screenshot** | html2canvas (bundled locally in `vendor/`) |
| **Storage** | JSON file `maparea_data.json` in app Documents via Capacitor Filesystem (falls back to localStorage on web) |
| **Build** | GitHub Actions → debug APK |
| **Map zoom** | 2–22 (tiles natively to z19, upscaled smoothly beyond) |

---

## 2. Layout

### 2.1 Header — Row 1 (Mode + Units)

| Element | Type | Function |
|---|---|---|
| **Area / Length** | Toggle button | Switches between area mode (polygon fill) and length mode (open polyline) |
| **Area unit** | Dropdown | ft², Cents, Acres, m², Are, Hectares, km², yd², mi². Default: ft². Disabled in length mode |
| **Length unit** | Dropdown | ft, m, km, yd, mi. Default: ft |

### 2.2 Header — Row 2 (Drawing Actions)

| Element | Type | Function |
|---|---|---|
| **Start / Pause / Continue Drawing** | Toggle button | Cycles through drawing states without clearing points |
| **← Undo** | Button | Removes the last placed point (LIFO). Disabled when no points |
| **Redo →** | Button | Restores the last undone point. Cleared when a new point is added or a marker is dragged |
| **Clear** | Button | Removes all points and resets all measurements |
| **💾 Save** | Button | Saves current points + settings to localStorage with a user-given name |
| **📂 Open** | Button | Shows a modal list of saved maps; open restores points/settings and flies to bounds |
| **📷** | Button | Captures full-page screenshot (map + stats) at 2× resolution, triggers PNG download |

### 2.3 GPS Info Bar (below map)

| Element | Function |
|---|---|
| **GPS status dot** | Blue pulsing = fix, red = no fix |
| **GPS status text** | `off`, `searching...`, `active`, `error (n)` |
| **Lat / Lng** | Current GPS coordinates (6 decimal places) |
| **Accuracy** | GPS accuracy in meters |

### 2.4 Hint Bar (below GPS info)

| Element | Function |
|---|---|
| **Hint text** | Contextual instruction text that changes based on current action |

### 2.5 Bottom Panel — Stats

| Stat | Details |
|---|---|
| **Area/Primary** | Label changes to "Area" or "Length" based on mode. Auto-scaling display |
| **Perimeter** | Closed polygon perimeter. Hidden in length mode |
| **Length** | Cumulative distance point‑1 → last point along the path. Always shown |
| **Points** | Point count, displayed inside a bordered box |

### 2.6 Bottom Panel — Actions

| Element | Type | Function |
|---|---|---|
| **Pts toggle** | Checkbox switch | Shows/hides the numbered red circle markers on the map (polygon/polyline stays visible) |
| **Search input** | Text field + suggestions | Type place name → live dropdown of Nominatim suggestions; type lat,lng → coordinate parsing |
| **Go** | Button | Flies map to the selected suggestion or parsed coordinates |
| **📌** | Button | Saves current GPS location to the data JSON file with a name |
| **📍** | Button | Opens a modal listing saved locations with Go / Delete actions |
| **📍 Locate** | Button | Starts GPS (triggers permission prompt), moves map to current position, enables continuous tracking |
| **+GPS** | Button | Places a point at current GPS position (requires drawing mode) |
| **Live** | Toggle button | When ON (pulsing red), every GPS position update auto-adds a point to the polygon |

---

## 3. Drawing System

### 3.1 Point Placement

| Method | Condition |
|---|---|
| **Click on map** | Drawing mode active |
| **+GPS button** | Drawing mode active + GPS fix acquired |
| **Space key** | Drawing mode active + GPS fix acquired |
| **Live mode** | GPS tracking active + Live ON |

### 3.2 Point Adjustment

Each point has an invisible 18×18 px draggable overlay. Dragging updates the point in real-time, clears the redo stack, and re-enables undo.

### 3.3 Visual Feedback

| Element | Description |
|---|---|
| **Ghost line** | Dashed polyline from last point to cursor position |
| **Ghost marker** | Semi-transparent circle at cursor position |
| **Numbered circles** | Red circle markers with white tooltip numbers at each vertex |
| **Point toggle** | Switch to hide/show the numbered circles |

### 3.4 Drawing States

| State | Button text | Click handlers | Cursor |
|---|---|---|---|
| Idle (no points) | Start Drawing | Attached | crosshair |
| Active | Pause Drawing | Attached | crosshair |
| Paused (has points) | Continue Drawing | Detached | normal |

---

## 4. Measurement System

### 4.1 Area Mode

- Draws a closed polygon with semi-transparent red fill
- Displays: Area, Perimeter, Length
- Area supports unit conversion (9 units)
- Perimeter uses the same unit as Length

### 4.2 Length Mode

- Draws an open polyline (no fill, no closing edge)
- Displays: Length (as primary stat)
- Area unit dropdown is disabled

### 4.3 Area Units

| Unit | Conversion factor (× m²) |
|---|---|
| ft² | 10.7639 |
| Cent | 0.0247105 (100 cents = 1 acre) |
| Acre | 0.000247105 |
| m² | 1 |
| Are | 0.01 (1 are = 100 m²) |
| Hectare | 1×10⁻⁴ |
| km² | 1×10⁻⁶ |
| yd² | 1.19599 |
| mi² | 3.861×10⁻⁷ |

### 4.4 Length Units

| Unit | Conversion factor (× meters) |
|---|---|
| ft | 3.28084 |
| m | 1 |
| km | 0.001 |
| yd | 1.09361 |
| mi | 0.000621371 |

### 4.5 Algorithms

| Calculation | Method |
|---|---|
| **Area** | Turf.js `turf.area()` on closed polygon |
| **Perimeter** | Haversine sum of all edges (closing back to point 1) |
| **Length** | Haversine sum of consecutive edges point‑1 → last point |
| **Haversine** | `d = 2R · atan2(√a, √(1-a))` with R = 6,371,000 m |

All measurements recalculate on every point add/remove/drag, mode switch, and unit change.

---

## 5. GPS System

### 5.1 Starting GPS

- **Entry point**: Clicking **📍 Locate** or **Live** when GPS is off
- Calls `navigator.geolocation.getCurrentPosition()` first (triggers Android permission dialog)
- On success: moves map to position, then starts `watchPosition()` for continuous tracking
- On timeout/failure: retries once with 60 s timeout
- Permissions (`ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`) injected into `AndroidManifest.xml` by CI build script

### 5.2 While GPS is Active

| Feature | Behavior |
|---|---|
| **📍 Locate** | Moves map center to current GPS position |
| **📍📌 Save** | Saves current lat/lng to localStorage with a name |
| **+GPS button** | Drops a point at current GPS position into the polygon |
| **Live mode** | Auto-adds a point on every position update |
| **Space key** | Same as +GPS (drawing mode + GPS active) |
| **GPS marker** | Pulsing blue dot on map |
| **Accuracy circle** | Semi-transparent circle showing estimated accuracy radius |
| **GPS info bar** | Shows lat, lng, accuracy, status, fix dot |

### 5.3 Stopping GPS

- Occurs when GPS is lost (error callback from `watchPosition`)
- All GPS-dependent buttons are disabled
- Live mode auto-stops if active

---

## 6. Persistence

- **Storage**: single JSON document `maparea_data.json` in the app's Documents folder via Capacitor Filesystem
- **Fallback**: `localStorage` (keys `maparea_saved_gps` and `maparea_saved_maps`) on web, and as a mirror cache on Android
- **Migration**: on startup, any localStorage-only entries are merged into the JSON file
- **JSON shape**: `{ "pins": [...], "maps": { "name": {...} } }`

### 6.1 Saved Maps

- **Data per map**: name, points array, area unit, length unit, mode
- **Save**: prompts for name, writes the JSON file
- **Open**: modal with list of saved names, each with Open and Delete buttons
- **Re-save**: Saving with an existing name overwrites that entry
- **On open**: restores points, units, mode; flies map to polygon bounds

### 6.2 Saved GPS Points (Pins)

- **Data per point**: name, lat, lng
- **Save**: prompts for name when 📌 is clicked while GPS has a fix
- **Browse**: the 📍 button opens a modal listing all saved locations with Go and Delete actions

---

## 7. Search

### 7.1 Place Search

- **API**: Nominatim (OpenStreetMap)
- **Trigger**: Typing ≥2 characters in the search input (input attributes disable autocorrect/spellcheck for fast typing; Android `captureInput` is off so keystrokes are not delayed)
- **Debounce**: 400 ms delay before fetching
- **Display**: Dropdown of up to 8 suggestions below the input
- **Selection**: Clicking a suggestion **flies the map to that location** and fills the input
- **Enter**: Pressing Enter moves the map to the highlighted/first suggestion (or does a fresh geocode search if the dropdown is closed)
- **Go**: Same behavior as Enter

### 7.2 Coordinate Search

- **Format**: `lat, lng` or `lat lng` (e.g. `13.0827, 80.2707`)
- **Detection**: Regex test on the input value
- **Validation**: lat ∈ [-90, 90], lng ∈ [-180, 180]
- **On Go**: flies map to the parsed coordinates

---

## 8. Screenshot

- **Library**: html2canvas 1.4.1 bundled locally at `vendor/html2canvas.min.js` (no CDN dependency, works offline)
- **Capture**: Full document body at 2× scale; tile layers are created with `crossOrigin='anonymous'` so the canvas is not tainted
- **Output (web/browser)**: Triggers download as `map-{timestamp}.png`
- **Output (Android)**: canvas PNG is written via Capacitor Filesystem to `maparea/screenshots/{timestamp}.png` in the Documents folder, then presented through the Android Share sheet (save to gallery / share)
- **Hint**: Shows "Screenshot saved" for 3 s

---

## 9. Zoom Behavior

- Map zoom range is 2–22
- Both tile layers use `maxNativeZoom: 19`: beyond z19 Leaflet upscales z19 tiles instead of requesting non-existent tiles, so the map never shows white "no data" background at high zoom
- Satellite layer uses `updateWhenIdle: true` to keep panning smooth while upscaling

---

## 10. Units of Measurement — Summary

| Category | Units | Default |
|---|---|---|
| Area | ft², Cent, Acre, m², Are, Hectare, km², yd², mi² | ft² |
| Length / Perimeter | ft, m, km, yd, mi | ft |

---

## 11. CI / Build

| Step | Action |
|---|---|
| Checkout | `actions/checkout@v4` |
| Node | 22, `npm install` |
| Java | 17 (Temurin) |
| Android SDK | Platform 34 |
| Prepare www | Copies `index.html`, `manifest.json`, `sw.js`, and `vendor/*.js` to `www/` |
| Capacitor | Adds Android platform if new, otherwise runs `cap sync` |
| Bump SDK | Python script: bumps SDK versions in `variables.gradle`, injects GPS permissions into `AndroidManifest.xml` |
| Sync | `npx cap sync android` |
| Build | `./gradlew assembleDebug` |
| Artifact | Uploads `app-debug.apk` |

---

## 12. File Structure

```
/
├── index.html                    # Single-page app (all HTML, CSS, JS)
├── capacitor.config.json         # Capacitor config (appId, plugins, permissions)
├── manifest.json                 # PWA manifest
├── sw.js                         # Service worker for offline caching
├── package.json                  # Dependencies including @capacitor/*
├── vendor/
│   ├── capacitor.js              # Capacitor core web runtime
│   ├── filesystem.js             # Filesystem plugin (Document storage, screenshots)
│   ├── share.js                  # Share plugin (Android share sheet for screenshots)
│   └── html2canvas.min.js        # Screenshot renderer (bundled, no CDN)
├── scripts/
│   └── bump_sdk.py              # CI: bumps SDK, injects permissions
└── .github/workflows/
    └── build-apk.yml             # CI pipeline
```
