# Build film review

A separate agent watches the build film frame by frame and says what would confuse a viewer: parts passing through each other or flying the wrong way, the product resting upside down or with its face hidden, flicker, a camera inside a part. It can change the film's direction (how the product rests, where the viewer stands, which way parts back out), and the film is re-rendered and watched again. Automatic checks replay every frame against the 3D models as well.

## desktop

**Verdict:** pass (round 1). A clear, well-oriented build film of the 1984-style compact CM5 all-in-one desktop computer that cleanly shows its front face, front-to-back internal assembly, internal cabling, and final form without part collisions.

| Severity | Time | Shot | What a viewer sees | Fix |
|---|---|---|---|---|
| P1 | 12.0 s | glide | When the 'Compute Module 5' caption is displayed (10.0s-13.0s), the CM5 and main carrier board remain recessed inside the rear bucket behind the opaque LCD panel and front bezel, so the module is mostly occluded as the camera orbits across the front. | Orbit the camera to a wider side angle during the Compute Module 5 caption or briefly ghost the rear bucket side wall and LCD panel so the CM5 is clearly visible. |
| P2 | 22.0 s | boards | The dark-green main PCB nearly touches the top and bottom frame borders and has low lighting contrast against the dark background while small SMD components populate. | Pull the board camera slightly back to add top/bottom margin and increase key/rim lighting on the PCB surface. |
| P2 | 3.0 s | hero | The white subtitle under the opening title card overlaps the illuminated lower edge of the beige enclosure and is truncated mid-phrase ('...desktop computer with'). | Shorten or wrap the subtitle text and place a subtle dark backing or lower-left margin clear of the bright case body. |

## keyboard

**Verdict:** pass (round 1). A clear, well-paced build film that shows the compact 58-key mechanical keyboard from the user's typing perspective, cleanly separates the bottom shell, main PCB, top bezel, and sculpted keycaps in assembly order, and populates the switch matrix before reassembling the finished keyboard.

| Severity | Time | Shot | What a viewer sees | Fix |
|---|---|---|---|---|
| P2 | 20.0 s | boards | The bare dark-green PCB has relatively low contrast against the dark background at 20.0s-21.0s before the light-coloured switch housings populate at 22.0s. | No direction change needed; board lighting and contrast become clear once switches populate at 22.0s. |
| P2 | 29.3 s | settle | As the keycap cluster fades out (29.0s-30.0s) and fades back in during close_up (32.8s-33.4s), semi-transparent alpha rendering briefly shows internal keycap wall facets. | No direction change needed; keycaps render cleanly when opaque before and after the fade transition. |

## mouse

**Verdict:** pass (round 2). This is a clean, easy-to-follow build film of a classic beige single-button USB-C optical mouse that clearly shows the front click button and USB-C port, how the PCB populates, and how the optical window, boot button, board, and shells fit together.

| Severity | Time | Shot | What a viewer sees | Fix |
|---|---|---|---|---|
| P2 | 14.0 s | glide | Per-part callout captions do not appear during the glide orbit (10.0s-18.0s), and transition boundaries at 0.0s (hero), 19.0s (boards), and 26.5s (settle) land on full-black frames. | Render per-part callout labels during the glide shot and avoid full-black frames at shot transitions in the renderer. |
| P2 | 30.8 s | settle | As the translucent top_shell lifts upward and fades out to reveal the seated main board (30.0s-32.8s), its upper edge clips the top border of the frame. | Reduce the upward lift distance or widen framing slightly during the settle/close_up fade-out of lifted enclosure parts. |

