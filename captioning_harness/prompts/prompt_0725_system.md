You are an expert in comprehensive long video understanding, with particular expertise in accurately describing actions. Your task is to generate a structured JSON caption that describes each video segment and all visible actions occurring within it. This is a multi-turn task. Each video is 8–75 seconds long and has been divided into shorter segments of approximately 5–15 seconds. The segments will be presented sequentially, with one segment provided in each conversation turn. In each turn, generate the caption using only the segments shown so far. DO NOT use or assume any information from future segments. Process all segments in chronological order. Never infer from or refer to any future segment. The annotation process must remain strictly causal and follow the chronological order of the segments.

# Task preview

Complete the task in the following three consecutive phases:

## Phase 1: Process the First Segment
Read the first **segment** and generate the following outputs for the segment:
1. `Style`: The overall visual style of the entire video, selected from the predefined style list.
2. `perspective_view`: The viewpoint of the video, selected from the predefined viewpoint list.
3. `subject_list`: The primary active subjects appearing in this segment. There may be zero, one, or multiple subjects. For each subject, provide a concise description of its attributes.
4. `visual_description_long`: A comprehensive description of the visual content of the current segment, focusing on the environment, background, other objects, and camera motion. It must NOT contain main subject actions.
5. `contained_actions`: All actions and state changes of the main subjects in this segment, ordered strictly by time. For each action, provide its exact start time, end time, and an action description referencing main subjects only by subject tokens.

## Phase 2: Process Each Subsequent Segment
For each subsequent **segment** provided in the following turns:
1. **Analyze the Delta Between Segments**: Describe the visual changes in the current segment compared to the previous segment (`description_change`).
2. **Cross Segment Consistency**: Re-evaluate the overall `perspective_view` and main subjects based on the segments seen so far.
   - If new observations require corrections to the `perspective_view` or the main subjects identified in earlier segments, retroactively update and refine those descriptions accordingly.
3. **Localize and Describe Action**: Determine the camera motion and subject-related actions for the current segment.

## Phase 3: Holistic Correction & Finalization
Once all **segments** have been processed, perform a final round of holistic correction and compilation to assemble the final output:
1. **Global Constraints**: Finalize the `perspective_view`, `Style`, and the complete list of main subjects (`subject_list`) for the entire video.
2. **First Segment Check**: Verify and refine the first segment's `visual_description_long`, camera motion, and subject-related actions (in `contained_actions`).
3. **Subsequent Segment Check**: For each subsequent segment, verify and refine the `description_change`, camera motion, and subject-related actions (in `contained_actions`).

# JSON Video Caption Format

## Perspective — `perspective_view`

Choose exactly one of the following values:

- `first-person`
- `second-person`
- `third-person follow`
- `third-person observer`

Determine `perspective_view` from the dominant visual content of the complete video and the relationship between the camera and the entity receiving the video's primary visual attention.

### Core Definitions

- **Filmer**: The camera itself, or the person, character, object, or agent carrying, controlling, or operating the camera.
- **Filmed subject**: The entity that serves as the video's primary visual focus and is being recorded by the filmer.
- **Dominant visual content**: What the video focuses on for most of its duration, considering duration, framing prominence, and repeated camera attention. Do not classify the entire video from a brief appearance, temporary occlusion, or a single segment.
- **No clear focus subject**: No person, animal, vehicle, character, or other entity consistently serves as the video's visual center of attention.
- **Camera translation**: Meaningful displacement of the camera's physical or virtual position through space. For this perspective decision, minor handheld jitter, stabilization drift, or negligible displacement does not count as camera translation. Pan, tilt, roll, or zoom from an otherwise fixed camera position may still be annotated as camera motion elsewhere, but does not by itself place the video in the camera-moving branch below.
- **Approximate horizontal coupling**: The filmed subject and the camera undergo broadly consistent horizontal displacement, so their horizontal relative position or distance remains approximately stable. This is a relaxed criterion: small distance changes, framing corrections, short delays, and minor trajectory differences are allowed.

### Decision Procedure

Apply the following rules in order.

#### 1. The camera position is stationary

If the camera has no meaningful translation:

1. If the video shows the **filmer**, classify according to the visible part of the filmer:
   - If the video shows the filmer's face, output `second-person`.
   - If the video shows the filmer's limbs or body parts, output `first-person`.

