"""Explicit, temporary single-L4 serving. Import/deploy does not run a benchmark.

Deploy with the isolated Modal CLI: modal deploy bench/modal_vllm.py
Stop after collection: modal app stop --yes cachekit-benchmark
"""

import modal

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
VLLM_VERSION = "0.31.0"
APP_NAME = "cachekit-benchmark"
PORT = 8000
COMMAND = [
    "vllm",
    "serve",
    MODEL,
    "--revision",
    REVISION,
    "--tokenizer-revision",
    REVISION,
    "--served-model-name",
    MODEL,
    "--host",
    "0.0.0.0",
    "--port",
    str(PORT),
    "--dtype",
    "bfloat16",
    "--max-model-len",
    "16384",
    "--block-size",
    "16",
    "--enable-prefix-caching",
    "--gpu-memory-utilization",
    "0.90",
    "--middleware",
    "bench.middleware.BenchmarkRoutes",
    "--disable-uvicorn-access-log",
]
image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==" + VLLM_VERSION)
    .env(
        {
            "HF_XET_HIGH_PERFORMANCE": "1",
            "VLLM_LOG_STATS_INTERVAL": "1",
            "VLLM_SERVER_DEV_MODE": "1",
        }
    )
    .add_local_python_source("bench")
)
app = modal.App(APP_NAME)


@app.server(
    image=image,
    gpu="L4",
    port=PORT,
    unauthenticated=True,
    max_containers=1,
    min_containers=0,
    scaledown_window=300,
    startup_timeout=900,
    volumes={
        "/root/.cache/huggingface": modal.Volume.from_name(
            "huggingface-cache", create_if_missing=True
        ),
        "/root/.cache/vllm": modal.Volume.from_name("vllm-cache", create_if_missing=True),
    },
)
class Server:
    @modal.enter()
    def start(self):
        import subprocess

        help_result = subprocess.run(
            ["vllm", "serve", "--help=all"], capture_output=True, text=True, check=True
        )
        missing = [
            flag for flag in COMMAND if flag.startswith("--") and flag not in help_result.stdout
        ]
        if missing:
            raise RuntimeError("Pinned server lacks required flags: " + ", ".join(missing))
        # Request logging is off by default in the pinned version. Do not enable it.
        self.process = subprocess.Popen(COMMAND)

    @modal.exit()
    def stop(self):
        import subprocess

        process = getattr(self, "process", None)
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
