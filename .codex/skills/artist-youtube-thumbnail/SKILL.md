---
name: artist-youtube-thumbnail
description: "Create a polished 1024x564 YouTube thumbnail for an artist biography or art-history story from three inputs: artist name, a local reference folder containing artwork images and story files, and the exact video title. Use when Codex must inspect local artist materials, search the web for an authoritative portrait or photograph, generate an artist-story thumbnail, preserve exact title text, and save a ready-to-upload PNG in the reference folder's YouTube subfolder."
---

# Artist YouTube Thumbnail

Create one ready-to-upload 1024x564 PNG from the user's artist name, reference folder, and exact video title. Use local materials as the primary evidence and web search only to supplement the artist's likeness. Save the final image under `<reference_folder>/YouTube/`.

## Required inputs

Collect these values before generation:

1. `artist_name`: artist name, preferably in the user's desired display language.
2. `reference_folder`: local folder containing artwork images and story material.
3. `video_title`: exact title to appear on the thumbnail.

Ask only for missing values. Treat the supplied title as verbatim text; do not translate, shorten, or correct it unless requested.

## Workflow

### 1. Inspect the reference folder

- Use `rg --files <folder>` first; fall back to a recursive directory listing if needed.
- Read relevant `.md` and `.txt` files. Use the appropriate installed document/PDF skill when other source formats require it.
- Inspect candidate images with `view_image`. Favor a recognizable portrait plus one or two visually strong representative artworks.
- Extract a compact creative brief: period, movement, signature works, major theme, visual motifs, mood, and historically appropriate palette.
- Never modify source files.

### 2. Search for the artist's likeness

Web browsing is mandatory because the user explicitly requests an image search.

- Run two or three focused `image_query` searches such as `<artist> portrait`, `<artist> self portrait`, and `<artist> Wikimedia Commons`.
- For artists before photography, accept a self-portrait, documented historical portrait, engraving, sculpture, or manuscript likeness. Do not invent a modern photograph.
- Open the source page and verify identity, attribution, and provenance. Prefer museum collections, archives, Wikimedia Commons, national libraries, and public-domain or openly licensed files.
- Do not use an image-search preview as provenance. Record the source-page URL and creator/license information when available.
- Save the selected file locally when a lawful direct file is available. If no suitable reusable image exists, use search results only as visual research and rely on the best local portrait or a historically plausible generated likeness; state this limitation in the final handoff.

### 3. Build the visual concept

- Select at most four references: one likeness and one to three artworks or locations.
- Establish one clear focal face or figure, one supporting artwork/environment, and a dedicated title zone.
- Match the art period without copying unrelated modern styles.
- Optimize for small-screen readability: bold silhouette, high contrast, restrained detail, and no visual clutter behind the title.
- Default to placing the artist on one side and reserving the opposite 45–55% for title text. Choose the side that preserves important artwork details.

### 4. Generate the artwork layer

- Read and follow the installed `imagegen` skill. Tell the user when it causes an action.
- Use the built-in image generation tool and pass every selected local reference image as a labeled reference.
- Generate a landscape YouTube-thumbnail composition with a clean title zone, but instruct the model to include **no text, letters, logos, captions, or watermark**. Add the exact title deterministically in the next step.
- Request a 1024x564 composition. If the generator returns another size, preserve the intended framing and normalize it with the bundled script.
- Keep recognizable features from the artist likeness and supplied artworks. Avoid fabricated signatures, anachronisms, modern props, and extra people that are not compositionally necessary.

Use this prompt scaffold:

```text
Use case: ads-marketing
Asset type: YouTube thumbnail, landscape, final delivery 1024x564
Primary request: Create an art-history thumbnail for <artist_name> using the supplied references and local story brief.
Input images: Image 1: artist likeness; Images 2–4: representative artwork/location references.
Subject: <artist and key motif>
Style/medium: cinematic editorial composition grounded in <period/movement>
Composition/framing: artist on <left/right>; uncluttered title zone on the opposite side
Lighting/mood: <brief-derived lighting and mood>
Color palette: <brief-derived palette>
Constraints: preserve recognizable references; no text, letters, logo, caption, signature, or watermark; no anachronisms
```

### 5. Add the exact title and normalize dimensions

Set `output_folder` to `<reference_folder>/YouTube`. Create it when it does not exist, and verify its resolved path remains inside `reference_folder`. Choose the first available filename in this sequence:

1. `youtube-thumbnail-<artist-slug>.png`
2. `youtube-thumbnail-<artist-slug>-v2.png`
3. Continue with `-v3`, `-v4`, and so on.

Run the bundled script after generation:

```powershell
python scripts/finalize_thumbnail.py --input <generated-image> --output "<reference_folder>/YouTube/youtube-thumbnail-<artist-slug>.png" --title "<video_title>" --text-side right
```

- Resolve the script path relative to this skill directory.
- Use `--text-side left` when the generated portrait occupies the right.
- Use `--font <path>` only when a specific display font is required.
- The script center-crops safely, resizes to exactly 1024x564, separates `Artist - Subtitle` into a highlighted artist line and supporting subtitle, wraps Traditional Chinese by character width, and writes a PNG.
- If the panel covers an important face or artwork detail, regenerate once with more negative space or switch `--text-side`.

### 6. Validate and deliver

- Verify the final file is exactly 1024x564 and in PNG format.
- Inspect it with `view_image` at full view and mentally at small thumbnail scale.
- Confirm the title is exact, complete, readable, and not clipped.
- Confirm the artist is recognizable and at least one local artwork/reference visibly informs the image.
- Confirm there is no watermark, stray model-generated text, or anachronistic object.
- Save only in `<reference_folder>/YouTube/` unless the user explicitly supplies another destination. Never save the final image directly in the reference-folder root. Never overwrite an existing file; add `-v2`, `-v3`, and so on.
- In the final response, provide the saved path, the portrait/source-page citation, and a one-sentence note naming the local references used. Do not claim a searched image was directly incorporated unless it was actually supplied to generation.

## Failure handling

- If a local image cannot be decoded, omit it and use the next strongest reference; do not stop when enough valid material remains.
- If the folder contains no story file, derive the brief from artwork filenames and authoritative web sources, then note the limitation.
- If no likeness can be verified, emphasize the artworks and period rather than presenting an invented face as authentic.
- If image generation fails, report the failure and the prepared brief; do not substitute an SVG, HTML mockup, or unrelated stock image.