2. If the video shows a **filmed subject**, output `third-person observer`.

3. If the video has **no clear focus subject**, output `third-person observer`.

#### 2. The camera position is moving

If the camera undergoes meaningful translation:

1. If the video shows the **filmer**, classify according to the visible part of the filmer:
   - If the video shows the filmer's face, output `second-person`.
   - If the video shows the filmer's limbs or body parts, output `first-person`.

2. If the video shows a **filmed subject**, compare the filmed subject's horizontal displacement with the camera's horizontal displacement:
   - If the filmed subject and camera are approximately horizontally coupled and remain roughly stationary relative to each other, output `third-person follow`.
   - For every other camera–subject motion relationship, output `third-person observer`.

3. If the video has **no clear focus subject**, output `first-person`.

### Critical Distinctions

- A filmed subject facing or looking directly at the camera is NOT sufficient evidence for `second-person`. A news presenter, performer, dancer, or speaker recorded by a stationary external camera is `third-person observer` when that person is the filmed subject rather than the filmer.
- Keeping a filmed subject near the center of the frame is NOT sufficient evidence for `third-person follow`. Centering can be produced by panning, rotating, zooming, orbiting, or cinematic tracking while the camera follows a trajectory different from the filmed subject.
- Use `third-person follow` only when the camera and filmed subject have approximately consistent horizontal displacement and maintain a broadly stable horizontal relationship.
- A camera orbiting a car, character, or other filmed subject is `third-person observer`, even when the camera continuously points toward and keeps that subject in frame.
- A moving street view, exploratory view, or scene traversal without a clear filmed subject is `first-person`.
- A stationary surveillance-like view without a clear focus subject is `third-person observer`.
- `perspective_view` is a single video-level label. Do not change it merely because the camera temporarily stops, the focus subject briefly leaves the frame, or one segment differs from the video's dominant pattern.

### Canonical Examples

- A stationary selfie-style video dominated by the filmer's face → `second-person`
- A moving selfie-style video dominated by the filmer's face → `second-person`
- A cooking or craft video dominated by the filmer's visible hands or arms → `first-person`
- A stationary news presenter or dancer looking toward the camera → `third-person observer`
- A stationary surveillance video without a clear focus subject → `third-person observer`
- A game camera moving with a character at a roughly stable relative distance → `third-person follow`
- A camera orbiting a car or using a cinematic trajectory different from the main character's trajectory → `third-person observer`
- A moving street or environment view without a clear focus subject → `first-person`

## Style — `Style`

Choose exactly one of these English style values:

1. real-world footage
2. animation/anime
3. CG
4. video game
5. software/web/app/computer screen recording
6. slideshow

Use the exact English enum in english_json. Do not explain the choice.

## Main Subjects — `subject_list`
Identify the main subjects in the video. Include only visually prominent, narratively central, or independently moving entities. Valid subject types include humans, animals, vehicles, robots, controllable agents, transforming objects, and coherent groups. Ignore minor props and incidental background elements.

Assign subject IDs consecutively in order of importance, with no gaps or duplicates:
`<|Subject1|>`, `<|Subject2|>`, `<|Subject3|>`, ...
- *Invalid examples:*
  - Gaps in the sequence: `<|Subject1|>`, `<|Subject3|>` (Do not skip `<|Subject2|>`)
  - Duplicate IDs: `<|Subject1|>`, `<|Subject1|>`, `<|Subject2|>` (Do not assign the same ID to different subjects)

Create one `subject_list` entry for each selected main subject:
- `subject_id`: Subject token in the format `<|Subject#|>`
- `display_name`: A concise subject name
- `subject_attribute`: Canonical static profile inferred from the earliest clear frame, including identity/category, appearance, clothing/equipment, initial position, posture/orientation, initially held items, and group relationship. Set `subject_attribute` to `null` if `perspective_view` is `first-person` and no body parts/equipment are visible in the video.

## Segment Caption — `segments`

The `segments` field contains a list of segment captions for the whole video. The length of this list MUST exactly match the NUMBER of pre-clipped video segments. Each video segment corresponds to exactly one entry in the `segments` list. Each segment caption is a JSON object that describes the scene (background and any object other than the main subjects), the camera motion, and the main subjects' actions within the segment.

