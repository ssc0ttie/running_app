def get_member_avatar_advanced(member_name):
    """Generate advanced avatar with gradients and patterns"""

    # Create deterministic hash from member name
    hash_val = sum(ord(c) for c in member_name)

    # Predefined gradient pairs
    gradients = [
        ("#FF512F", "#DD2476"),  # Sunset
        ("#FF6B6B", "#4ECDC4"),  # Coral to Mint
        ("#45B7D1", "#96CEB4"),  # Blue to Green
        ("#F7D794", "#F8A5C2"),  # Yellow to Pink
        ("#9B5DE5", "#F15BB5"),  # Purple to Pink
        ("#00B4DB", "#0083B0"),  # Ocean
        ("#FC4C02", "#FF8C42"),  # Orange gradient
        ("#11998E", "#38EF7D"),  # Green gradient
    ]

    # Select gradient based on member name
    gradient_index = hash_val % len(gradients)
    color1, color2 = gradients[gradient_index]

    """Simple avatar configuration for specific members"""

    avatar_map = {
        "Aiza": {"emoji": "🏃‍♀️", "color1": "#FF6B6B", "color2": "#EE5A24"},
        "Chona": {"emoji": "🌟", "color1": "#F9CA24", "color2": "#F0932B"},
        "Fraulein": {"emoji": "🦋", "color1": "#C39BD3", "color2": "#8E44AD"},
        "Lead": {"emoji": "👑", "color1": "#F1C40F", "color2": "#D4AC0D"},
        "Maxine": {"emoji": "🏃‍♂️", "color1": "#3498DB", "color2": "#2980B9"},
        "Scott": {"emoji": "⚡", "color1": "#2ECC71", "color2": "#27AE60"},
    }

    if member_name in avatar_map:
        return avatar_map[member_name]

    # Default for other members
    return {"emoji": "🏃", "color1": "#95A5A6", "color2": "#7F8C8D"}
