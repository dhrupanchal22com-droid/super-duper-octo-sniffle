# API Documentation

## Core Classes

### DrawingProcessor

Main orchestrator for processing drawings.

```python
from src.core.processor import DrawingProcessor

# Initialize
processor = DrawingProcessor("path/to/drawing.dwg")

# Process
analysis = processor.process()

# Access results
print(f"Windows: {len(analysis.windows)}")
print(f"Doors: {len(analysis.doors)}")
```

**Methods:**
- `process() -> DrawingAnalysis`: Process the drawing file
- `_process_dwg()`: Internal DWG processing
- `_process_pdf()`: Internal PDF processing
- `_process_image()`: Internal image processing

---

### DWGParser

Parse and extract data from DWG files.

```python
from src.core.dwg_parser import DWGParser

parser = DWGParser("drawing.dwg")
if parser.load_file():
    layers = parser.get_layers()
    texts = parser.get_all_texts()
    dimensions = parser.get_all_dimensions()
    blocks = parser.get_blocks()
    inserts = parser.get_block_inserts()
    geometries = parser.get_lines_and_polylines()
```

**Methods:**
- `load_file() -> bool`: Load DWG file
- `get_layers() -> Dict`: Get all layer information
- `get_blocks() -> Dict`: Get block definitions
- `get_all_texts() -> List[Dict]`: Extract text entities
- `get_all_dimensions() -> List[Dict]`: Extract dimensions
- `get_block_inserts() -> List[Dict]`: Get block instances
- `get_lines_and_polylines() -> List[Dict]`: Get geometric entities

---

### WindowDetector

Detect windows from images and annotations.

```python
from src.detection.window_detector import WindowDetector
import cv2

detector = WindowDetector()

# From image
image = cv2.imread("drawing.jpg")
windows = detector.detect_windows_from_image(image, scale_factor=1.0)

# From text annotations
texts = [{"value": "WINDOW 1200x800"}]
windows = detector.detect_windows_from_text_annotations(texts)

# Remove duplicates
unique_windows = detector.remove_duplicates(windows, tolerance_mm=50)
```

**Methods:**
- `detect_windows_from_image(image, scale_factor) -> List[Window]`
- `detect_windows_from_text_annotations(texts) -> List[Window]`
- `remove_duplicates(windows, tolerance_mm) -> List[Window]`

---

### DoorDetector

Detect doors from images and annotations.

```python
from src.detection.door_detector import DoorDetector
import cv2

detector = DoorDetector()

# From image
image = cv2.imread("drawing.jpg")
doors = detector.detect_doors_from_image(image, scale_factor=1.0)

# From text annotations
texts = [{"value": "DOOR 900x2100"}]
doors = detector.detect_doors_from_text_annotations(texts)

# Remove duplicates
unique_doors = detector.remove_duplicates(doors, tolerance_mm=50)
```

**Methods:**
- `detect_doors_from_image(image, scale_factor) -> List[Door]`
- `detect_doors_from_text_annotations(texts) -> List[Door]`
- `remove_duplicates(doors, tolerance_mm) -> List[Door]`

---

### ScaleDetector

Detect drawing scale from annotations.

```python
from src.detection.scale_detector import ScaleDetector

detector = ScaleDetector()

# From title block
texts = [{"value": "SCALE: 1:100"}]
scale = detector.detect_from_title_block(texts)

# From reference dimensions
dimensions = [{"value": "1000"}]
scale = detector.detect_from_reference_dimensions(dimensions, 10000)

# Default fallback
scale = detector.estimate_default_scale()
```

**Methods:**
- `detect_from_title_block(texts) -> Optional[float]`
- `detect_from_reference_dimensions(dimensions, known_dimension) -> Optional[float]`
- `estimate_default_scale() -> float`

---

### ExcelGenerator

Generate Excel reports.

```python
from src.export.excel_generator import ExcelGenerator
from src.data.models import DrawingAnalysis

# Create generator
generator = ExcelGenerator("output.xlsx")

# Add sheets
generator.create_summary_sheet(analysis)
generator.create_windows_sheet(analysis.windows)
generator.create_doors_sheet(analysis.doors)

# Save
generator.save()
```

**Methods:**
- `create_summary_sheet(analysis)`: Create summary sheet
- `create_windows_sheet(windows)`: Create windows sheet
- `create_doors_sheet(doors)`: Create doors sheet
- `save() -> bool`: Save workbook to file

---

## Data Models

### Window