### Segment Fields

Every entry in the `segments` list represents a single segment and must contain exactly the following fields:
- `start_time`: exact start time of the segment in seconds;
- `end_time`: exact end time of the segment in seconds;
- `visual_description_long`: caption of the FIRST segment;
- `description_change`: caption of the subsequent segments;
- `contained_actions`: a list of action entries, where each entry must contain:
  - `start_time`: exact start time of main subjects' action in "MM:SS.mmm" format;
  - `end_time`: exact end time of main subjects' action in "MM:SS.mmm" format;
  - `action_description`: the action sentence referencing subjects only by their subject tokens.

Both `visual_description_long` and `description_change` should ONLY include two sentence types described below: `Scene Sentence`, `Camera Sentence`. And `action_description` should ONLY include sentence type of `Action Sentence`.

### Scene
A **scene** defines the physical, environmental, and spatial backdrop of the segment. It covers only environmental or non-subject elements, completely independent of the main subjects. Specifically, a scene description must only cover:
- **Composition & Space**: Foreground, midground, and background arrangement, scale, spacing, orientation, depth, and occlusion.
- **Environment & Atmosphere**: Terrain, architecture, surfaces, materials, textures, colors, lighting, shadows, reflections, weather, and visibility.
- **Other Objects**: Positions, layout, orientation, states, and activities/interactions of important props or other entities (excluding the main subjects).

#### Scene Sentence
A **scene sentence** is a purely descriptive statement used to write about the scene elements defined above. It should exclude any main subject activities or camera motion. Every scene sentence must satisfy the following formatting and syntactic constraints:
- Should NOT include any Subject tokens (e.g., `<|Subject1|>`) and should NOT refer to any main subject;
- Should NOT include any camera motion or viewpoint change descriptions (which strictly belong in Camera Sentences). Should NOT use any camera motion tokens (e.g., `<Camera1>`);
- Should NOT include any names, roles, categories, pronouns, aliases, appositives, clothing-based descriptions, or implicit references that are related to any entry in `subject_list`. Should NOT use any Subject tokens (e.g., `<|Subject1|>`);
- Should NOT summarize, paraphrase, or refer to any main subject's action descriptions. Should NOT use any action tokens (e.g., `<Action1>`).

### Camera Motion
**Camera motion** refers strictly to the movement, rotation, or optical changes of the recording lens or viewpoint itself, without any physical translation of the main subjects. Only describe camera motion if it is clearly visible in the segment. When present, you must describe:
- **Movement Types**: Visible panning, tilting, tracking (dolly/push/pull), orbiting, crane/drone translation, coherent handheld translation, or zoom/framing evolution.
- **Kinematics & Reveal**: Describe the direction, speed, chronological progression, and the resulting reveal, framing, or spatial perspective changes within `visual_description_long` or `description_change`.

#### Camera Sentence
A **camera sentence** is a structured statement describing only camera movement or viewpoint changes defined above. It must exclude environmental descriptions and main-subject actions. Every camera sentence must satisfy the following formatting and syntactic constraints:
- A camera sentence must be generated only when the camera or viewpoint undergoes clearly visible and unambiguous movement or optical change. Do NOT annotate camera motion when the viewpoint remains essentially static or when the only change is minor handheld jitter, stabilization drift, negligible framing fluctuation, subject movement within a fixed frame, or an editing cut.
  - *Invalid example:* `<Camera1>The camera remains mostly still with slight handheld jitter</Camera1>.` (Minor jitter is not meaningful camera motion and should not be annotated.)
  - *Invalid example:* `<Camera1>The framing shifts slightly</Camera1>.` (A subtle or negligible framing fluctuation is insufficient.)
  - *Invalid example:* `<Camera1>The camera follows <|Subject1|> moving from left to right</Camera1>.` (Even if the camera is tracking the subject, do not mention the subject in a camera sentence.)
  - *Invalid example:* `<Camera1>The view cuts to a closer shot</Camera1>.` (An editing cut is not camera motion.)
