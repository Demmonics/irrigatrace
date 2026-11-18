# Stitch MCP Tool Inventory

Confirmed and inspected from `C:\Users\yoosh\.gemini\antigravity-ide\mcp\StitchMCP`:

## 1. Project Management
- **`create_project`**
  - Params: `title` (string, optional)
  - Returns: Project object with `name` (format `projects/{project_id}`) and `title`.
- **`get_project`**
  - Params: `name` (string, required, e.g. `projects/4044680601076201931`)
- **`list_projects`**
  - Params: `pageSize`, `pageToken`
- **`delete_project`**
  - Params: `name` (string, required)

## 2. Screen Generation & Editing
- **`generate_screen_from_text`**
  - Params:
    - `projectId` (string, required, without `projects/` prefix)
    - `prompt` (string, required)
    - `designSystem` (string, optional, e.g. `assets/...`)
    - `deviceType` ("DESKTOP" | "MOBILE" | "TABLET" | "AGNOSTIC")
    - `modelId` ("GEMINI_3_8_FLASH" | "GEMINI_3_5_FLASH_LITE")
  - Output: Contains screen details, components, suggestions.
- **`edit_screens`**
  - Params: `projectId`, `screenIds`, `prompt`
- **`generate_variants`**
  - Params: `projectId`, `screenId`, `prompt`, `variantCount`

## 3. Screen Inspection & Assets
- **`get_screen`**
  - Params: `name` (string, required: `projects/{project}/screens/{screen}`)
  - Returns: Screen metadata, `html_code` object, `screenshot` object.
- **`list_screens`**
  - Params: `parent` (`projects/{project}`)
- **`download_file`**
  - Params: `name` (string, required: `projects/{project}/files/{file}`)
  - Returns: `html` (raw string for HTML) or `image` (base64-encoded image bytes with `image_metadata`).

## 4. Design Systems
- **`create_design_system`**, **`create_design_system_from_design_md`**, **`update_design_system`**, **`list_design_systems`**, **`apply_design_system`**, **`upload_design_md`**
