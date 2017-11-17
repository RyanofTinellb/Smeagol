# Page Editor

## User Stories

### New Site

As a site editor, I want to save a new site.

Index|Action|Expected Behaviour
---:|---|---
1. | Open Editor from `%HOMEPATH%` | Blank editor pops up with blank heading.
2. | Press `Ctrl+S` | Window pops up to allow user to modify properties.
3. | Click on the `Browse` button next to the `Source` textbox. | Filesearch pane pops up.
4. | Navigate to `%HOMEPATH%/documents/tinellbianlanguages/smeagol` | Usual Windows behaviour
5. | Select `EditorTest.txt` | Message box pops up `This file already exists. Are you sure you wish to replace it? (Cancel) (OK)`
6. | Click `OK` | Message box disappears. Filesearch pane disappears. `%HOMEPATH%/documents/tinellbianlanguages/smeagol/EditorTest.txt` appears in the `Source` textbox.
7. | Click `OK` in the properties window | Properties window disappears. Heading box holds `Testing`. Main textbox holds `This is a test page`. A new file `%HOMEPATH%/index.html` is created. A new folder `%HOMEPATH%/next` with a file `%HOMEPATH%/next/index.html` is created.
8. | Press `ALT+F4` | Editor closes.