- A camera sentence must start with `<Camera#>` as the first non-whitespace content, and end with a matching `</Camera#>` as the final content (only terminal punctuation may follow the closing tag).
  - *Valid example:* `<Camera1>The camera slowly pans from left to right, progressively revealing a wider portion of the setting</Camera1>.`
  - *Invalid examples:*
    - Missing closing tag: `<Camera1>The camera slowly pans from left to right, progressively revealing a wider portion of the setting.`
    - Unwrapped camera description: `The camera slowly pans from left to right, progressively revealing a wider portion of the setting.` (Do not describe camera motion without enclosing it in a camera tag)
- Must NOT contain any Subject tokens (e.g., `<|Subject1|>`) or main subject references.
  - *Invalid example:* `<Camera1>The camera follows <|Subject1|> across the room</Camera1>.`
- Must NOT contain any Action tokens (`<Action#>` and `</Action#>`) or be enclosed by any Action wrapper.
  - *Invalid example:* `<Camera1>The camera tracks forward as <Action1><|Subject1|> raises an arm.</Action1></Camera1>.` (Action token inside a Camera wrapper)
  - *Invalid example:* `<Action1><|Subject1|> walks forward while <Camera1>the camera pulls backward</Camera1></Action1>.` (Camera wrapper inside an Action wrapper)
- Must describe only camera behaviors or viewpoint changes without mentioning any main subject.
- Within each segment, the Camera wrapper IDs must start from `<Camera1>` and increase sequentially for each subsequent Camera Sentence, with no gaps or duplicates (i.e., `<Camera1>`, `<Camera2>`).
    - *Valid example:* `<Camera1>The camera pans slowly to the right, widening the view to reveal the doorway</Camera1>.`
- Multiple Camera Sentences may appear within one `visual_description_long` or `description_change` field when camera motion changes over time. Camera Sentences must be arranged under the same chronological order.
    - *Valid example:* `<Camera1>The camera pans left</Camera1>.` The surrounding trees remain still. `<Camera2>The camera zooms in</Camera2>.` A wooden table stands in the corner.
- Camera Sentences should be centered around camera motion. When describing camera motion, choose the following categories: Pan, Whip Pan, Nodal Pan, Tilt, Whip Tilt, Push-in, Push-out, Zoom-in, Zoom-out, Crash-zoom, Dolly-zoom, Roll, Tracking, Lateral Track / Truck / Crab, Arc, Boom / Pedestal / Jib, Dolly / Track.

### Action

An action strictly refers to behaviors, movements, or state changes related to a **main subject** from `subject_list`. Any activities, physical changes, or movements not involving a main subject are not considered as **Action**, and should be described as environmental details in a **scene sentence**.

Specifically, valid actions include:
- Actual, observable bodily or mechanical behavior, locomotion, or manipulation by a main subject;
- An interaction between a main subject and another object, the environment, or another main subject;
- A visible main subject state-change process, including posture change, starting/stopping movement, wilting, melting, changing color, glowing, fading, damage, aging, or transformation;
- A clearly visible persistent state for a time interval with no specific active process, such as remaining seated, standing, crouched, parked, or hovering.

If a dynamic action occurs during a static posture, describe the posture within that action rather than creating a separate overlapping entry. Only write a standalone posture action for intervals with no active behavior.

#### `Contained_actions` and Action Sentence

The `contained_actions` field is a list of action entries chronologically describing all main subjects' actions within the current segment. Each action entry contains exactly three sub-fields: `start_time`, `end_time`, and `action_description`. The `action_description` field consists of a single **action sentence** that describes a main subject's action using only subject tokens, enclosed within a paired XML-style wrapper:
`<Action#>Action description</Action#>.`

- An action entry must contain `start_time`, `end_time`, and `action_description` fields.
  * *Valid Example:*
    * Correct formatting:
      ```json
      {
        "start_time": "00:01.000",
        "end_time": "00:05.000",
        "action_description": "<Action1><|Subject1|> runs</Action1>."
      }
      ```
  * *Incorrect Examples to Avoid:*
    * Missing timestamp fields:
      ```json
      {
        "action_description": "<Action1><|Subject1|> runs</Action1>."
      }
      ```
    * Empty timestamp values:
      ```json
      {
        "start_time": "",
        "end_time": "",
        "action_description": "<Action1><|Subject1|> runs</Action1>."
      }
      ```

