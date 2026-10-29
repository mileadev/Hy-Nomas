# English Caption Examples

Two structural examples for final-turn English captions, subject/action/camera tokens and segment boundaries. Do not infer any content about the current video from these examples.

## Example 1

~~~json
{
  "english_json": {
    "perspective_view": "third-person observer",
    "Style": "real-world footage",
    "subject_list": [
      {
        "subject_id": "<|Subject1|>",
        "display_name": "adult handling green stems",
        "subject_attribute": "Light-skinned forearms and hands emerging from a black long-sleeved garment; face and body remain outside the frame."
      }
    ],
    "segments": [
      {
        "start_time": "00:00.000",
        "end_time": "00:12.680",
        "visual_description_long": "A tight close-up presents the interior of and the space immediately above a large, pale white plastic container. A dark, irregular heap of leafy plant material rests out of focus in the lower-left corner. A black horizontal structure occupies the upper-left background, while a blurred blue-gray area appears intermittently along the right edge. Several short green stems with smooth outer surfaces, pale fibrous interiors, and jagged split ends fill the central foreground. Soft, natural-looking illumination and shallow depth of field emphasize the torn fibers and fine surface textures. <Camera1>The externally positioned camera maintains a slightly elevated side angle, with subtle handheld drift, minor focus softness, and no major reframing</Camera1>. Pale strips become exposed along the split ends, while the dark heap remains stationary in the background. Multiple stems now display pointed, splintered tips and light-colored interiors beneath their green surfaces. The bundle becomes more compact, with shortened green shafts projecting in several directions. Several upright green ends and pale torn slivers remain visible above the container as the close-up concludes.",
        "description_change": null,
        "contained_actions": [
          {
            "start_time": "00:00.000",
            "end_time": "00:03.000",
            "action_description": "<Action1><|Subject1|> holds several green stems, pinches loose outer layers, bends individual pieces, and separates them above the container</Action1>."
          },
          {
            "start_time": "00:03.000",
            "end_time": "00:06.000",
            "action_description": "<Action2><|Subject1|> grips separate stems, pulls away fibrous coverings, rotates the pieces, and gathers the stripped sections into a small bundle</Action2>."
          },
          {
            "start_time": "00:06.000",
            "end_time": "00:09.500",
            "action_description": "<Action3><|Subject1|> aligns the bundle, transfers pieces between grips, and repeatedly plucks or tears away thin dangling fibers</Action3>."
          },
          {
            "start_time": "00:09.500",
            "end_time": "00:12.680",
            "action_description": "<Action4><|Subject1|> lifts a short piece, returns it to the bundle, pinches another split end, and continues rearranging and cleaning the remaining stems</Action4>."
          }
        ]
      }
    ]
  }
}
~~~

## Example 2

