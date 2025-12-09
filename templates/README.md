# Templates Directory

This directory contains template images for computer vision-based UI automation.

## Structure

```
templates/
├── buttons/         # Button templates (export, import, save, ok, etc.)
├── icons/          # Icon templates (capcut_icon, exporting_icon, etc.)
└── status/         # Status indicators (export_complete, export_progress, etc.)
```

## Usage

Templates are PNG images used for template matching with OpenCV. They should:
- Be clear screenshots of UI elements
- Have consistent size and quality
- Be captured at standard screen resolution
- Be named descriptively

## Adding Templates

You can add templates in two ways:

1. **Manual**: Place PNG files in appropriate category folder
2. **Auto-capture**: Use the GUI's "Capture Template" feature

## Versioning

Templates can have versions for different CapCut releases:
- `export_button.png` - Default version
- `export_button_v2.png` - Version 2
- `export_button_v3.png` - Version 3

## Management

Templates are managed by `TemplateManager` service which provides:
- Template loading and caching
- Version management
- Validation
- Metadata tracking
