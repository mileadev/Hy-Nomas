"""English-only caption output preserves timing and subject identity."""

import json
from pathlib import Path

import pytest

from captioning_harness.prepare_sft import validate_final

ROOT = Path(__file__).resolve().parents[2]


def valid_caption():
    return {
        "english_json": {
            "perspective_view": "third-person observer",
            "Style": "real-world footage",
            "subject_list": [{
                "subject_id": "<|Subject1|>",
                "display_name": "actor",
                "subject_attribute": "brown jacket",
            }],
            "segments": [{
                "start_time": "00:00.000",
                "end_time": "00:05.000",
                "visual_description_long": "A sunlit street",
                "description_change": None,
                "contained_actions": [{
                    "start_time": "00:00.000",
                    "end_time": "00:05.000",
                    "action_description": "<Action1><|Subject1|> walks</Action1>",
                }],
            }],
        },
    }


def test_english_caption_validates():
    validate_final(valid_caption(), [{"start_sec": 0.0, "end_sec": 5.0}])


def test_bilingual_key_is_rejected():
    caption = valid_caption()
    caption["chinese_json"] = caption["english_json"]
    with pytest.raises(ValueError, match="english_json"):
        validate_final(caption, [{"start_sec": 0.0, "end_sec": 5.0}])


def test_action_out_of_bounds_is_rejected():
    caption = valid_caption()
    caption["english_json"]["segments"][0]["contained_actions"][0]["end_time"] = "00:06.000"
    with pytest.raises(ValueError, match="timeline"):
        validate_final(caption, [{"start_sec": 0.0, "end_sec": 5.0}])


def test_prompt_examples_are_english_only():
    path = ROOT / "captioning_harness/prompts/prompt_0725_icl2.md"
    data = path.read_text(encoding="utf-8")
    assert "chinese_json" not in data
    for part in data.split("~~~json")[1:]:
        document = json.loads(part.split("~~~", 1)[0].strip())
        assert set(document) == {"english_json"}
