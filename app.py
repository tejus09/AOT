import os
import gradio as gr
import json
from PIL import Image
from typing import Dict, List, Tuple, Optional
import pandas as pd
import difflib  # Add difflib for string similarity matching

from data_handler import (get_all_samples, get_image_path, load_json_data, 
                         save_json_data, mark_as_verified, get_verification_stats,
                         load_progress, export_dataset_stats, save_progress)
from validation import (get_attribute_options, validate_json_structure, 
                       suggest_fixes, validate_attribute)
from utils import generate_report, get_timestamp
from config import OUTPUT_DIR, VEHICLE_BRANDS, VEHICLE_COLORS, VEHICLE_ORIENTATIONS, VEHICLE_LABELS, VEHICLE_ITYPES, VEHICLE_TYPES, VEHICLE_SPECIAL_TYPES

# Global state variables
current_sample_index = 0
samples = get_all_samples()
current_data = {}
modified = False
issues = []
verified_status = False

# Add global variable to store previous state
previous_data = {}

def load_current_sample() -> Tuple[Optional[Image.Image], Dict, str]:
    """Load the current sample (image and JSON)"""
    global current_data, issues, modified, verified_status
    
    if not samples or current_sample_index < 0 or current_sample_index >= len(samples):
        # Empty the current data
        current_data = {}
        issues = []
        modified = False
        verified_status = False
        return None, {}, "No samples found"
    
    try:
        json_path = samples[current_sample_index]
        image_path = get_image_path(json_path)
        
        # Check if verified
        progress = load_progress()
        verified_status = json_path in progress["verified"]
        
        # If verified, check if there's a verified version in the output directory
        if verified_status:
            base_name = os.path.basename(json_path)
            verified_path = os.path.join(OUTPUT_DIR, base_name)
            
            # Load from verified path if it exists, otherwise from original
            if os.path.exists(verified_path):
                current_data = load_json_data(verified_path)
            else:
                current_data = load_json_data(json_path)
        else:
            # Load data from original path
            current_data = load_json_data(json_path)
        
        # Set default values for all attributes if they don't exist
        attribute_defaults = {
            "label": "None of the above",
            "orientation": "None of the above",
            "brand_name": "None of the above",
            "vehicle_color": "None of the above",
            "itype": "None of the above",
            "type": "None of the above",
            "special_type": "None of the above"
        }
        
        # Apply defaults for missing attributes
        for attr, default_value in attribute_defaults.items():
            if attr not in current_data:
                current_data[attr] = default_value
                modified = True  # Mark as modified since we added defaults
            
        issues = validate_json_structure(current_data)
        
        # Load image if exists
        if os.path.exists(image_path):
            image = Image.open(image_path)
            return image, current_data, f"Sample {current_sample_index + 1}/{len(samples)}: {os.path.basename(json_path)}"
        else:
            return None, current_data, f"Image not found for {os.path.basename(json_path)}"
    except Exception as e:
        return None, {}, f"Error loading sample: {str(e)}"

