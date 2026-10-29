#!/usr/bin/env bash
# Local wrapper around upstream gateway / GPU worker launcher.
set -euo pipefail
umask 077
cd "$(dirname "$0")/../.."
: "${Hy_Nomas_Model_Path:?Set Hy_Nomas_Model_Path to downloaded weights}"
mode="${NOMAS_RUN_MODE:-low-mem}"
python3 scripts/local/doctor.py --require-model-files
save_path="${NOMAS_SAVE_PATH:-./outputs/seg_ar_demo}"
case "${mode}" in
  low-mem)
    : "${CUTLASS_PATH:?Set CUTLASS_PATH for low-memory FP8 decoding}"
    exec bash scripts/inference/start_seg_ar_demo.sh \
      --single-gpu-low-mem-mode \
      --dit-weight "${Hy_Nomas_Model_Path}/DiT/distilled_int8/diffusion_pytorch_model_ema_0_995_int8.safetensors" \
      --save-path "${save_path}" \
      "model.vae.checkpoint=${Hy_Nomas_Model_Path}/VAE/PixelUMM_FT_FP8/diffusion_pytorch_model_fp8.safetensors" \
      "$@"
    ;;
  multi-gpu)
    exec bash scripts/inference/start_seg_ar_demo.sh \
      --dit-weight "${Hy_Nomas_Model_Path}/DiT/distilled/diffusion_pytorch_model_ema_0_995.safetensors" \
      --sp-size "${NOMAS_SP_SIZE:-8}" \
      --save-path "${save_path}" \
      "model.vae.checkpoint=${Hy_Nomas_Model_Path}/VAE/PixelUMM_FT/diffusion_pytorch_model.safetensors" \
      "$@"
    ;;
  *)
    echo "NOMAS_RUN_MODE must be low-mem or multi-gpu" >&2
    exit 2
    ;;
esac
