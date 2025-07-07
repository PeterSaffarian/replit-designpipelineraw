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
- **Video Generator** - Creates animated videos from static images using provider-agnostic routing
- **Kling Integration** - Handles JWT authentication and direct video extension with Kling AI
- **Runway Integration** - Handles frame extraction and chained segment generation with Runway ML
- **Video Concatenation** - FFmpeg-based utilities for seamless video segment joining
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

## Recent Changes (July 07, 2025)

✓ Added Runway ML integration as alternative to Kling AI
✓ Implemented frame extraction for seamless video segment chaining  
✓ Created video concatenation utilities using FFmpeg
✓ Enhanced scenario configuration with provider selection
✓ Updated video generation pipeline to support both providers
✓ Added artwork quality checker using OpenAI GPT-4o multimodal model
✓ Implemented retry loop with configurable max attempts (default: 3)
✓ Enhanced orchestrator with quality control workflow and detailed logging

→ System now validates artwork quality before proceeding to video generation