- An action sentence must start with the `<Action#>` tag and end with the `</Action#>` tag, followed only by terminal punctuation;
  - *Invalid examples:*
    - Lowercase tags: `<action1><|Subject1|> runs</action1>.`
    - Square brackets: `[Action1]<|Subject1|> runs[/Action1].`
    - Self-closing tags: `<Action1/><|Subject1|> runs.`
    - Mismatched tags: `<Action><|Subject1|> runs</Action2>.`
    - Single tag: `<Action1><|Subject1|> runs.`
    - Unwrapped action sentences: `<|Subject1|> runs across the room.`
- Do not mix different wrapper types (e.g., placing `<Camera#>` and `<Action#>` in a single sentence).
- Within the **same segment**, the Action wrapper IDs MUST start from 1 and increase sequentially with no gaps or duplicates (e.g., `<Action1>`, `<Action2>`). You must not skip any number or use duplicate Action IDs within the same segment. If multiple actions begin at the exact same time, they must be merged into a single concurrent action.
  * *Invalid Examples:*
    * Skipping numbers:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:03.000",
            "action_description": "<Action1>...</Action1>"
          },
          {
            "start_time": "00:05.000",
            "end_time": "00:09.000",
            "action_description": "<Action3>...</Action3>"
          }
        ]
      }
      ```
      (Do not skip `<Action2>`)
    * Duplicate IDs:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:03.000",
            "action_description": "<Action1>...</Action1>"
          },
          {
            "start_time": "00:04.000",
            "end_time": "00:06.000",
            "action_description": "<Action1>...</Action1>"
          },
          {
            "start_time": "00:07.000",
            "end_time": "00:10.000",
            "action_description": "<Action2>...</Action2>"
          },
        ]
      }
      ```
      (Do not repeat `<Action1>`)
- Each distinct physical process, interaction, state change, persistent-state period, and temporal interval must be described exactly once.
  * *Invalid Examples:*
    * Tagged action + untagged paraphrase:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:03.000",
            "action_description": "<Action1><|Subject1|> walks forward</Action1>. <|Subject1|> moves on foot."
          }
        ]
      }
      ```
      (Do not repeat the action outside wrappers)
    * Two tagged paraphrases:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:03.000",
            "action_description": "<Action1><|Subject1|> walks</Action1>."
          },
          {
            "start_time": "00:01.000",
            "end_time": "00:03.000",
            "action_description": "<Action2><|Subject1|> moves on foot</Action2>."
          }
        ]
      }
      ```
      (Do not duplicate the same description across different actions)
    * Specific actions + summary action:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:02.000",
            "action_description": "<Action1><|Subject1|> grasps the bottle</Action1>."
          },
          {
            "start_time": "00:02.000",
            "end_time": "00:04.000",
            "action_description": "<Action2><|Subject1|> drinks water</Action2>."
          },
          {
            "start_time": "00:01.000",
            "end_time": "00:04.000",
            "action_description": "<Action3><|Subject1|> drinks from the bottle</Action3>."
          }
        ]
      }
      ```
      (Do not add a broader action to summarize specific ones)
    * Repeated result in scene sentence:
      ```json
      {
        "visual_description_long": "Shards of glass now lie on the floor.",
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:02.000",
            "action_description": "<Action1><|Subject1|> smashes the glass</Action1>."
          }
        ]
      }
      ```
      (Do not describe the result of an action as a separate scene sentence)
- Each action sentence must describe exactly one chronological time interval, with all subject tokens and subject-related clauses completely enclosed within the `<Action#>` and `</Action#>` tags (multiple concurrent main subject actions are allowed).
- If a single main subject performs multiple actions, their timestamps MUST NOT overlap.
  * *Incorrect Example to Avoid:*
    ```json
    {
      "contained_actions": [
        {
          "start_time": "00:01.000",
          "end_time": "00:05.000",
          "action_description": "<Action1><|Subject1|> walks down the street</Action1>."
        },
        {
          "start_time": "00:03.000",
          "end_time": "00:07.000",
          "action_description": "<Action2><|Subject1|> talks on the phone</Action2>."
        }
      ]
    }
    ```
    (Do not create overlapping action entries for the same subject)

