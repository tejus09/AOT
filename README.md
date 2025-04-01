# AOT (AttributeannOtationTool)

A Gradio-based web interface for verifying and annotating vehicle attribute datasets.

## Features

- Browse through vehicle images and their attributes
- Edit existing attribute values or add new attributes
- Validate attributes against predefined lists
- Track verification progress
- Export statistics about the verified dataset
- **Non-destructive workflow**: Original JSON files remain untouched

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Configure input/output directories in `config.py` if needed:
   - `INPUT_DIR`: Directory containing original image/JSON pairs (default: `/home/tejus09/Desktop/PersonAttr/unpadded_data`)
   - `OUTPUT_DIR`: Directory where verified JSON files will be saved (default: `/home/tejus09/Desktop/PersonAttr/verified_data`)

## Usage

1. Run the application:
   ```
   python app.py
   ```
2. Open the web interface (default: http://127.0.0.1:7860)
3. Navigate through samples using Previous/Next buttons
4. Modify attributes as needed:
   - Use dropdown menus to select from predefined values
   - Enter custom values when needed
   - Add completely new attributes using the "Add Custom Attribute" section
5. Click "Save Changes" to save modifications in memory (original files remain unchanged)
6. Click "Mark as Verified & Save to Output" to mark a sample as verified and save it to the output directory
7. Use filtering options to focus on verified or pending samples
8. Export statistics to track annotation progress

## Data Workflow

- **Original files**: Files in the input directory are never modified by the tool
- **In-memory editing**: All changes are kept in memory until you verify a sample 
- **Verified files**: Only when you mark a sample as verified, a copy with your changes is saved to the output directory
- **Verification tracking**: The tool tracks which samples have been verified in a separate progress file

## File Structure

- `app.py`: Main application file with UI and logic
- `config.py`: Configuration parameters and attribute lists
- `data_handler.py`: Functions for loading and saving data
- `validation.py`: Validation logic for attributes
- `utils.py`: Utility functions
- `requirements.txt`: Dependencies

## Output

- Verified JSON files are saved to the output directory
- Statistics can be exported to a text report
- Verification progress is tracked across sessions

## Attribute Categories

The tool supports validation and selection from the following attribute categories:

- Vehicle brands (e.g., Maruti-Suzuki, Honda, Toyota)
- Vehicle colors (e.g., White, Black, Gray)
- Vehicle orientations (Front, Back, Side)
- Vehicle labels (e.g., Car, Motorbike, Bus)
- Vehicle internal types (e.g., LMV, MGWG, LGV)
- Vehicle subtypes (e.g., Sedan, SUV, Hatchback)
- Special vehicle types (e.g., Ambulance, Army_Vehicle)

## Troubleshooting

- If images are not displayed, ensure the image path in the JSON file matches the actual image location
- If the UI doesn't load, check that Gradio is installed correctly
- For verification progress issues, check the permissions on the output directory 