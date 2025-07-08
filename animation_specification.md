# Animation Specification

## Two Distinct Animation Types

### 1. Element Entrance Animations (Within Each Slide)
**Purpose:** How elements appear when a slide starts
**Duration:** 1 second at the beginning of each slide
**Effect:** Fade-in from transparent to opaque
**Elements Affected:**
- Logo
- "KiaOra presents" text
- AI-generated title
- "Follow us for more" text

**Timeline within each slide:**
- 0.0-1.0s: All elements fade in simultaneously
- 1.0-3.0s: All elements remain static at full opacity

### 2. Slide Transition Effects (Between Videos)
**Purpose:** How one video transitions to the next
**Duration:** 0.5 seconds between videos
**Effect:** Cross-fade (overlap fade-out/fade-in)
**Videos Affected:**
- Intro slide → Main video
- Main video → Outro slide

**Timeline between videos:**
- Last 0.5s of Video A: Fade out
- First 0.5s of Video B: Fade in
- Overlap creates smooth cross-fade transition

## Implementation Summary

**Intro Slide:**
1. Elements fade in during first 1 second
2. 2 seconds of static content
3. Cross-fade transition to main video

**Main Video:**
1. Fade in from intro (cross-fade)
2. Play original content
3. Cross-fade transition to outro

**Outro Slide:**
1. Fade in from main video (cross-fade)
2. Elements fade in during first 1 second
3. 2 seconds of static content

## Technical Notes

- Element fade-ins use `fade=in:st=0:d=1` on individual elements
- Cross-fade transitions use `fade=out` and `fade=in` with temporal overlap
- Audio is preserved throughout all transitions
- Total branded video: Intro (3s) + Main (variable) + Outro (3s) with smooth transitions