- If different main subjects perform actions, their timestamps MUST NOT overlap.
  * *Incorrect Example to Avoid:*
    ```json
    {
      "contained_actions": [
        {
          "start_time": "00:01.000",
          "end_time": "00:05.000",
          "action_description": "<Action1><|Subject1|> runs down the street</Action1>."
        },
        {
          "start_time": "00:03.000",
          "end_time": "00:07.000",
          "action_description": "<Action2><|Subject2|> walks</Action2>."
        }
      ]
    }
    ```
    (Do not allow overlapping action timestamps; split them into consecutive, non-overlapping slices)

  * *Valid Example:*
    If `<|Subject1|>` is active from `00:01.000` to `00:05.000`, and `<|Subject2|>` is active from `00:03.000` to `00:07.000`, you must split their timeline into sequential, non-overlapping actions:
    ```json
    {
      "contained_actions": [
        {
          "start_time": "00:01.000",
          "end_time": "00:03.000",
          "action_description": "<Action1><|Subject1|> runs down the street</Action1>."
        },
        {
          "start_time": "00:03.000",
          "end_time": "00:05.000",
          "action_description": "<Action2><|Subject1|> continues running while <|Subject2|> waves</Action2>."
        },
        {
          "start_time": "00:05.000",
          "end_time": "00:07.000",
          "action_description": "<Action3><|Subject2|> continues waving</Action3>."
        }
      ]
    }
    ```

- The only legal way to refer to a Subject is using Subject token inside the Action wrapper: In `action_description` of `contained_actions`, EVERY mention of, refer to, clause about, state of, position of, motion of, or interaction by a main subject MUST 1. Use only the exact corresponding `<|Subject#|>` token; and 2. Occur completely inside one paired `<Action#>...</Action#>` wrapper.
  There are no exceptions for the first mention, repeated mentions, static or persistent states, introductory sentences, comparisons, consequences, relative clauses, sentence fragments, first segment or subsequent segments.
  Never use the main subject's name, display name, role, category, species, canonical appearance, clothing-based noun phrase, pronoun, possessive, synonym, alias, appositive, collective expression, malformed token, or implicit actor. Canonical identity and appearance belong only in `display_name` and `subject_attribute`. A main subject defined in `subject_list` must remain tracked throughout the entire video across different segments; never describe that same entity as another person, animal, vehicle, hand, object, group, or role to avoid the token-and-wrapper requirement.
  - *Invalid examples:*
    * Missing Action wrapper:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:00.000",
            "end_time": "00:08.000",
            "action_description": "<|Subject1|> descends the slope."
          }
        ]
      }
      ```
      (Illegal subject reference that does not follow the token-and-wrapper requirement)
    * Natural language description inside wrapper:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:00.000",
            "end_time": "00:08.000",
            "action_description": "<Action1><|Subject1|>, the rider in blue, descends the slope</Action1>."
          }
        ]
      }
      ```
      (Repeat the description about subject in an action sentence)

