#!/usr/bin/env python3
"""
Example script showing how to customize fonts and sizes in the branding system.

This demonstrates different ways to modify the appearance of intro/outro slides.
"""

from factory.branding import BRANDING_CONFIG, LAYOUT_CONFIG, create_intro_slide, create_outro_slide

def show_current_settings():
    """Display current branding configuration."""
    print("=== CURRENT BRANDING SETTINGS ===")
    print("\n📝 FONTS:")
    for name, path in BRANDING_CONFIG['fonts'].items():
        print(f"  {name}: {path}")
    
    print("\n📏 SIZE RATIOS:")
    for name, ratio in BRANDING_CONFIG['size_ratios'].items():
        print(f"  {name}: {ratio}")
    
    print("\n🎨 COLORS:")
    for name, color in BRANDING_CONFIG['colors'].items():
        print(f"  {name}: {color}")
    
    print("\n📍 LAYOUT:")
    for name, ratio in LAYOUT_CONFIG.items():
        print(f"  {name}: {ratio}")

def example_size_calculations():
    """Show how different ratios affect font sizes."""
    print("\n=== SIZE EXAMPLES ===")
    
    # Example for 720x1280 vertical video
    width, height = 720, 1280
    print(f"\nFor {width}x{height} video:")
    
    logo_size = min(width, height) // BRANDING_CONFIG['size_ratios']['logo_ratio']
    title_font = min(height // BRANDING_CONFIG['size_ratios']['title_height_ratio'], 
                     width // BRANDING_CONFIG['size_ratios']['title_width_ratio'])
    presents_font = height // BRANDING_CONFIG['size_ratios']['presents_ratio']
    outro_font = height // BRANDING_CONFIG['size_ratios']['outro_text_ratio']
    
    print(f"  Logo size: {logo_size}px")
    print(f"  Title font: {title_font}px")
    print(f"  'KiaOra presents' font: {presents_font}px")
    print(f"  Outro text font: {outro_font}px")

def customize_example():
    """Example of how to customize settings."""
    print("\n=== CUSTOMIZATION EXAMPLES ===")
    
    print("\n1. TO MAKE FONTS LARGER:")
    print("   - Decrease the ratio numbers (smaller number = larger text)")
    print("   - BRANDING_CONFIG['size_ratios']['title_height_ratio'] = 12  # Was 15")
    print("   - BRANDING_CONFIG['size_ratios']['presents_ratio'] = 15      # Was 20")
    
    print("\n2. TO USE DIFFERENT FONTS:")
    print("   - Change the font paths in BRANDING_CONFIG['fonts']")
    print("   - Available fonts: DejaVu, Ubuntu, Liberation")
    print("   - BRANDING_CONFIG['fonts']['primary'] = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'")
    
    print("\n3. TO CHANGE COLORS:")
    print("   - BRANDING_CONFIG['colors']['text'] = 'white'")
    print("   - BRANDING_CONFIG['colors']['background'] = 'black'")
    
    print("\n4. TO ADJUST POSITIONING:")
    print("   - LAYOUT_CONFIG['logo_y_ratio'] = 4     # Logo higher (was 6)")
    print("   - LAYOUT_CONFIG['title_y_ratio'] = 0.8  # Title lower (was 0.75)")

def test_custom_branding():
    """Test with custom settings."""
    print("\n=== TESTING CUSTOM SETTINGS ===")
    
    # Temporarily modify settings for demo
    original_title_ratio = BRANDING_CONFIG['size_ratios']['title_height_ratio']
    original_text_color = BRANDING_CONFIG['colors']['text']
    
    try:
        # Make title font larger and text blue
        BRANDING_CONFIG['size_ratios']['title_height_ratio'] = 12  # Larger font
        BRANDING_CONFIG['colors']['text'] = 'blue'  # Blue text
        
        print("Creating test slide with larger blue text...")
        result = create_intro_slide(
            'Custom Test', 
            'test_files/logo.png', 
            'test_files/custom_branding_test.mp4', 
            720, 1280
        )
        
        if result:
            print(f"✅ Custom branding test created: {result}")
        else:
            print("❌ Custom branding test failed")
            
    finally:
        # Restore original settings
        BRANDING_CONFIG['size_ratios']['title_height_ratio'] = original_title_ratio
        BRANDING_CONFIG['colors']['text'] = original_text_color

if __name__ == "__main__":
    show_current_settings()
    example_size_calculations()
    customize_example()
    test_custom_branding()
    
    print("\n💡 TO APPLY CHANGES:")
    print("   Edit the BRANDING_CONFIG and LAYOUT_CONFIG dictionaries")
    print("   at the top of factory/branding.py")