def update_interface() -> List:
    """Update the Gradio interface with current sample data"""
    global current_data, issues, verified_status
    
    # Check if we have valid samples
    if not samples or current_sample_index < 0 or current_sample_index >= len(samples):
        # No samples or invalid index
        image = None
        label = None
        orientation = None
        brand_name = None
        vehicle_color = None
        itype = None
        vehicle_type = None
        special_type = None
        issues_text = ""
        
        # Generate a basic summary with just the statistics
        stats = get_verification_stats()
        summary = f"No samples in current view\n"
        summary += f"Overall Progress: {stats['verified']}/{stats['total']} ({stats['progress_percentage']:.2f}%)"
        
        current_attrs_text = ""
        
        # Return empty UI state
        return [
            image, 
            summary,
            label, 
            orientation,
            brand_name,
            vehicle_color,
            itype,
            vehicle_type,
            special_type,
            issues_text,
            verified_status,
            current_attrs_text
        ]
    
    # If we have valid samples and current_data is empty, load the sample
    if not current_data:
        image, data, status = load_current_sample()
    else:
        # Use existing data and just load the image
        json_path = samples[current_sample_index]
        image_path = get_image_path(json_path)
        
        # Load image if exists
        if os.path.exists(image_path):
            image = Image.open(image_path)
        else:
            image = None
        
        data = current_data
        status = f"Sample {current_sample_index + 1}/{len(samples)}: {os.path.basename(json_path)}"
    
    # Ensure all attributes have default values
    attribute_defaults = {
        "label": "None of the above",
        "orientation": "None of the above",
        "brand_name": "None of the above",
        "vehicle_color": "None of the above",
        "itype": "None of the above",
        "type": "None of the above",
        "special_type": "None of the above"
    }
    
    # Apply defaults for missing attributes in current_data
    for attr, default_value in attribute_defaults.items():
        if attr not in current_data:
            current_data[attr] = default_value
    
    # Extract attribute values from current_data (with defaults applied)
    label = current_data.get("label")
    orientation = current_data.get("orientation")
    brand_name = current_data.get("brand_name")
    vehicle_color = current_data.get("vehicle_color")
    itype = current_data.get("itype")
    vehicle_type = current_data.get("type")
    special_type = current_data.get("special_type")
    
    # Update issue list
    issues_text = "\n".join(issues) if issues else "No issues detected"
    
    # Check verification status
    verification_status = "✅ Verified" if verified_status else "⏳ Pending"
    
    # Generate summary with sample information
    summary = f"Sample {current_sample_index + 1}/{len(samples)}: {os.path.basename(samples[current_sample_index])}\n"
    summary += f"Status: {verification_status}\n"
    
    # Statistics
    stats = get_verification_stats()
    summary += f"Overall Progress: {stats['verified']}/{stats['total']} ({stats['progress_percentage']:.2f}%)"
    
    # Format current attributes
    attr_list = []
    for key, value in current_data.items():
        if key not in ["img_name", "width", "height"]:  # Skip metadata
            attr_list.append(f"{key}: {value}")
    
    current_attrs_text = "\n".join(attr_list) if attr_list else "No attributes"
    
    # Return all the UI elements that need to be updated
    return [
        image, 
        summary,
        label, 
        orientation,
        brand_name,
        vehicle_color,
        itype,
        vehicle_type,
        special_type,
        issues_text,
        verified_status,
        current_attrs_text
    ]

def update_with_status(additional_msg: str = "") -> List:
    """Update the interface and ensure status text is correctly displayed
    
    This wrapper ensures the status is properly updated when navigating samples
    and adds any additional messages.
    
    Args:
        additional_msg: Optional additional message to include in the status
    
    Returns:
        List: Updated UI elements
    """
    # Get the base interface update
    result = update_interface()
    
    # Get the current status text
    status = result[1]
    
    # Add the additional message if provided
    if additional_msg:
        status += f"\n\n{additional_msg}"
    
    # Replace status text in the result
    result[1] = status
    
    return result

def next_sample() -> List:
    """Move to the next sample"""
    global current_sample_index, current_data, modified, issues
    
    # Save current changes if needed
    if modified and samples and 0 <= current_sample_index < len(samples):
        save_changes()
    
    # Clear current data to force reloading from file
    current_data = {}
    modified = False
    issues = []
    
    if current_sample_index < len(samples) - 1:
        current_sample_index += 1
    
    return update_with_status()

def prev_sample() -> List:
    """Move to the previous sample"""
    global current_sample_index, current_data, modified, issues
    
    # Save current changes if needed
    if modified and samples and 0 <= current_sample_index < len(samples):
        save_changes()
    
    # Clear current data to force reloading from file
    current_data = {}
    modified = False
    issues = []
    
    if current_sample_index > 0:
        current_sample_index -= 1
    
    return update_with_status()

def jump_to_sample(index: int) -> List:
    """Jump to a specific sample by index"""
    global current_sample_index, current_data, modified, issues
    
    # Save current changes if needed
    if modified and samples and 0 <= current_sample_index < len(samples):
        save_changes()
    
    # Clear current data to force reloading from file
    current_data = {}
    modified = False
    issues = []
    
    if not samples:
        # No samples available
        current_sample_index = -1
        return update_with_status("No samples available to navigate to.")
    
    if 0 <= index < len(samples):
        current_sample_index = index
        return update_with_status()
    else:
        # Invalid index provided
        return update_with_status(f"Invalid sample number. Please enter a value between 1 and {len(samples)}.")

def get_similar_values(attr: str, value: str, max_suggestions: int = 3) -> List[str]:
    """Get similar values from the predefined options for an attribute
    
    Args:
        attr: The attribute name
        value: The current value
        max_suggestions: Maximum number of suggestions to return
    
    Returns:
        List of similar standard values
    """
    if not value:
        return []
    
    standard_values = get_attribute_options(attr)
    if not standard_values:
        return []
    
    # Find similar values using difflib
    similar_values = difflib.get_close_matches(value, standard_values, n=max_suggestions, cutoff=0.6)
    return similar_values