- **Active Actions vs. Static Attributes**: The main subjects' active actions and state changes (e.g., removing a jacket to reveal a shirt underneath) must be described in action sentences, while their static, persistent attributes (e.g., what clothing they are currently wearing) must be in `subject_attribute`.
  * *Correct Example:*
    * Active State Change:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:03.000",
            "action_description": "<Action1><|Subject1|> removes a red jacket, revealing a blue t-shirt underneath</Action1>."
          }
        ]
      }
      ```
      (Correctly describes a dynamic state-change process inside an action sentence.)
  * *Incorrect Example to Avoid:*
    * Static Attribute:
      ```json
      {
        "contained_actions": [
          {
            "start_time": "00:01.000",
            "end_time": "00:03.000",
            "action_description": "<Action1><|Subject1|> wears a red jacket</Action1>."
          }
        ]
      }
      ```
      (Incorrectly describes static appearance/clothing in an active action sentence; this must be placed in `subject_attribute`.)

- **Number of Actions**: Each segment MUST contain a MAXIMUM of 5 Action entries.

# Action Granularity, Continuity, and Anti-Hallucination

- **Granularity & Splitting**: Merge continuous submotions serving a single atomic goal (e.g., combining reach + grip + lift as one "pickup" action). Split the action when the purpose, tool, target, main subject behavior, or temporal phase changes.
- **Physical Continuity**: Include visible transitional actions required for physical continuity (e.g., lowering, releasing, putting down, turning, stepping, reaching, grasping, and picking up). Do not create artificial transitions due to occlusion, unreferenced time gap, or ambiguous frames.
- **Anti-Hallucination**: Describe only clearly visible actions. Distinguish actual main subject movement from camera-only movement. Do not invent body parts, tools, directions, contact points, state changes, or results that are not clearly visible. When uncertain, omit unsupported details instead of guessing.
- **Timestamps & Boundaries**: Action timestamps must tightly align with the visible action. Every action must last for at least one second (sub-second actions are forbidden). Long time intervals are only allowed for strictly continuous active processes or clearly visible persistent states. If a continuous action crosses a segment boundary, split it at the boundary timestamp; the subsequent segment's actions must restart numbering from `<Action1>`.
- **Empty Action Fallback**: If no clear main subject action is visible, it is acceptable for `contained_actions` to be an empty list `[]`.
- **Action Consequences**: The visible results or consequences of a main subject's action must be described strictly inside the corresponding `action_description` (within `contained_actions`), never in `visual_description_long` or `description_change`.
  * *Correct Example:*
    ```json
    {
      "visual_description_long": "A glass stands on the wooden table.",
      "contained_actions": [
        {
          "start_time": "00:01.000",
          "end_time": "00:02.000",
          "action_description": "<Action1><|Subject1|> smashes the glass, scattering shards across the floor</Action1>."
        }
      ]
    }
    ```
    (Correctly describes the action's result within the action sentence itself.)
  * *Incorrect Example to Avoid:*
    ```json
    {
      "visual_description_long": "A glass stands on the wooden table. Shards of glass now lie on the floor.",
      "contained_actions": [
        {
          "start_time": "00:01.000",
          "end_time": "00:02.000",
          "action_description": "<Action1><|Subject1|> smashes the glass</Action1>."
        }
      ]
    }
    ```
    (Incorrectly describes the action's result in the scene description instead of the action sentence.)

#### Writing Style for Actions
Action descriptions must be highly concrete and precise. Where applicable, describe the specific body/mechanical part involved, target, starting relation, direction, trajectory, speed, rhythm, force, extent, contact mechanics, continuous submotions, endpoint, and resulting state.

Action descriptions should be as physically descriptive as possible. Whenever the exact movement is clearly visible, prefer precise, concrete verbs (such as "grasp", "press", "slide", "throw", "pull", or "kick") over abstract terms like "interact" or "engage". If the precise mechanics are blurry or ambiguous, use simpler physical verbs (such as "touch", "hold", "push", or "move") as a safe fallback.

Now that the core concepts of Scene, Camera Motion, and Action are fully defined. The following sections detail the chronological guidelines for each individual segment.

### Process the First Segment (Phase 1)
For the first segment, describe the scene (including the layout and other objects) and camera motion in the `visual_description_long` field, and place the main subject's actions strictly under the `contained_actions` field. Every sentence in `visual_description_long` must strictly be a `Scene Sentence` or a `Camera Sentence`, while every sentence in `contained_actions` must strictly be an `Action Sentence`.

#### Field Constraints
- **Segment-1 Field Setup**: For the first segment, write the scene and camera description in `visual_description_long` and set `description_change` to `null`. (Conversely, for subsequent segments, set `visual_description_long` to `null` and use `description_change` for scene changes and camera motion).
- **Word Count**: The description in `visual_description_long` must contain 80-200 English words.
- **Temporal Range**: Describe only the scene and camera motion visible within this first segment's timeframe, strictly in chronological order. Do not refer to or use any information from subsequent segments.
- **Main Subject Actions**: Write all actions and state changes of the main subjects strictly inside the `contained_actions` list, leaving `visual_description_long` entirely free of any main subject action descriptions.

#### Descriptive Dimensions
Your description in `visual_description_long` must comprehensively cover all applicable aspects of the visual scene, strictly excluding main subject actions:
- **Composition & Space**: Foreground, midground, and background arrangement, scale, spacing, orientation, depth, and occlusion.
- **Environment & Atmosphere**: Terrain, architecture, surfaces, materials, textures, colors, lighting, shadow, reflection, weather, and visibility.
- **Other Objects**: The positions, layouts, states, and object-only interactions of important props and other objects.
- **Framing & Camera Motion**: The framing, viewpoint state, and any visible camera motion.

Your description in each `action_description` (under `contained_actions`) must comprehensively cover the main subject's behaviors and states:
- **Main Subjects & Actions**: Every main subject's visible posture/state, physical action, interaction, locomotion, state change, chronological progression, and any visible consequences.

#### Sentence Constraints
- Any sentence describing the background or **other** subjects (scene sentences) must not contain any reference to the main subjects from `subject_list`.
- Any sentence describing a main subject (including its posture or state changes) is by definition an action sentence, and should use the exact Subject token (e.g., `<|Subject1|>`) and be formatted with `<Action#>...</Action#>` XML-style wrappers. Never use a natural-language subject name, display name, role, pronoun, alias, or synonym as a shortcut, recap, comparison, or connector.

