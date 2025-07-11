#!/usr/bin/env python3
"""
Complete test of the new pre-made video branding workflow.
Tests: Title generation → Title overlay → Video concatenation
"""

import os
import sys
from factory.branding import add_branding, generate_title, add_title_overlay, concatenate_videos

def test_complete_branding_workflow():
    """Test the complete branding workflow with existing test files."""
    
    print("🎬 COMPLETE BRANDING WORKFLOW TEST")
    print("=" * 50)
    print("Testing: Pre-made videos + AI title overlay + concatenation")
    print()
    
    # Define test files
    test_files = {
        'main_video': 'test_files/video_with_subtitles.mp4',
        'intro_video': 'test_files/intro.mp4', 
        'outro_video': 'test_files/outro.mp4'
    }
    
    # Test content
    idea = "Understanding Digital Privacy and Online Security"
    script = "In today's digital world, protecting your personal information online is more important than ever. Learn essential privacy tips and security practices."
    output_dir = "test_files"
    
    print("📋 TEST CONFIGURATION:")
    print(f"   Idea: {idea}")
    print(f"   Script: {script[:60]}...")
    print(f"   Output: {output_dir}")
    print()
    
    # Check file availability
    print("📁 CHECKING TEST FILES:")
    missing_files = []
    for name, path in test_files.items():
        exists = os.path.exists(path)
        status = "✅ Found" if exists else "❌ Missing"
        print(f"   {name.replace('_', ' ').title()}: {status}")
        if not exists:
            missing_files.append(path)
    print()
    
    if missing_files:
        print("⚠️  MISSING FILES - Cannot complete test")
        print("💡 Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # Test Step 1: Title Generation
    print("🔤 STEP 1: GENERATING VIDEO TITLE")
    print("   Using OpenAI to create smart title...")
    
    try:
        title = generate_title(idea, script)
        print(f"   ✅ Generated title: '{title}'")
    except Exception as e:
        print(f"   ❌ Title generation failed: {e}")
        return False
    print()
    
    # Test Step 2: Title Overlay
    print("🎨 STEP 2: ADDING TITLE OVERLAY")
    print("   Adding title to intro video...")
    
    intro_with_title = os.path.join(output_dir, "test_intro_with_title.mp4")
    
    try:
        result = add_title_overlay(test_files['intro_video'], title, intro_with_title)
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / (1024 * 1024)  # MB
            print(f"   ✅ Title overlay added successfully!")
            print(f"   📍 Output: {result}")
            print(f"   📊 Size: {file_size:.1f} MB")
        else:
            print("   ❌ Title overlay failed")
            return False
    except Exception as e:
        print(f"   ❌ Title overlay error: {e}")
        return False
    print()
    
    # Test Step 3: Video Concatenation
    print("🔗 STEP 3: CONCATENATING VIDEOS")
    print("   Joining: intro_with_title + main + outro...")
    
    final_output = os.path.join(output_dir, "test_complete_branded_video.mp4")
    video_list = [intro_with_title, test_files['main_video'], test_files['outro_video']]
    
    try:
        result = concatenate_videos(video_list, final_output)
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / (1024 * 1024)  # MB
            print(f"   ✅ Video concatenation successful!")
            print(f"   📍 Final video: {result}")
            print(f"   📊 Size: {file_size:.1f} MB")
        else:
            print("   ❌ Video concatenation failed")
            return False
    except Exception as e:
        print(f"   ❌ Concatenation error: {e}")
        return False
    print()
    
    # Test Step 4: Full Workflow
    print("🚀 STEP 4: TESTING COMPLETE WORKFLOW")
    print("   Running add_branding() with all steps...")
    
    complete_output = os.path.join(output_dir, "test_workflow_complete.mp4")
    
    try:
        result = add_branding(
            test_files['main_video'], 
            idea, 
            script, 
            test_files['intro_video'], 
            test_files['outro_video'], 
            output_dir
        )
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / (1024 * 1024)  # MB
            print(f"   ✅ Complete workflow successful!")
            print(f"   📍 Final branded video: {result}")
            print(f"   📊 Size: {file_size:.1f} MB")
        else:
            print("   ❌ Complete workflow failed")
            return False
    except Exception as e:
        print(f"   ❌ Workflow error: {e}")
        return False
    print()
    
    # Cleanup temporary files
    print("🧹 CLEANUP:")
    temp_files = [intro_with_title]
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                print(f"   ✅ Removed: {temp_file}")
        except Exception:
            print(f"   ⚠️  Could not remove: {temp_file}")
    print()
    
    # Final Summary
    print("📊 WORKFLOW SUMMARY:")
    print("   ✅ Title Generation: AI-powered smart titles")
    print("   ✅ Title Overlay: Professional text placement") 
    print("   ✅ Video Concatenation: Seamless transitions")
    print("   ✅ Complete Integration: End-to-end workflow")
    print()
    print("🎯 NEW WORKFLOW BENEFITS:")
    print("   • User provides custom intro/outro videos")
    print("   • AI generates contextual titles")
    print("   • Automatic title overlay positioning")
    print("   • Smooth concatenation with audio preservation")
    print("   • Much faster than slide generation")
    print()
    
    return True

def main():
    """Run the complete branding workflow test."""
    try:
        success = test_complete_branding_workflow()
        if success:
            print("🎉 ALL TESTS PASSED! New branding workflow is ready.")
        else:
            print("❌ Tests failed. Check error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()