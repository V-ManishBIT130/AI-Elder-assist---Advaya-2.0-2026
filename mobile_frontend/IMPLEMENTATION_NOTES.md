# React Native Conversion Notes (mobile_frontend)

## 1) Purpose
Create a new folder named `mobile_frontend` and convert the 3 provided HTML screens into React Native screen equivalents:
- Home dashboard
- Medications
- Emergency

The conversion preserves the same UI sections and interaction intent:
- Top app bar
- Main content cards and sections
- Floating voice button
- Bottom tab navigation

## 2) Source to Target Mapping
### Home Dashboard
Source HTML area mapped to React Native:
- `header` -> top `View` row with greeting + profile `Image`
- `section` movement card -> `View` card + icon tile + gauge block
- daily reminder card list -> stacked `View` cards with icon + text + trailing icon
- mood check tiles -> 3 `Pressable` blocks with icon + label
- floating voice button -> absolute positioned `Pressable`
- bottom nav `nav` -> fixed bottom `View` with 3 tab `Pressable` items

### Medications
Source HTML area mapped to React Native:
- sticky top bar -> top `View` with title/subtitle + profile `Image`
- warning banner -> highlighted `View` with warning icon and explanatory text
- 3 medication cards -> card `View` blocks with:
  - schedule time + medication name
  - status badge (`Taken`, `Due Now`, `Upcoming`)
  - supply status row + progress bar
  - action button state (disabled for taken)
- floating mic area -> absolute `Pressable`
- bottom nav -> fixed tab bar with active Medications state

### Emergency
Source HTML area mapped to React Native:
- top app bar -> profile image + title + subtitle + settings icon button
- emergency contacts grid/list -> cards with initials bubble, name, role, call button
- main emergency action -> large circular CTA hierarchy (`I NEED HELP`)
- cancel action -> secondary `Pressable`
- reassurance line and pulse dots -> text + indicator dots
- floating mic area -> absolute `Pressable` + label
- bottom nav -> fixed tab bar with active Emergency state

## 3) Project Structure Created
- `mobile_frontend/App.tsx`
- `mobile_frontend/src/theme/colors.ts`
- `mobile_frontend/src/types.ts`
- `mobile_frontend/src/screens/HomeDashboardRajScreen.tsx`
- `mobile_frontend/src/screens/MedicationsRajScreen.tsx`
- `mobile_frontend/src/screens/EmergencyRajScreen.tsx`
- `mobile_frontend/README.md`

## 4) Core Concepts Used
- `SafeAreaView` + `ScrollView` for mobile-safe layout and vertical content flow
- `Pressable` for all tappable controls (buttons, tabs, CTAs)
- absolute positioning for floating mic and bottom nav behavior
- shared color tokens in `src/theme/colors.ts` for consistency
- shared tab type and navigation props in `src/types.ts`

## 5) Command Requirements
Install icon dependency in your React Native app:

```bash
npm install react-native-vector-icons
```

If you are using Expo, switch icon imports to `@expo/vector-icons`.

## 6) Verification Performed
- Confirmed all new files are present under `mobile_frontend`
- Ran editor diagnostics on screen files
- Reported errors are dependency-environment related (`react`, `react-native`, icon package types not available in this standalone folder), not syntax errors in the converted code

## 7) Notes and Assumptions
- This folder contains frontend conversion code and screen mappings, not a fully bootstrapped RN app initialization (no package.json / android / ios generated here)
- The three screens are integrated via tab state in `App.tsx` so you can switch between them immediately once placed in a RN project

## 8) Suggested Next Step
If you want, the next step is to scaffold a full React Native app around this folder structure and wire these files as the default screens so you can run directly with `npm run android` / `npm run ios`.
