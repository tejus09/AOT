from typing import Dict, List, Optional
from config import (VEHICLE_BRANDS, VEHICLE_COLORS, VEHICLE_ORIENTATIONS,
                   VEHICLE_LABELS, VEHICLE_ITYPES, VEHICLE_TYPES, VEHICLE_SPECIAL_TYPES)

def validate_attribute(attribute: str, value: str) -> bool:
    """Validate if an attribute value is in the allowed list"""
    if attribute == "brand_name":
        return value in VEHICLE_BRANDS
    elif attribute == "vehicle_color":
        return value in VEHICLE_COLORS
    elif attribute == "orientation":
        return value in VEHICLE_ORIENTATIONS
    elif attribute == "label":
        return value in VEHICLE_LABELS
    elif attribute == "itype":
        return value in VEHICLE_ITYPES
    elif attribute == "type":
        return value in VEHICLE_TYPES
    elif attribute == "special_type":
        return value in VEHICLE_SPECIAL_TYPES
    # For attributes like width, height, etc. return True
    return True

def get_attribute_options(attribute: str) -> List[str]:
    """Get all options for a specific attribute"""
    if attribute == "brand_name":
        return VEHICLE_BRANDS
    elif attribute == "vehicle_color":
        return VEHICLE_COLORS
    elif attribute == "orientation":
        return VEHICLE_ORIENTATIONS
    elif attribute == "label":
        return VEHICLE_LABELS
    elif attribute == "itype":
        return VEHICLE_ITYPES
    elif attribute == "type":
        return VEHICLE_TYPES
    elif attribute == "special_type":
        return VEHICLE_SPECIAL_TYPES
    return []

def validate_json_structure(data: Dict) -> List[str]:
    """Validate the entire JSON structure, return a list of issues"""
    issues = []
    
    # Check for required fields
    required_fields = ["img_name", "width", "height"]
    for field in required_fields:
        if field not in data:
            issues.append(f"Missing required field: {field}")
    
    # Validate attribute values if they exist
    for attr in ["brand_name", "vehicle_color", "orientation", "label", "itype", "type"]:
        if attr in data and not validate_attribute(attr, data[attr]):
            issues.append(f"Invalid value for {attr}: {data[attr]}")
    
    return issues

def suggest_fixes(data: Dict) -> Dict[str, str]:
    """Suggest fixes for common issues in the data"""
    suggestions = {}
    
    # Check for brand name variations and suggest standardized versions
    if "brand_name" in data:
        brand = data["brand_name"]
        # Handle common misspellings or variations
        if brand == "Maruthi":
            suggestions["brand_name"] = "Maruti-Suzuki"
        elif brand == "Tata":
            suggestions["brand_name"] = "Tata-Motors"
        elif brand == "Hero Honda":
            suggestions["brand_name"] = "Hero-Honda"
    
    # For color variations
    if "vehicle_color" in data:
        color = data["vehicle_color"]
        if color == "Grey":
            suggestions["vehicle_color"] = "Gray"
        elif color == "Golden":
            suggestions["vehicle_color"] = "Yellow"
    
    return suggestions 