def update_attribute(attr: str, value: str) -> Tuple[str, str, str]:
    """Update an attribute in the current sample
    
    Returns:
        Tuple[str, str, str]: Issues text, formatted attributes, and status message
    """
    global current_data, modified, issues
    
    status_msg = ""
    
    if value:
        # Check if the value is in the standard options
        if not validate_attribute(attr, value) and attr in ["brand_name", "vehicle_color", "orientation", 
                                 "label", "itype", "type", "special_type"]:
            # Get suggestions for similar values
            suggestions = get_similar_values(attr, value)
            if suggestions:
                suggestion_text = ", ".join(suggestions)
                status_msg = f"Warning: '{value}' is not a standard {attr}. Did you mean: {suggestion_text}?"
            else:
                status_msg = f"Warning: '{value}' is not a standard {attr}. Using custom value."
        
        # Preserve critical data that should never be lost
        if "img_name" not in current_data and attr != "img_name" and len(current_data) == 0:
            # Load original data if current_data is empty to ensure we don't lose metadata
            if samples and current_sample_index < len(samples):
                original_data = load_json_data(samples[current_sample_index])
                # Copy basic metadata
                for meta_key in ["img_name", "width", "height"]:
                    if meta_key in original_data:
                        current_data[meta_key] = original_data[meta_key]
        
        current_data[attr] = value
        if not status_msg:
            status_msg = f"Updated {attr} to '{value}' (in memory only, original file untouched)"
    elif attr in current_data:
        # Don't allow removing essential metadata
        if attr not in ["img_name", "width", "height"]:
            del current_data[attr]
            status_msg = f"Removed {attr} (in memory only, original file untouched)"
        else:
            status_msg = f"Cannot remove essential metadata: {attr}"
    
    modified = True
    issues = validate_json_structure(current_data)
    
    # Return issues, current attributes, and status message
    issues_text = "\n".join(issues) if issues else "No issues detected"
    return issues_text, get_formatted_attributes(), status_msg

def get_formatted_attributes() -> str:
    """Get a formatted string of all current attributes"""
    attr_list = []
    for key, value in current_data.items():
        if key not in ["img_name", "width", "height"]:  # Skip metadata
            attr_list.append(f"{key}: {value}")
    
    return "\n".join(attr_list) if attr_list else "No attributes"

def save_changes() -> List:
    """Save changes to the current sample
    
    Returns:
        List: UI updates including status message and formatted attributes
    """
    global modified, previous_data, verified_status
    
    if not samples or current_sample_index < 0 or current_sample_index >= len(samples):
        return "No sample selected", get_formatted_attributes()
    
    current_path = samples[current_sample_index]
    
    if modified:
        # Store the current state before saving if not already backed up
        if current_path in previous_data:
            # Don't overwrite previous backup if it exists
            pass
        else:
            # Create a backup of the current state
            previous_data[current_path] = load_json_data(current_path).copy()
        
        # Ensure we have essential metadata
        original_data = load_json_data(current_path)
        for meta_key in ["img_name", "width", "height"]:
            if meta_key not in current_data and meta_key in original_data:
                current_data[meta_key] = original_data[meta_key]
        
        # Mark as not modified since we're saving now
        modified = False
        status_msg = f"Changes recorded for {os.path.basename(current_path)} (original file unchanged)"
        
        # If the sample is verified, also save to the output directory
        if verified_status:
            base_name = os.path.basename(current_path)
            output_file_path = os.path.join(OUTPUT_DIR, base_name)
            
            try:
                # Save to the verified directory, leaving original untouched
                save_json_data(current_data, output_file_path)
                status_msg += " and saved to verified output directory"
            except Exception as e:
                status_msg += f"\nError saving to output directory: {str(e)}"
    else:
        status_msg = "No changes to save"
    
    # Get updated status text with the additional message
    status_text = update_with_status(status_msg)[1]
    
    return status_text, get_formatted_attributes()

