# New Pre-Made Video Branding Workflow

## What Changed

**BEFORE**: System generated intro/outro slides from scratch using logos and text
**NOW**: System uses your pre-made intro/outro videos and adds title overlay

## New Workflow

1. **You provide**: 
   - `inputs/intro.mp4` - Your custom intro video
   - `inputs/outro.mp4` - Your custom outro video

2. **System generates**:
   - Video title using OpenAI (based on idea + script)
   - Title overlay on top of your intro video

3. **Final result**:
   - `intro_with_title + main_content + outro` concatenated together

## How to Use

### Step 1: Place Your Videos
```
inputs/
├── intro.mp4    ← Your custom intro (any length)
├── outro.mp4    ← Your custom outro (any length)
└── hero.png     ← Character reference image
```

### Step 2: Run Pipeline
The orchestrator will automatically:
- Generate a smart title like "Digital Privacy Essentials"
- Add that title as overlay text on your intro video
- Concatenate everything together

### Step 3: Customize (Optional)
Edit `factory/branding.py` to adjust:
- Title positioning (`title_y = int(height * 0.75)`)
- Font size (`title_font = min(height // 15, width // 20)`)
- Title display timing (`enable='between(t,1,4)'`)

## Benefits

✅ **Full Creative Control**: Use any intro/outro design you want  
✅ **Faster Processing**: No slide generation, just overlay + concatenation  
✅ **Professional Quality**: Your branded videos, AI-generated titles  
✅ **Flexible Timing**: Intro/outro can be any length  
✅ **Easy Updates**: Change intro/outro without code changes  

## File Structure

```
NEW WORKFLOW:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Intro    │    │   Main Content   │    │   Your Outro    │
│   + AI Title    │ +  │   (Generated)    │ +  │   (Your Brand)  │
│   (Your Brand)  │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ↓                       ↓                       ↓
              🎬 FINAL BRANDED VIDEO 🎬
```

## Technical Details

- **Title Overlay**: Uses FFmpeg drawtext filter with fade-in effects
- **Concatenation**: Preserves audio from main content, adds silent audio to intro/outro
- **Cross-Fade**: Smooth 0.5-second transitions between segments
- **Auto-Cleanup**: Temporary files removed after processing

This gives you maximum flexibility while keeping the AI-powered title generation!