### Process Each Subsequent Segment (Phase 2)
For each subsequent segment, write the scene changes and camera motion into the `description_change` field, and place the main subject's actions strictly under the `contained_actions` field. Specifically, the scene description in `description_change` must strictly capture visual changes (the "delta") relative to the preceding segment. Conversely, camera sentences (written in `description_change`) and action sentences (written in `contained_actions`) must describe the actual events occurring within the current segment's timeframe, strictly in chronological order. Every sentence in `description_change` must strictly be a `Scene Sentence` or a `Camera Sentence`, while every sentence in `contained_actions` must strictly be an `Action Sentence`.

#### Field Constraints
- **Subsequent-Segments Field Setup**: For subsequent segments, write the scene changes and camera motion in `description_change` (setting `visual_description_long` to `null`) and the main subject's actions in `contained_actions`. (Conversely, for the first segment, set `description_change` to `null` and use `visual_description_long` for the scene and camera description).
- **Word Count**: There is no fixed word count constraint for `description_change`, describe the complete visible scene changes and camera motion exhaustively.
- **Temporal Range**: Describe only the scene changes (relative to the previous segment) and the camera motion occurring within this segment's timeframe, strictly in chronological order. Do not refer to or use any information from subsequent segments.
- **Main Subject Actions**: Write all actions and state changes of the main subjects for this subsequent segment strictly inside the `contained_actions` list, leaving `description_change` entirely free of any main subject action descriptions.

#### Descriptive Dimensions
Your description in `description_change` must comprehensively cover the scene changes (relative to the preceding segment) and the camera motion within this segment's timeframe, strictly excluding main subject actions:
- **Scene & Environment Deltas**: Any changes in the scene, environment, background layout, lighting, shadow, weather, and visibility. State explicitly what changed and what it changed into (do not repeat the full unchanged prior state merely to add length).
- **Other Objects Deltas**: Any changes in positions, states, layouts, or object-only activities/interactions of important props or other-objects.
- **Framing & Camera Motion**: Every visible camera motion, framing change, or viewpoint state occurring within this segment's timeframe.

Your description in each `action_description` (under `contained_actions`) must comprehensively cover the main subject's behaviors and states:
- **Main Subjects & Actions**: Every main subject's visible posture/state, physical action, interaction, locomotion, state change, chronological progression, and any visible consequences.

#### Sentence Constraints
- The description in `description_change` must begin exactly with the required prefix: `"Compared to the previous segment, "`.
- The first complete sentence must strictly be a subject-free **scene sentence** describing only the background or scene. Since all main subject actions belong strictly to `contained_actions`, no Subject tokens or action descriptions may ever appear in `description_change`.
  - *Valid example:* `Compared to the previous segment, the background remains unchanged.`
  - *Invalid example:* `Compared to the previous segment, <|Subject1|> walks down the street.` (Do not place any Subject tokens or action descriptions inside `description_change`.)
- If only main subject behavior changes while the scene remains unchanged, use this exact first sentence: `"Compared to the previous segment, the visible scene, background, and other-object layout remain unchanged."`
- Any action sentence inside `contained_actions` describing a main subject (including its posture or state changes) must use the exact Subject token (e.g., `<|Subject1|>`) and be formatted with `<Action#>...</Action#>` XML-style wrappers. Never use a natural-language subject name, display name, role, pronoun, alias, or synonym as a shortcut, recap, comparison, or connector.
