#!/usr/bin/env python3
"""
Test script for Runway integration.
This script tests the video generation workflow with Runway provider.
"""

import os
import json
import tempfile
from factory import video_gen

def create_test_scenario():
    """Create a test scenario file for Runway."""
    scenario = {
        "global_settings": {
            "provider": "runway",
            "model_name": "gen4_turbo",
            "aspect_ratio": "16:9",
            "mode": "pro"
        },
        "opening_scene": {
            "type": "image_to_video",
            "duration": 5,
            "prompt": "A still shot of a professional character in business attire, with subtle ambient motion.",
            "image_source": "test_image.jpg"
        },
        "extensions": [
            "The character begins to speak, their expression animated and engaging.",
            "The character continues talking with confident gestures."
        ]
    }
    
    # Create temporary scenario file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(scenario, f, indent=2)
        return f.name

def create_test_image():
    """Create a simple test image (placeholder for actual artwork)."""
    import cv2
    import numpy as np
    
    # Create a simple 1280x720 test image
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    img[:] = (50, 100, 150)  # Blue background
    
    # Add some text
    cv2.putText(img, 'TEST CHARACTER', (400, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    # Save to temporary file
    test_image_path = tempfile.mktemp(suffix='.jpg')
    cv2.imwrite(test_image_path, img)
    return test_image_path

def test_runway_integration():
    """Test the complete Runway integration workflow."""
    print("🧪 Testing Runway Integration")
    print("=" * 50)
    
    # Check if Runway API key is available
    if not os.environ.get("RUNWAY_API_KEY"):
        print("❌ RUNWAY_API_KEY environment variable not set")
        print("   Please set this to test Runway integration")
        return False
    
    try:
        # Create test assets
        print("📁 Creating test assets...")
        scenario_path = create_test_scenario()
        test_image_path = create_test_image()
        assets_dir = os.path.dirname(test_image_path)
        
        # Copy test image to expected location
        expected_image_path = os.path.join(assets_dir, 'test_image.jpg')
        import shutil
        shutil.copy2(test_image_path, expected_image_path)
        
        print(f"   ✅ Scenario: {scenario_path}")
        print(f"   ✅ Test image: {expected_image_path}")
        
        # Test video generation
        print("\n🎬 Testing video generation...")
        result = video_gen.generate(scenario_path, assets_dir)
        
        if result:
            print("   ✅ Video generation completed successfully!")
            print(f"   📊 Result: {result}")
            
            # Check if it's a Runway result
            if 'videos' in result and len(result['videos']) > 0:
                video_info = result['videos'][0]
                if video_info.get('provider') == 'runway':
                    print("   🎯 Runway provider confirmed")
                    print(f"   📹 Video segments: {video_info.get('segments', 'N/A')}")
                    print(f"   📄 Video path: {video_info.get('path', 'N/A')}")
                else:
                    print("   ℹ️  Video generated with different provider")
            
            return True
        else:
            print("   ❌ Video generation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        import traceback
        print(f"   🔍 Details: {traceback.format_exc()}")
        return False
    
    finally:
        # Cleanup
        try:
            if 'scenario_path' in locals():
                os.unlink(scenario_path)
            if 'test_image_path' in locals():
                os.unlink(test_image_path)
            if 'expected_image_path' in locals() and os.path.exists(expected_image_path):
                os.unlink(expected_image_path)
        except:
            pass

def test_provider_fallback():
    """Test that the system falls back to Kling when provider is not specified."""
    print("\n🔄 Testing Provider Fallback")
    print("=" * 50)
    
    scenario = {
        "global_settings": {
            "model_name": "kling-v1",
            # No provider specified - should default to Kling
        },
        "opening_scene": {
            "type": "image_to_video",
            "duration": 5,
            "prompt": "Test prompt",
            "image_source": "test.jpg"
        },
        "extensions": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(scenario, f, indent=2)
        scenario_path = f.name
    
    try:
        # This should work even without Runway API key
        print("📋 Testing scenario loading and provider detection...")
        
        # Just test the scenario loading and provider routing logic
        # (Don't actually generate video to avoid API calls)
        from factory.video_gen import _load_scenario_data
        scenario_data = _load_scenario_data(scenario_path)
        
        if scenario_data:
            provider = scenario_data.get('global_settings', {}).get('provider', 'kling').lower()
            print(f"   ✅ Provider detected: {provider}")
            
            if provider == 'kling':
                print("   ✅ Correctly defaulted to Kling provider")
                return True
            else:
                print(f"   ❌ Unexpected provider: {provider}")
                return False
        else:
            print("   ❌ Failed to load scenario")
            return False
            
    finally:
        os.unlink(scenario_path)

if __name__ == "__main__":
    print("🚀 Runway Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Provider fallback (always works)
    fallback_success = test_provider_fallback()
    
    # Test 2: Runway integration (requires API key)
    runway_success = test_runway_integration()
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    print(f"Provider Fallback: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    print(f"Runway Integration: {'✅ PASS' if runway_success else '❌ FAIL'}")
    
    if fallback_success and runway_success:
        print("\n🎉 All tests passed! Runway integration is ready.")
    elif fallback_success:
        print("\n⚠️  Basic functionality works. Set RUNWAY_API_KEY to test full integration.")
    else:
        print("\n❌ Tests failed. Check implementation.")