~~~json
{
  "english_json": {
    "perspective_view": "third-person observer",
    "Style": "real-world footage",
    "subject_list": [
      {
        "subject_id": "<|Subject1|>",
        "display_name": "protective-suited operator",
        "subject_attribute": "An adult-sized operator wearing a bulky olive-green protective suit with a padded hood, rounded helmet, clear face visor, dark gloves, black straps, and an attached hose or cable, initially standing beside a raised planting bed and holding a long green-and-black pole toward inspection equipment."
      },
      {
        "subject_id": "<|Subject2|>",
        "display_name": "younger GATE officer",
        "subject_attribute": "A younger adult man wearing a black cap with yellow GATE lettering, a fitted black short-sleeved shirt, dark camouflage trousers, black boots, a duty belt, and an earpiece, initially standing in a sunlit parking lot beside another GATE officer."
      },
      {
        "subject_id": "<|Subject3|>",
        "display_name": "older GATE officer with microphone",
        "subject_attribute": "An older adult man with short gray hair wearing a black cap with yellow GATE lettering, a black armored vest marked GATE over a dark camouflage uniform, and black boots, initially standing beside the younger officer while holding a logo-marked handheld microphone."
      }
    ],
    "segments": [
      {
        "start_time": "00:00.000",
        "end_time": "00:08.000",
        "visual_description_long": "A sunlit outdoor dirt area lies beside a pale beige perimeter wall topped with coils of wire. A faded rectangular notice or emblem is mounted on the wall. Tree trunks and a raised planting bed occupy the shaded left side, while dry leaves, stones, twigs, and exposed pipes cover the uneven ground. Strong sunlight casts sharply defined shadows across the wall and soil. The pole extends diagonally toward a compact mechanical assembly positioned before a black rectangular panel. <Camera1>The handheld camera moves forward and pans right from a medium view, following the pole toward the equipment and gradually narrowing the composition</Camera1>. The handled panel bears white “VIDISCO” and “BlazeX” markings, four corner guides, and a central crosshair. A metal mechanism with several narrow hanging components stands immediately before the panel on thin supports and a white padded base. A curved cable runs from the panel area toward the right edge. <Camera2>The camera pushes into a close view of the pole tip, mechanical assembly, and marked panel with slight handheld shake</Camera2>. A small olive-colored boxlike device with a dark circular front, a red top button, yellow markings, and a short cable becomes visible on the ground in the lower foreground. Long shadows stretch across the dirt around the device and panel. <Camera3>The camera then eases backward and slightly left, widening to include more of the pole and the foreground device while retaining the panel and assembly on the right</Camera3>.",
        "description_change": null,
        "contained_actions": [
          {
            "start_time": "00:00.000",
            "end_time": "00:02.000",
            "action_description": "<Action1><|Subject1|> stands in the left foreground in a bulky olive-green protective suit with a padded hood, helmet, clear visor, dark gloves, black straps, and an attached hose or cable while gripping a long green-and-black pole with both hands</Action1>."
          },
          {
            "start_time": "00:02.000",
            "end_time": "00:08.000",
            "action_description": "<Action2><|Subject1|> keeps the far end of the pole aligned with the mechanical assembly and makes small, controlled positioning adjustments without releasing the two-handed grip</Action2>."
          }
        ]
      },
      {
        "start_time": "00:08.000",
        "end_time": "00:21.000",
        "visual_description_long": null,
        "description_change": "Compared to the previous segment, the view leaves the wall-side inspection setup and opens onto a paved parking lot marked with yellow lines, rows of dark and light-colored cars, leafy trees, several distant uniformed figures, and a large pale building under intense backlighting and green lens flare. <Camera1>The handheld camera pans quickly left along the pole, passes the raised planting bed and building corner, and swings into the adjoining parking lot</Camera1>. The panel and small ground device leave the frame as parked vehicles fill the foreground and background. <Camera2>The camera advances across the lot with noticeable shake and strong flare from the low sun behind the distant building</Camera2>. <Camera3>The camera pushes from a wide parking-lot view into a medium waist-up two-shot</Camera3>. <Camera4>The camera closes in further and shifts slightly right as lens-flare spots cross the frame</Camera4>.",
        "contained_actions": [
          {
            "start_time": "00:08.000",
            "end_time": "00:10.000",
            "action_description": "<Action1><|Subject1|> continues gripping the long pole with both hands while keeping the far end directed toward the inspection panel, then disappears from view as the framing turns away</Action1>."
          },
          {
            "start_time": "00:10.000",
            "end_time": "00:14.000",
            "action_description": "<Action2><|Subject2|> stands in a black GATE cap, fitted black shirt, camouflage trousers, duty belt, and earpiece while speaking and pointing forward with a partially extended right hand; <|Subject3|> stands alongside in a black GATE cap, dark camouflage uniform, and marked armored vest while raising a logo-marked microphone toward <|Subject2|></Action2>."
          },
          {
            "start_time": "00:14.000",
            "end_time": "00:17.500",
            "action_description": "<Action3><|Subject2|> continues speaking and alternates between a pinched-finger gesture and an open hand near chest height, while <|Subject3|> holds the microphone steady and watches attentively</Action3>."
          },
          {
            "start_time": "00:17.500",
            "end_time": "00:21.000",
            "action_description": "<Action4><|Subject2|> extends the right arm fully across the foreground to indicate an area off-screen right, then begins drawing the arm back while continuing smaller explanatory gestures; <|Subject3|> turns the gaze in the indicated direction and keeps the microphone positioned between <|Subject2|> and <|Subject3|></Action4>."
          }
        ]
      },
      {
        "start_time": "00:21.000",
        "end_time": "00:35.969",
        "visual_description_long": null,
        "description_change": "Compared to the previous segment, the visible scene, background, and other-object layout remain materially unchanged. <Camera1>The handheld camera holds a close two-shot with minor lateral drift and persistent green lens flare from the upper-left sunlight</Camera1>. <Camera2>The framing subtly pans and widens to the right, exposing more space between the parked cars</Camera2>. <Camera3>The camera edges closer on the microphone side of the two-shot while preserving the parking-lot activity in the right background</Camera3>.",
        "contained_actions": [
          {
            "start_time": "00:21.000",
            "end_time": "00:24.500",
            "action_description": "<Action1><|Subject2|> continues speaking with small pinched-finger and open-hand gestures near chest height while looking off-screen right, as <|Subject3|> keeps the microphone directed toward <|Subject2|> and watches the same area</Action1>."
          },
          {
            "start_time": "00:24.500",
            "end_time": "00:27.500",
            "action_description": "<Action2><|Subject2|> sweeps the right hand outward once more and then lowers it, while <|Subject3|> shifts attention farther right and draws the microphone closer to the chest</Action2>."
          },
          {
            "start_time": "00:27.500",
            "end_time": "00:30.500",
            "action_description": "<Action3><|Subject1|> enters from the right background and walks leftward while carrying the long pole horizontally with both hands; <|Subject2|> pauses the larger gestures and looks toward the activity, while <|Subject3|> turns toward <|Subject2|> and raises the microphone to begin responding</Action3>."
          },
          {
            "start_time": "00:30.500",
            "end_time": "00:33.000",
            "action_description": "<Action4><|Subject3|> speaks into the microphone and gestures with the free hand, alternating between an open palm and a downward indication toward the lot; <|Subject2|> faces <|Subject3|> and listens; <|Subject1|> stops in the right background, steadies the pole horizontally, and briefly raises one hand toward the helmet or visor</Action4>."
          },
          {
            "start_time": "00:33.000",
            "end_time": "00:35.969",
            "action_description": "<Action5><|Subject3|> continues speaking, points toward the right, and finishes with a level sweeping hand motion; <|Subject2|> remains attentive with hands lowered; <|Subject1|> maintains a wide stance and makes small adjustments to the pole’s angle while holding it across the body</Action5>."
          }
        ]
      }
    ]
  }
}
~~~
