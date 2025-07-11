# AI Video Generation Pipeline

## Overview

This is an automated video generation system that creates short informational videos from text ideas. The system takes a concept (like "explain digital privacy"), generates artwork featuring a character, writes a script, creates audio narration, and produces a final video with synchronized audio and visuals.

The pipeline uses multiple AI services: vision models for artwork design and generation, text-to-speech for audio, video generation for animations, and video assembly for final production.

## System Architecture

### Modular Pipeline Design
The system follows a clean separation of concerns with distinct phases:

1. **Creative Studio** - Handles content creation (artwork design, image generation, script writing, scenario production)
2. **Factory** - Manages technical production (audio generation, video generation, final assembly)
3. **Orchestrator** - Coordinates the entire workflow and manages project state

### Service Integration Pattern
The architecture integrates multiple external AI services through dedicated modules:
- **Google Gemini/OpenAI GPT** for text and vision tasks
- **ElevenLabs** for text-to-speech audio generation
- **Kling AI** for video generation from images
- **Sync.so** for final video assembly with audio synchronization

## Key Components

### Creative Studio (`creative_studio/`)
- **Artwork Designer** - Analyzes ideas and reference images to create detailed prompts for image generation
- **Artwork Builder** - Generates artwork using vision models with image generation capabilities
- **Artwork Checker** - Quality control system using OpenAI GPT-4o to evaluate generated artwork and retry if needed
- **Script Writer** - Creates short, spoken-word scripts based on ideas and generated artwork
- **Producer** - Assembles scenario configurations that define video generation parameters
- **Models** - Central abstraction layer for AI model interactions (Gemini/GPT)

### Factory (`factory/`)
- **Audio Generator** - Converts scripts to speech using ElevenLabs TTS
- **Subtitle Generator** - Creates SRT subtitle files from audio using OpenAI Whisper API
- **Subtitle Burner** - Burns styled subtitles into videos using FFmpeg with Netflix-style formatting
- **Video Branding** - Creates animated intro/outro slides with dynamic titles and professional branding
- **Video Generator** - Creates animated videos from static images using provider-agnostic routing
- **Kling Integration** - Handles JWT authentication and direct video extension with Kling AI
- **Runway Integration** - Handles frame extraction and chained segment generation with Runway ML
- **Video Concatenation** - FFmpeg-based utilities for seamless video segment joining
- **Video Watermark** - FFmpeg-based logo overlay system with configurable positioning and transparency
- **Assembly** - Combines raw video with audio using Sync.so for final production

### Storage System
- **Project-based Organization** - Each video generation creates a unique project folder
- **Asset Tracking** - JSON files track project status, assets, and metadata
- **Run Summaries** - Aggregate reports of batch processing results

## Data Flow

1. **Input Processing** - Ideas are read from CSV files or provided directly
2. **Content Creation** - Artwork prompts are designed based on ideas and reference characters
3. **Asset Generation** - Images, scripts, and audio are created in parallel workflows
4. **Scenario Assembly** - Production parameters are configured based on audio duration
5. **Video Production** - Static images are animated and extended to match audio length
6. **Final Assembly** - Video and audio are synchronized and combined
7. **Output Management** - Final videos are saved with comprehensive metadata tracking

## External Dependencies

### AI Services
- **Google Gemini API** - Text generation and vision analysis
- **OpenAI GPT API** - Alternative text and vision model
- **ElevenLabs API** - Text-to-speech audio generation
- **Kling AI API** - Image-to-video generation with extensions
- **Sync.so API** - Video and audio synchronization

### Supporting Services
- **uguu.se** - Temporary file hosting for API uploads
- **Requests** - HTTP client for API communications
- **Mutagen** - Audio file metadata extraction

### Python Libraries
- **google-generativeai** - Google AI model integration
- **openai** - OpenAI API client
- **elevenlabs** - ElevenLabs SDK
- **pandas** - Data processing for idea management
- **jwt** - JWT token generation for Kling authentication

## Deployment Strategy