def undo_changes() -> List:
    """Undo the last saved changes for the current sample"""
    global current_data, modified, issues, verified_status
    
    current_path = samples[current_sample_index]
    status_msg = ""
    
    if current_path in previous_data:
        # Get the original data to ensure we have all metadata
        original_data = load_json_data(current_path)
        
        # Restore the previous state
        current_data = previous_data[current_path].copy()
        
        # Make sure we're not losing any metadata
        for meta_key in ["img_name", "width", "height"]:
            if meta_key not in current_data and meta_key in original_data:
                current_data[meta_key] = original_data[meta_key]
                
        modified = True  # Mark as modified so next save will update the file
        issues = validate_json_structure(current_data)
        
        # Remove the backup data
        del previous_data[current_path]
        
        # Update verification status
        progress = load_progress()
        verified_status = current_path in progress["verified"]
        
        status_msg = f"Changes for {os.path.basename(current_path)} have been undone"
    else:
        # No previous state to restore
        status_msg = "No changes available to undo"
    
    # Return with the status message
    return update_with_status(status_msg)

def verify_sample() -> Tuple[str, bool, str]:
    """Mark the current sample as verified
    
    Returns:
        Tuple[str, bool, str]: Status message, verification status, and formatted attributes
    """
    global verified_status, previous_data
    
    # First save any changes to memory (not to the original file)
    status_msg, attrs = save_changes()
    
    current_path = samples[current_sample_index]
    
    # Get the output file path
    base_name = os.path.basename(current_path)
    output_file_path = os.path.join(OUTPUT_DIR, base_name)
    
    # Only save to the verified_data directory, not to the original file
    try:
        # Ensure we have all metadata from the original file
        original_data = load_json_data(current_path)
        
        # Make sure we're not losing any metadata
        for meta_key in ["img_name", "width", "height"]:
            if meta_key not in current_data and meta_key in original_data:
                current_data[meta_key] = original_data[meta_key]
        
        # Ensure all attributes have values (default to "None of the above")
        attribute_defaults = {
            "label": "None of the above",
            "orientation": "None of the above",
            "brand_name": "None of the above",
            "vehicle_color": "None of the above",
            "itype": "None of the above",
            "type": "None of the above",
            "special_type": "None of the above"
        }
        
        # Apply defaults for missing attributes
        for attr, default_value in attribute_defaults.items():
            if attr not in current_data:
                current_data[attr] = default_value
                
        # Save only to the verified directory, leaving original untouched
        save_json_data(current_data, output_file_path)  # Save to verified directory
        file_saved = True
    except Exception as e:
        file_saved = False
        print(f"Error saving verified file: {str(e)}")
    
    # Mark as verified in the progress tracker
    mark_as_verified(current_path)
    verified_status = True
    
    # Clear undo history for this sample once verified
    if current_path in previous_data:
        del previous_data[current_path]
    
    # Build status message
    result_msg = f"{status_msg}\nSample marked as verified"
    if file_saved:
        result_msg += " and saved to verified data directory (original file untouched)"
    
    return result_msg, True, attrs

def filter_samples(filter_verified: bool) -> List:
    """Filter samples based on verification status"""
    global samples, current_sample_index, current_data, modified, issues
    
    # Save current changes if needed
    if modified and samples and 0 <= current_sample_index < len(samples):
        save_changes()
    
    # Clear current data to force reloading from file
    current_data = {}
    modified = False
    issues = []
    
    progress = load_progress()
    
    if filter_verified:
        # Show only verified samples
        samples = [s for s in get_all_samples() if s in progress["verified"]]
        if not samples:
            # If no verified samples, set index to invalid and show message
            current_sample_index = -1
            return update_with_status("No verified samples found. Verify samples to see them here.")
    else:
        # Show only pending samples
        samples = [s for s in get_all_samples() if s in progress["pending"]]
        if not samples:
            # If no pending samples, set index to invalid and show message
            current_sample_index = -1
            return update_with_status("No pending samples found. All samples have been verified!")
    
    # If we have samples, set to the first one
    current_sample_index = 0 if samples else -1
    
    # Update the interface
    return update_with_status()

def show_all_samples() -> List:
    """Show all samples (both verified and pending)"""
    global samples, current_sample_index, current_data, modified, issues
    
    # Save current changes if needed
    if modified and samples and 0 <= current_sample_index < len(samples):
        save_changes()
    
    # Clear current data to force reloading from file
    current_data = {}
    modified = False
    issues = []
    
    samples = get_all_samples()
    
    if not samples:
        current_sample_index = -1
        return update_with_status("No samples found in the input directory. Please check your configuration.")
    
    current_sample_index = 0
    return update_with_status()

