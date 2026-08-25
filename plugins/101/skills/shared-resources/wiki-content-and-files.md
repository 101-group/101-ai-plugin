# Wiki Content and Files

- A Wiki contains pages and ordered Wiki blocks. Change structure only through existing Wiki tools.
- Upload a file through `upload_files`, then place the current API result into the page media block.
- Images and ordinary files differ by block type and API-returned metadata; never infer either from a filename.
- Removing media from a page means deleting the corresponding Wiki block.
- Physical deletion from storage is outside this workflow and must not be simulated.
- After a mutation, reread the affected page or blocks and report the actual state.
