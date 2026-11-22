#!/usr/bin/env python3
"""Isolated HiDream-I1 Diffusers backend; run in its own GPU environment."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-type", choices=("full",), required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    import torch
    from diffusers import HiDreamImagePipeline
    from transformers import LlamaForCausalLM, PreTrainedTokenizerFast

    llama = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    tokenizer = PreTrainedTokenizerFast.from_pretrained(llama)
    encoder = LlamaForCausalLM.from_pretrained(
        llama, output_hidden_states=True, output_attentions=True, torch_dtype=torch.bfloat16
    )
    pipe = HiDreamImagePipeline.from_pretrained(
        "HiDream-ai/HiDream-I1-Full",
        tokenizer_4=tokenizer, text_encoder_4=encoder, torch_dtype=torch.bfloat16,
    ).to("cuda")
    image = pipe(
        args.prompt, height=1248, width=832, guidance_scale=5.0,
        num_inference_steps=50, generator=torch.Generator("cuda").manual_seed(args.seed),
    ).images[0]
    image.save(args.output)


if __name__ == "__main__":
    main()