### Environment Configuration
The system uses environment variables for API key management:
- `GOOGLE_API_KEY` - Google Gemini access
- `OPENAI_API_KEY` - OpenAI GPT access
- `ELEVENLABS_API_KEY` - ElevenLabs TTS access
- `KLING_ACCESS_KEY` / `KLING_SECRET_KEY` - Kling AI authentication
- `RUNWAY_API_KEY` - Runway ML video generation access
- `SYNC_API_KEY` - Sync.so video assembly access

### Project Structure
- `inputs/` - Source materials (hero images, idea lists, templates)
- `storage/` - Generated projects and assets
- `schemas/` - Configuration templates and schemas

### Error Handling
- Graceful degradation when services are unavailable
- Comprehensive logging and status tracking
- Project-level failure recovery and retry mechanisms

## Changelog

- July 07, 2025: Initial setup with Kling AI integration
- July 07, 2025: Added Runway ML support as alternative video provider with frame-extraction chaining method

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 08, 2025)

✓ Added Runway ML integration as alternative to Kling AI
✓ Implemented frame extraction for seamless video segment chaining  
✓ Created video concatenation utilities using FFmpeg
✓ Enhanced scenario configuration with provider selection
✓ Updated video generation pipeline to support both providers
✓ Added artwork quality checker using OpenAI GPT-4o multimodal model
✓ Implemented retry loop with configurable max attempts (default: 3)
✓ Enhanced orchestrator with quality control workflow and detailed logging
✓ Added logo watermarking system with FFmpeg-based overlay functionality
✓ Implemented final branding step preserving original video while creating branded version
✓ Added configurable logo positioning, opacity, and scaling options
✓ Integrated OpenAI Whisper API for automatic subtitle generation from audio
✓ Created professional subtitle burning with Netflix-style formatting using FFmpeg
✓ Enhanced pipeline workflow: Sync → Subtitles → Logo for streamlined production
✓ Added professional intro/outro branding system with dynamic title generation
✓ Implemented OpenAI-powered video title creation with natural language flexibility
✓ Created HD slides with professional typography, proper aspect ratio detection, and logo positioning
✓ Fixed vertical video support (720x1280) to match actual video dimensions using ffprobe
✓ Integrated complete branding sequence: Intro → Main Content → Outro with seamless transitions
✓ Enhanced slides with Liberation Sans fonts, proportional scaling, and safe logo positioning
✓ Implemented automatic video dimension detection for perfect aspect ratio matching
✓ Resolved FFmpeg syntax issues and created clean, reliable branding workflow
✓ Created beautiful animated intro/outro slides with working FFmpeg animations
✓ Added floating logo animations, text slide effects, and gradient backgrounds
✓ Implemented large logos (1/3 screen), proper text sizing, and professional design
✓ Fixed all animation syntax issues and created reliable video_branding_simple.py module
✓ Cleaned up redundant branding files and created single factory/branding.py module
✓ Built proper workflow with add_branding() function and test_branding_workflow.py
✓ Fixed slide design: logo first, then "KiaOra presents", then title on white background
✓ Eliminated complex animations for reliable, clean slide generation
✓ Fixed audio preservation: Final branded video now retains original audio from main video
✓ Added smart text adaptation: Automatic line wrapping and adaptive font sizing prevents overflow
✓ Implemented entrance animations: Logo and text slide in smoothly then remain static
✓ Enhanced title generation: Smart 4-word OpenAI titles with automatic truncation
✓ Corrected entrance animations: Elements start off-screen, animate in, then remain static (no constant motion)
✓ Fixed outro text overflow: Smart text wrapping and adaptive font sizing for perfect slide fit
✓ Resolved FFmpeg syntax issues: Simplified animation expressions prevent parser errors
✓ Fixed concatenation workflow: Proper file existence checking, step-by-step audio addition, and error handling
✓ Enhanced cleanup system: Automatic temporary file removal with detailed logging
✓ Fixed entrance animations: Elements now start OFF-SCREEN and slide INTO view (proper entrance behavior)
✓ Corrected animation logic: Elements begin invisible and animate to final positions where they remain static
✓ Fixed text formatting: Proper FFmpeg line breaks (\\\\n) prevent unwanted \\n characters in video display
✓ Implemented proper off-screen positioning: Logo starts at -200px, text at height+100px for true entrance effects
✓ Updated animation timing: All elements now animate simultaneously within 1-second window (0-1 seconds)
✓ Optimized slide duration: 3-second slides with 1 second animation + 2 seconds static content
✓ Fixed FFmpeg expression syntax: Proper escaping prevents parser errors in animation expressions
✓ Implemented fade-in entrance animations: Elements within each slide fade from transparent to opaque (1 second)
✓ Added cross-fade slide transitions: Smooth 0.5-second fade between intro → main → outro videos
✓ Clarified animation types: Element entrance (within slides) vs slide transitions (between videos)
✓ Enhanced visual experience: Professional fade effects for both element entrance and slide transitions
✓ Fixed FFmpeg syntax issues: Proper alpha expressions for text fade-in and logo overlay fade effects
✓ Resolved logo positioning: Correct overlay placement and sizing with fade-in animations
✓ Separated slide fade from element fade: Static white background with only elements fading in
✓ Fixed logo fade-in animations: Logo now properly fades in from transparent to opaque within first 1 second
✓ Implemented working fade filter: format=yuva420p,fade=in:st=0:d=1:alpha=1 syntax works correctly
✓ Verified fade timing: Logo invisible at 0.4s (fade-in), fully visible at 2.0s (static content)
✓ Completed simultaneous element entrance: All elements (logo + text) fade in during 1-second window

