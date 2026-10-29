# Final English Caption

Video duration: {duration:.2f} seconds
Sampled frames: {num_frames} at {fps} FPS

## Authoritative Segments

Use these exact boundaries. Never merge, reorder, or adjust times:

{precomputed_event_segments}

## Task and Invariants

All video evidence was supplied as successive segments in previous turns. No
additional frames are attached to this final request. Review the observed
segments and intermediate drafts, then return one complete, English-only JSON
object containing exactly one top-level key: "english_json".

- Finalize perspective_view, Style and the numbered subject_list for the entire
  video. Merge duplicate subjects and correct mistaken identities.
- Produce exactly one segment caption per authoritative segment, retaining
  the exact start_time and end_time.
- The first segment has a nonempty visual_description_long (about 80–200 words)
  and null description_change.
- Every later segment has null visual_description_long and a nonempty
  description_change starting "Compared to the previous segment, ".
- Scene and camera descriptions must never describe a main subject's actions.
  All subject actions belong in contained_actions. Every main-subject
  reference uses its precise <|SubjectN|> token inside an
  <ActionK>...</ActionK> wrapper; never use names or pronouns instead.
- Camera movement is described inside <CameraK>...</CameraK> wrappers in the
  scene descriptions, never inside action wrappers.
- Action and camera IDs each restart from 1 on every segment without gaps.
  Actions must be chronological, non-overlapping, and within segment bounds.
  Camera wrappers and action wrappers must never be nested.
- Use only visible evidence, not guesses about future segments.
- Output valid raw JSON, with no markdown, explanation, translation,
  extra fields or intermediate evidence keys.

## Required Output Schema

{
  "english_json": {
    "perspective_view": "third-person observer",
    "Style": "real-world footage",
    "subject_list": [
      {
        "subject_id": "<|Subject1|>",
        "display_name": "English subject name",
        "subject_attribute": "English visible attributes"
      }
    ],
    "segments": [
      {
        "start_time": "00:00.000",
        "end_time": "00:05.000",
        "visual_description_long": "Scene and camera details for segment one",
        "description_change": null,
        "contained_actions": [
          {
            "start_time": "00:00.000",
            "end_time": "00:05.000",
            "action_description": "<Action1><|Subject1|> performs a visible action</Action1>"
          }
        ]
      }
    ]
  }
}

The schema example is illustrative only. Use the real segment boundaries.