def export_statistics() -> str:
    """Export statistics about the dataset"""
    stats = export_dataset_stats()
    report_path = os.path.join(OUTPUT_DIR, f"AOT_report_{get_timestamp()}.txt")
    report_file = generate_report(stats, report_path)
    
    return f"Report exported to {report_file}"

def reset_changes() -> List:
    """Reset all unsaved changes to the current sample"""
    global current_data, modified, issues
    
    current_path = samples[current_sample_index]
    
    # Remember any metadata values we had
    metadata = {}
    for meta_key in ["img_name", "width", "height"]:
        if meta_key in current_data:
            metadata[meta_key] = current_data[meta_key]
    
    # Reload the JSON data from disk
    current_data = load_json_data(current_path)
    
    # Make sure we don't lose metadata if it was missing in the file
    for meta_key, value in metadata.items():
        if meta_key not in current_data:
            current_data[meta_key] = value
            
    modified = False
    issues = validate_json_structure(current_data)
    
    # Return with the status message
    return update_with_status("Discarded all unsaved changes")

def unmark_verified() -> Tuple[str, bool, str]:
    """Remove a sample from the verified list
    
    Returns:
        Tuple[str, bool, str]: Status message, verification status, and formatted attributes
    """
    global verified_status
    
    current_path = samples[current_sample_index]
    progress = load_progress()
    
    if current_path in progress["verified"]:
        # Get the output file path
        base_name = os.path.basename(current_path)
        output_file_path = os.path.join(OUTPUT_DIR, base_name)
        
        # Remove the file from verified directory if it exists
        if os.path.exists(output_file_path):
            try:
                os.remove(output_file_path)
                file_deleted = True
            except Exception as e:
                file_deleted = False
                print(f"Error deleting verified file: {str(e)}")
        else:
            file_deleted = False
        
        # Remove from verified and add to pending
        progress["verified"].remove(current_path)
        if current_path not in progress["pending"]:
            progress["pending"].append(current_path)
        
        # Save updated progress
        save_progress(progress)
        verified_status = False
        
        # Build status message
        status_msg = f"Sample {os.path.basename(current_path)} unmarked as verified"
        if file_deleted:
            status_msg += " and removed from verified data directory"
        
        return status_msg, False, get_formatted_attributes()
    else:
        return "Sample was not in verified list", verified_status, get_formatted_attributes()

def check_verified_status() -> str:
    """Check if the current sample is verified and prepare confirmation message
    
    Returns:
        str: Confirmation message
    """
    global verified_status
    
    if not samples or current_sample_index < 0 or current_sample_index >= len(samples):
        return "No sample is currently selected"
    
    if not verified_status:
        return "This sample is not marked as verified"
    
    current_path = samples[current_sample_index]
    return f"Are you sure you want to unmark sample {os.path.basename(current_path)} as verified? This will delete the file from the verified data directory."

def update_attr_and_refresh(attr, value):
    """Update an attribute and refresh the entire UI
    
    This function updates an attribute value, records any warnings or issues,
    and ensures the interface is fully refreshed with the current attribute values.
    
    Args:
        attr: The attribute name to update
        value: The new value for the attribute
        
    Returns:
        List: Updated UI elements
    """
    global current_data, modified, verified_status
    
    # If value is None, do nothing (this happens when dropdown is clicked but no selection is made)
    if value is None:
        return update_interface()
        
    # Call update_attribute to get the warnings and messages
    issues_txt, attrs_txt, status_msg = update_attribute(attr, value)
    
    # Explicitly save the changes to ensure they persist
    if samples and 0 <= current_sample_index < len(samples):
        current_path = samples[current_sample_index]
        
        # Store the current state as a backup
        if current_path not in previous_data:
            try:
                previous_data[current_path] = load_json_data(current_path).copy()
            except Exception:
                previous_data[current_path] = {}
        
        # If this sample is already verified, immediately update the output file
        if verified_status:
            base_name = os.path.basename(current_path)
            output_file_path = os.path.join(OUTPUT_DIR, base_name)
            
            try:
                # Save only to the verified directory, leaving original untouched
                save_json_data(current_data, output_file_path)
                status_msg += "\nChanges saved to verified output directory"
            except Exception as e:
                status_msg += f"\nError saving to output directory: {str(e)}"
    
    # Now refresh the whole interface with the status message
    # Force a complete refresh of the UI to ensure all attributes are displayed correctly
    result = update_interface()
    
    # Add the status message to the result
    if status_msg:
        result[1] = result[1] + f"\n\n{status_msg}"
    
    return result

