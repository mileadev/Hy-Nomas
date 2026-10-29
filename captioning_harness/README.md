# SFT Data Preparation

Prepare SFT data from local videos in three stages: **VAE Encoding → Event Segmentation → Captioning with Kimi-K3**. The final training file contains video latents, segment boundaries, and per-segment prompts.

![Local videos, VAE encoding, event segmentation, Kimi-K3 captioning, and the final SFT dataset.](../assets/sft-data-preparation.svg)

Run commands from the repository root. Download the model repository as described in [Model Assets](../README.md#model-assets) and set `Hy_Nomas_Model_Path` to that directory. The commands below reuse its value. Keep the original local videos available for segmentation and captioning.

> The diagram describes the preparation workflow. The current scripts expose separate interfaces: the VAE encoder expects existing prompts and boundaries, and the captioning command uses fixed-duration segments rather than the event-segmentation output. They do not yet implement the complete sequence above automatically.

## 1. VAE Encoding

Encode video frames with the model's 32-channel DCAE-V checkpoint. Store the unscaled BF16 bytes in `latent` and the `[C,T,H,W]` shape in `latent_shape`.

The existing encoder takes an Arrow file with local `video_path` values and the training-schema columns, including prompts and segment boundaries. For an input already containing those annotations:

```bash
export Hy_Nomas_Model_Path="${Hy_Nomas_Model_Path:-/path/to/Hy-Nomas}"

VAE_PATH="${Hy_Nomas_Model_Path}/VAE/DCAE-V/dc-ae-v-1.0-f32t4c32-bf16.pt" NUM_GPUS=8 \
  bash scripts/data_processing/vae_latent_encoding.sh \
  /path/to/videos.arrow /path/to/videos_vae.arrow
```

The launcher supports one node, one input Arrow, and one output Arrow. Set `NUM_GPUS=1` for one GPU, `GPU_IDS=0,1` to select logical devices within `CUDA_VISIBLE_DEVICES`, or `PREFETCH=0` to disable CPU prefetch. The checkpoint can also be supplied with `--vae-checkpoint`.

To encode only the first row before processing the full dataset:

```bash
export Hy_Nomas_Model_Path="${Hy_Nomas_Model_Path:-/path/to/Hy-Nomas}"

VAE_PATH="${Hy_Nomas_Model_Path}/VAE/DCAE-V/dc-ae-v-1.0-f32t4c32-bf16.pt" NUM_GPUS=1 \
  bash scripts/data_processing/vae_latent_encoding.sh \
  /path/to/videos.arrow /path/to/videos_vae_smoke.arrow --rows 0
```

Omit `--rows` to process every row. The encoder preserves input row order and schema, validates and preserves rows with existing latents, and writes the final Arrow only after every row validates. Use a new output path for each run; existing outputs are not overwritten.

### Sampling and Input Requirements

- Frames are sampled at 24 FPS using the nearest source frame, then center-cropped to 704×1280 by default. Set `HEIGHT` and `WIDTH` to change the crop; both must be multiples of 32 and fit inside the source frames. Images are not resized or padded.
- The sampled frame count is rounded down to a multiple of four, dropping at most three tail frames. Pixel normalization is performed in FP32 before casting to BF16; the default crop produces latent spatial dimensions of 22×40.
- Input prompts and segment boundaries must use the 24-FPS timeline. Internal boundaries and prompts are preserved; the final boundary is updated to the encoded latent length. A different boundary FPS is rejected.
- Pre-VAE rows must set `has_camera=false` and both camera payloads to null. Calibrated camera trajectories require a transform matching the image preprocessing before they can be attached to the training data.

### Tests

Run the VAE encoding checks from the repository root:

```bash
python -m pytest -q scripts/data_processing/test_vae_latent_encoding.py
```

## 2. Event Segmentation

Use Kimi-K3 to identify continuous events and their contained actions. Start the [Kimi-K3 service](#start-kimi-k3) before running this step.

```bash
python3 captioning_harness/prepare_sft.py segment \
  --input /path/to/videos_vae.arrow \
  --output /path/to/videos_segmented.arrow \
  --model kimi-k3 \
  --api-base http://first-node-hostname:30000/v1
```

The input needs a local `video_path` column and an absent or entirely null `segments` column. Existing latent columns are preserved. The command reads the original videos and writes `segments` as JSON containing event start/end times, labels, descriptions, and contained actions. Relative video paths resolve against the input Arrow directory.

Segmentation samples at 2 FPS by default for visual analysis; this does not change the VAE frame rate. Events must cover the clip continuously from start to end. Failed rows retain null `segments` and are listed in `<output>.failures.jsonl`.

## 3. Captioning with Kimi-K3

Kimi-K3 describes each segment in successive visual chat turns, then produces a validated English-only summary. English per-segment prompts contain scene context, subjects, visual descriptions, and actions.

### Start Kimi-K3

Install an SGLang build compatible with your Kimi-K3 checkpoint. The example uses four nodes with eight GPUs each. Run on every node with its own `K3_NODE_RANK`; all nodes share `K3_DIST_INIT_ADDR`.

```bash
export K3_MODEL_PATH=/path/to/kimi-k3
export K3_NNODES=4 K3_TP_SIZE=8 K3_PP_SIZE=4 K3_EP_SIZE=8
export K3_DIST_INIT_ADDR=first-node-hostname:50000
export K3_NODE_RANK=0  # Set 1, 2, or 3 on the other nodes.
bash captioning_harness/serve_k3.sh
```

Adjust the topology for your hardware. If authentication is enabled, set `K3_API_KEY` on the server and `CAPTION_API_KEY` for the annotation commands.

### Run Captioning

The current captioning entry point accepts one local video or a directory of videos. It creates fixed 4-second segments and does not consume `videos_segmented.arrow` yet:

```bash
python3 captioning_harness/prepare_sft.py annotate \
  --input /path/to/local_videos \
  --annotations /path/to/annotations.jsonl \
  --model kimi-k3 \
  --api-base http://first-node-hostname:30000/v1 \
  --fps 24
```

This command center-crops to 512×512 and accepts videos up to 32 seconds by default. It saves validated captions and prompts to JSONL and skips completed records on rerun. Review segment descriptions and action timestamps before training.

To produce a training file from this command's JSONL, use the existing `pack` entry point. It encodes the annotated frames again; it does not reuse the latents from step 1:

```bash
export Hy_Nomas_Model_Path="${Hy_Nomas_Model_Path:-/path/to/Hy-Nomas}"

python3 captioning_harness/prepare_sft.py pack \
  --annotations /path/to/annotations.jsonl \
  --vae-checkpoint "${Hy_Nomas_Model_Path}/VAE/DCAE-V/dc-ae-v-1.0-f32t4c32-bf16.pt" \
  --output /path/to/train.arrow
```

Keep `dataset.fps` equal to the annotation frame rate. The commands above use 24 FPS to match `sft.yaml`; if using `annotate`'s default 16 FPS, set `dataset.fps=16` when training.

For camera-conditioned samples, pass `--camera-dir /path/to/cameras` to `pack`. Each `<sample_id>.npz` must contain normalized FP32 `camera_extrinsics` (`[F,4,4]`) and `camera_intrinsics` (`[F,3,3]`) matching the sampled frames and image preprocessing. Without camera data, samples use `has_camera=false`.

After preparing the training file, create the packing plan below, then follow [Training and Merging](../README.md#training-and-merging).

## Offline Sequence Packing

Build an offline sequence-packing plan from one encoded SFT Arrow or Parquet
file:

```bash
python scripts/data_processing/build_sft_packing_plan.py \
  --input /path/to/train.arrow \
  --output /path/to/train_packing.json \
  --max-seq-len 360000 \
  --seed 42
```

The script reads `latent_shape` and writes sample-index groups to one JSON file.
It does not rewrite or split the input dataset, and an existing output is never
overwritten. Every input row appears exactly once, and each group stays within
`--max-seq-len`.

- By default, groups are built with First-Fit Decreasing.
- `--num-groups N` requests exactly N groups with balanced token counts. N must
  not exceed the sample count and must provide enough capacity; the script
  fails if it cannot construct a valid plan.
- `--patch-size PT PH PW` sets the latent patch dimensions, defaulting to
  `1 1 1`. Token cost is `(T / PT) * (H / PH) * (W / PW)`; latent dimensions
  must be divisible by the patch dimensions. Text tokens are not counted.

Enable the plan in the training config:

```yaml
dataset:
  data_file: /path/to/train.arrow
  token_packing: true
  token_packing_sorted_groups_path: /path/to/train_packing.json
  token_packing_shuffle_chunks_each_epoch: false
```

Use the same dataset and row order that were used to build the plan. The
training sampler distributes groups across data-parallel ranks and drops an
incomplete final set of groups. To cover every sample each epoch, choose
`--num-groups` as a multiple of the data-parallel degree, with at least one
group per rank and sufficient total token capacity.

## Training Data Format

Pass exactly one Arrow IPC file (`.arrow`) or one Parquet file (`.parquet`) as `dataset.data_file`. Both use the same row schema:

| Column | Type | Meaning |
|:---|:---|:---|
| `latent` | binary | Unscaled VAE latent, contiguous little-endian BF16 bytes in `[C,T,H,W]` order |
| `latent_shape` | list of 4 integers | `[C,T,H,W]` |
| `prompts` | list of strings | One nonempty text prompt per segment; at least one segment |
| `segment_boundaries` | list of integers | Segment boundaries in latent frames, starting at 0 and ending at `T` |
| `camera_extrinsics` | binary | Normalized camera extrinsics, contiguous little-endian FP32 bytes in `[(T-1)*4+1,4,4]` order |
| `camera_intrinsics` | binary | Normalized camera intrinsics, contiguous little-endian FP32 bytes in `[(T-1)*4+1,3,3]` order |
| `has_camera` | boolean, optional | `false` for a text-only row; both camera payloads may then be null |
| `sample_id` | string, optional | Identifier used in logs |

`segment_boundaries` must be strictly increasing and have one more entry than `prompts`. The latent must use the 32-channel DCAE-V (`dcae-v-f32t4c32`) associated with the model weights. The file contains the latent payload itself; video paths, latent paths, directories, manifests, and network URLs cannot substitute for these embedded payloads. When token packing is enabled, supply the separate packing plan through `dataset.token_packing_sorted_groups_path`; see [Offline Sequence Packing](#offline-sequence-packing).

Camera tensors must use the normalization associated with the released camera-control checkpoint. The public training config uses `extrinsics_attn`; text-only rows set `has_camera=false` and null camera payloads. No external trajectory or pose file is read at training time.