✓ RESOLVED logo visibility issues: Logos now display perfectly in both intro and outro slides
✓ Fixed logo transparency problem: Removed problematic fade filter that was making logos invisible
✓ Confirmed logo positioning: KiaOra Canterbury Academy logo appears correctly in both slides
✓ Text elements working: All text ("KiaOra presents", titles, "Follow us for more") display properly
✓ Clean slide design: Professional white background with proper spacing and typography

✓ Final cleanup: Removed all test files, keeping only one verification test
✓ Logo display confirmed: Logos visible without fade effects (text keeps fade-in animations)
✓ Orchestrator integration: Branding workflow active at Step 11/12 in main pipeline
✓ Production ready: Complete branding system integrated and tested
✓ Added comprehensive font customization system with 8 available fonts
✓ Organized fonts by category: Sans Serif (modern), Serif (elegant), Monospace (technical)
✓ Included style guide for different content types (business, tech, creative, educational)
✓ Updated default font to DejaVu Sans Bold (more reliable than Liberation fonts)
✓ MAJOR ARCHITECTURAL CHANGE: Replaced slide generation with pre-made video workflow
✓ Removed intro/outro slide creation - now uses user-provided intro.mp4 and outro.mp4
✓ Added title overlay function to add generated titles to pre-made intro videos
✓ Simplified branding workflow: intro_with_title + main + outro concatenation
✓ Updated orchestrator to look for intro.mp4/outro.mp4 in inputs directory
✓ Created single test script (test_branding.py) for pre-made video workflow verification
✓ Cleaned up redundant test files - now using one comprehensive test script

✓ Complete 12-step production pipeline with PRE-MADE VIDEO BRANDING, title overlay, seamless concatenation, subtitle burning, and flexible user-controlled intro/outro design
✓ Fixed video dimension mismatch: All videos now scaled to match main video dimensions (720x1280) before concatenation
✓ Optimized transition timing: Reduced fade duration to 0.5s to prevent black screens between segments
✓ Perfected title positioning: Titles now centered within dotted box area (30% from top) with smart text wrapping for longer titles
✓ Enhanced text styling: White uppercase text with black shadow, properly sized and wrapped to fit within box constraints
✓ Fixed text timing: Title now displays for full intro video duration using dynamic duration detection
✓ Enhanced producer with vision capabilities: Now analyzes artwork to create contextually accurate animation prompts
✓ Complete vision integration: Both script writer and producer use GPT-4o vision to analyze artwork for consistent output
✓ Fixed Runway video concatenation bug: Corrected KeyError 'video_path' by using proper 'path' key in segments structure
✓ Production-ready branding workflow: Seamless intro → main → outro with proper scaling, positioning, and timing