def build_ui():
    """Build the Gradio UI"""
    with gr.Blocks(title="AOT - AttributeannOtationTool") as app:
        gr.Markdown("# AOT - AttributeannOtationTool")
        gr.Markdown("### Vehicle Attribute Verification and Annotation")
        gr.Markdown("*Note: Original files in the input directory remain untouched. Only verified files are saved to the output directory.*")
        
        with gr.Row():
            with gr.Column(scale=2):
                image_display = gr.Image(label="Vehicle Image", type="pil")
                status_text = gr.Textbox(label="Status", interactive=False)
                
                with gr.Row():
                    prev_btn = gr.Button("Previous")
                    next_btn = gr.Button("Next")
                
                with gr.Row():
                    sample_index = gr.Number(label="Jump to sample #", value=1, precision=0)
                    jump_btn = gr.Button("Go")
                
                with gr.Row():
                    show_all_btn = gr.Button("Show All")
                    show_verified_btn = gr.Button("Show Verified")
                    show_pending_btn = gr.Button("Show Pending")
            
            with gr.Column(scale=3):
                with gr.Group():
                    gr.Markdown("### Attributes")
                    
                    label = gr.Dropdown(label="Vehicle Label", choices=get_attribute_options("label"), allow_custom_value=True)
                    orientation = gr.Dropdown(label="Orientation", choices=get_attribute_options("orientation"), allow_custom_value=True)
                    brand_name = gr.Dropdown(label="Brand Name", choices=get_attribute_options("brand_name"), allow_custom_value=True)
                    vehicle_color = gr.Dropdown(label="Vehicle Color", choices=get_attribute_options("vehicle_color"), allow_custom_value=True)
                    itype = gr.Dropdown(label="Internal Type", choices=get_attribute_options("itype"), allow_custom_value=True)
                    vehicle_type = gr.Dropdown(label="Vehicle Type", choices=get_attribute_options("type"), allow_custom_value=True)
                    special_type = gr.Dropdown(label="Special Type", choices=get_attribute_options("special_type"), allow_custom_value=True)
                    
                    # Display current attributes
                    current_attrs = gr.Textbox(label="Current Attributes", interactive=False)
                
                issues_text = gr.Textbox(label="Issues", interactive=False)
                
                # Organize buttons for better layout
                with gr.Row():
                    save_btn = gr.Button("Save Changes (In Memory Only)", variant="primary")
                    undo_btn = gr.Button("Undo Saved Changes", variant="secondary")
                    reset_btn = gr.Button("Reset Unsaved Changes", variant="secondary")
                
                # Verification controls in their own group
                with gr.Group():
                    gr.Markdown("### Verification Controls")
                    gr.Markdown("*Verified samples are saved to the output directory. Original files remain untouched.*")
                    # Verification status indicator
                    verified_status = gr.Checkbox(label="Verified", interactive=False)
                    
                    with gr.Row():
                        verify_btn = gr.Button("Mark as Verified & Save to Output", variant="primary")
                        unverify_btn = gr.Button("Unmark Verified", variant="secondary")
                    
                    # Confirmation for unmarking
                    unverify_confirm = gr.Textbox(label="Confirmation", interactive=False, visible=False)
                    with gr.Row(visible=False) as confirm_row:
                        confirm_yes_btn = gr.Button("Yes, Unmark", variant="stop")
                        confirm_no_btn = gr.Button("No, Cancel", variant="secondary")

                export_stats_btn = gr.Button("Export Statistics")
                export_result = gr.Textbox(label="Export Result", interactive=False)
        
        # Event handlers
        next_btn.click(next_sample, inputs=[], outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs])
        prev_btn.click(prev_sample, inputs=[], outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs])
        
        jump_btn.click(lambda x: jump_to_sample(int(x) - 1), inputs=[sample_index], outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs])
        
        # Sample filtering handlers with explicit error handling
        def safe_filter(filter_verified):
            try:
                return filter_samples(filter_verified)
            except Exception as e:
                print(f"Error in filter_samples: {str(e)}")
                # Set to invalid state
                global current_sample_index
                current_sample_index = -1
                # Return a graceful error message
                return update_with_status(f"An error occurred while filtering samples: {str(e)}")
        
        show_all_btn.click(
            lambda: show_all_samples(), 
            inputs=[], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        show_verified_btn.click(
            lambda: safe_filter(True), 
            inputs=[], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        show_pending_btn.click(
            lambda: safe_filter(False), 
            inputs=[], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        
        # Update the attribute change handlers to be more stable
        # Only trigger attribute updates when there's a real selection change
        label.select(
            lambda x: update_attr_and_refresh("label", x), 
            inputs=[label], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        orientation.select(
            lambda x: update_attr_and_refresh("orientation", x), 
            inputs=[orientation], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        brand_name.select(
            lambda x: update_attr_and_refresh("brand_name", x), 
            inputs=[brand_name], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        vehicle_color.select(
            lambda x: update_attr_and_refresh("vehicle_color", x), 
            inputs=[vehicle_color], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        itype.select(
            lambda x: update_attr_and_refresh("itype", x), 
            inputs=[itype], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        vehicle_type.select(
            lambda x: update_attr_and_refresh("type", x), 
            inputs=[vehicle_type], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        special_type.select(
            lambda x: update_attr_and_refresh("special_type", x), 
            inputs=[special_type], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        
        # Create a wrapper for save_changes that updates the whole UI
        def save_and_refresh():
            """Save changes and refresh the UI
            
            This function saves changes to the current sample and ensures that
            the UI is fully refreshed with the current attribute values.
            
            Returns:
                List: Updated UI elements
            """
            # Save changes and get the status message
            status_msg, _ = save_changes()
            
            # Force a complete UI refresh to ensure all attributes are displayed correctly
            result = update_interface()
            
            # Update the status message in the result
            if status_msg:
                result[1] = status_msg
            
            return result
        
        save_btn.click(
            save_and_refresh, 
            inputs=[], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        
        undo_btn.click(
            undo_changes, 
            inputs=[], 
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        reset_btn.click(
            reset_changes,
            inputs=[],
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        
        # Define a wrapper function for verify_sample to make it return the correct type
        def verify_and_update():
            result, status, _ = verify_sample()
            return update_with_status(result)
            
        verify_btn.click(
            verify_and_update,
            inputs=[],
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        )
        
        # Unverify button shows confirmation
        unverify_btn.click(
            check_verified_status,
            inputs=[],
            outputs=[unverify_confirm]
        ).then(
            lambda: (gr.update(visible=True), gr.update(visible=True)),
            inputs=[],
            outputs=[unverify_confirm, confirm_row]
        )
        
        # Define a wrapper function for unmark_verified
        def unmark_and_update():
            result, _, _ = unmark_verified()
            return update_with_status(result)
            
        # Confirm or cancel buttons
        confirm_yes_btn.click(
            unmark_and_update,
            inputs=[],
            outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs]
        ).then(
            lambda: (gr.update(visible=False), gr.update(visible=False)),
            inputs=[],
            outputs=[unverify_confirm, confirm_row]
        )
        
        # Function to cancel unverify operation
        def cancel_unverify():
            # Return status with the cancellation message preserved
            return update_with_status("Unmarking cancelled")[1]
        
        confirm_no_btn.click(
            cancel_unverify,
            inputs=[],
            outputs=[status_text]
        ).then(
            lambda: (gr.update(visible=False), gr.update(visible=False)),
            inputs=[],
            outputs=[unverify_confirm, confirm_row]
        )
        
        export_stats_btn.click(export_statistics, inputs=[], outputs=[export_result])
        
        # Add a function to update all attributes display
        def refresh_attributes() -> str:
            """Return a formatted string of all current attributes"""
            attr_list = []
            for key, value in current_data.items():
                if key not in ["img_name", "width", "height"]:  # Skip metadata
                    attr_list.append(f"{key}: {value}")
            
            return "\n".join(attr_list) if attr_list else "No attributes"
        
        # Add a refresh button for attributes
        with gr.Row():
            refresh_btn = gr.Button("Refresh Attributes")
        
        refresh_btn.click(get_formatted_attributes, inputs=[], outputs=[current_attrs])
        
        # Initialize the interface
        app.load(update_with_status, inputs=[], outputs=[image_display, status_text, label, orientation, brand_name, vehicle_color, itype, vehicle_type, special_type, issues_text, verified_status, current_attrs])
    
    return app

if __name__ == "__main__":
    app = build_ui()
    app.launch(share=False) 