```python
@dataclass
class Window:
    id: str                          # Unique identifier
    window_type: WindowType          # Sliding, Casement, Fixed, etc.
    width_mm: float                  # Width in millimeters
    height_mm: float                 # Height in millimeters
    quantity: int = 1                # Number of identical windows
    location: str = ""               # Location/room name
    glass_type: str = ""             # Type of glass
    glass_thickness_mm: Optional[float] = None
    frame_material: str = "Aluminum"
    position: Optional[Point] = None
    bounding_box: Optional[BoundingBox] = None
    layer: str = ""                  # DWG layer
    confidence_score: float = 0.0    # Detection confidence (0-1)
    notes: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
    manual_override: bool = False
```

**Methods:**
- `to_dict() -> dict`: Convert to dictionary

---

### Door

```python
@dataclass
class Door:
    id: str                          # Unique identifier
    door_type: DoorType              # Hinged, Sliding, Bifold, etc.
    width_mm: float                  # Width in millimeters
    height_mm: float                 # Height in millimeters
    quantity: int = 1
    location: str = ""
    material: str = "Aluminum"
    frame_type: str = ""
    position: Optional[Point] = None
    bounding_box: Optional[BoundingBox] = None
    layer: str = ""
    confidence_score: float = 0.0
    notes: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
    manual_override: bool = False
```

**Methods:**
- `to_dict() -> dict`: Convert to dictionary

---

### DrawingAnalysis

```python
@dataclass
class DrawingAnalysis:
    file_path: str
    file_name: str
    file_type: str                   # "DWG", "PDF", "IMAGE"
    windows: List[Window] = field(default_factory=list)
    doors: List[Door] = field(default_factory=list)
    detected_scale: float = 1.0      # mm per unit
    total_area_mm2: float = 0.0
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_seconds: float = 0.0
    status: str = "Pending"          # Pending, Processing, Complete, Error
    error_message: str = ""
```

---

## Enumerations

### WindowType
- `SLIDING`: Sliding window
- `CASEMENT`: Casement window
- `FIXED`: Fixed window
- `AWNING`: Awning window
- `HOPPER`: Hopper window
- `DOUBLE_HUNG`: Double-hung window
- `UNKNOWN`: Unknown type

### DoorType
- `HINGED`: Hinged door
- `SLIDING`: Sliding door
- `BIFOLD`: Bifold door
- `POCKET`: Pocket door
- `PIVOT`: Pivot door
- `GLASS`: Glass door
- `UNKNOWN`: Unknown type

---

## Usage Examples

### Complete Analysis Pipeline

```python
from src.core.processor import DrawingProcessor
from src.export.excel_generator import ExcelGenerator

# Process drawing
processor = DrawingProcessor("floor_plan.dwg")
analysis = processor.process()

# Check results
if analysis.status == "Complete":
    print(f"Found {len(analysis.windows)} windows")
    print(f"Found {len(analysis.doors)} doors")
    
    # Export to Excel
    generator = ExcelGenerator("results.xlsx")
    generator.create_summary_sheet(analysis)
    generator.create_windows_sheet(analysis.windows)
    generator.create_doors_sheet(analysis.doors)
    generator.save()
else:
    print(f"Error: {analysis.error_message}")
```

### Manual Detection

```python
from src.detection.window_detector import WindowDetector
import cv2

# Load image
image = cv2.imread("drawing.jpg")

# Detect
detector = WindowDetector()
windows = detector.detect_windows_from_image(image, scale_factor=1.0)

# Process results
for window in windows:
    print(f"{window.id}: {window.width_mm}x{window.height_mm} mm")
```

### Batch Processing

```python
from pathlib import Path
from src.core.processor import DrawingProcessor
from src.export.excel_generator import ExcelGenerator

# Process all DWG files in directory
drawings_dir = Path("drawings")

for dwg_file in drawings_dir.glob("*.dwg"):
    processor = DrawingProcessor(str(dwg_file))
    analysis = processor.process()
    
    if analysis.status == "Complete":
        output_file = f"{dwg_file.stem}_analysis.xlsx"
        generator = ExcelGenerator(output_file)
        generator.create_summary_sheet(analysis)
        generator.create_windows_sheet(analysis.windows)
        generator.create_doors_sheet(analysis.doors)
        generator.save()
```

---

## Error Handling

```python
try:
    processor = DrawingProcessor("drawing.dwg")
    analysis = processor.process()
except Exception as e:
    print(f"Processing failed: {e}")
    logger.error(f"Error processing drawing: {e}")

# Check analysis status
if analysis.status == "Error":
    print(f"Error message: {analysis.error_message}")
```

---

## Logging

```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

All logs are saved to `logs/app.log`

