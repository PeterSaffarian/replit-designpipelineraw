#!/usr/bin/env python3
"""
Demo: Exact workflow as requested
Process: Generate title → Drop title on intro → Attach all videos → Output
"""

import os
from factory.branding import generate_title, add_title_overlay, concatenate_videos

def demo_exact_workflow():
    """Demonstrate the exact process requested by user."""
    
    print("🎬 BRANDING WORKFLOW DEMO")
    print("=" * 30)
    print("Process: Generate title → Drop on intro → Attach videos → Output")
    print()
    
    # Setup
    idea = "Digital Privacy and Security Best Practices"
    script = "Learn essential techniques to protect your personal data online and stay safe from cyber threats."
    
    intro_video = "test_files/intro.mp4"
    main_video = "test_files/video_with_subtitles.mp4" 
    outro_video = "test_files/outro.mp4"
    output_dir = "test_files"
    
    print(f"📝 Content: {idea}")
    print(f"🎥 Files: intro.mp4 + main video + outro.mp4")
    print()
    
    # Step 1: Generate video title
    print("STEP 1: Generate Video Title")
    print("→ Using OpenAI to create smart title...")
    
    title = generate_title(idea, script)
    print(f"✅ Generated: '{title}'")
    print()
    
    # Step 2: Drop title on intro slide  
    print("STEP 2: Drop Title on Intro Video")
    print("→ Adding title overlay to intro video...")
    
    intro_with_title = os.path.join(output_dir, "demo_intro_with_title.mp4")
    overlay_result = add_title_overlay(intro_video, title, intro_with_title)
    
    if overlay_result:
        print(f"✅ Title dropped on intro: {overlay_result}")
    else:
        print("❌ Failed to add title overlay")
        return
    print()
    
    # Step 3: Attach all videos together
    print("STEP 3: Attach All Videos Together")
    print("→ Concatenating: intro_with_title + main + outro...")
    
    final_output = os.path.join(output_dir, "demo_final_branded_video.mp4")
    video_list = [intro_with_title, main_video, outro_video]
    
    print("   Processing video concatenation...")
    concat_result = concatenate_videos(video_list, final_output)
    
    if concat_result:
        file_size = os.path.getsize(concat_result) / (1024 * 1024)  # MB
        print(f"✅ Videos attached successfully!")
        print(f"📍 Final output: {concat_result}")
        print(f"📊 Size: {file_size:.1f} MB")
    else:
        print("❌ Failed to concatenate videos")
        return
    print()
    
    # Step 4: Output summary
    print("STEP 4: Output Complete")
    print("🎯 WORKFLOW COMPLETED SUCCESSFULLY!")
    print()
    print("📋 Process Summary:")
    print(f"   1. ✅ Generated title: '{title}'")
    print(f"   2. ✅ Added title to intro video")
    print(f"   3. ✅ Concatenated all videos with transitions")
    print(f"   4. ✅ Output: {os.path.basename(final_output)}")
    print()
    
    # Cleanup temporary intro file
    try:
        if os.path.exists(intro_with_title):
            os.unlink(intro_with_title)
            print("🧹 Cleaned up temporary files")
    except:
        pass
    
    print("🎉 Demo complete! New branding workflow is working perfectly.")

if __name__ == "__main__":
    demo_exact_workflow()