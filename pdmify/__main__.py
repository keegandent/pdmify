import argparse
import pathlib as pl
from concurrent.futures import ProcessPoolExecutor as PoolExecutor
from concurrent.futures import wait
from uu import Error

import h5py as h5
import numpy as np
import soundfile as sf
from numba import njit
from tqdm import tqdm

USING_CUPY = True
try:
    import cupy as cp
    from cupyx.scipy.signal import resample
except Error:
    USING_CUPY = False
    from scipy.signal import resample

INP_FILE_EXTENSIONS = [".wav", ".flac"]


@njit
def delta_sigma(x):
    delta = np.zeros_like(x[0])
    for i in range(x.shape[0]):
        sigma = x[i] - delta
        for j in range(x.shape[1]):
            x[i, j] = 1 if sigma[j] > 0 else -1
        delta = x[i] - sigma
    return x


def process_file(
    inpf: pl.Path, outf: pl.Path, pdm_freq: float, force_mono: bool = False
) -> None:
    with open(inpf, "rb") as f:
        data, sample_rate = sf.read(f, always_2d=True)
    if USING_CUPY:
        # lowers needless VRAM usage
        data = cp.asarray(data, dtype=cp.float32)
    if force_mono:
        data = data.mean(axis=-1)

    data = resample(
        data,
        int(
            np.ceil(
                (data.shape[0] * pdm_freq / sample_rate),
            )
        ),
    )
    if USING_CUPY:
        data = cp.asnumpy(data)
    data = delta_sigma(data)

    with h5.File(str(outf.absolute()), "w") as f:
        f.create_dataset("pdm", data=data, compression="gzip")


def main():
    parser = argparse.ArgumentParser(
        prog="pdmify", description="Convert PCM audio files to PDM"
    )
    parser.add_argument("target", type=pl.Path, help="Audio file or directory path")
    parser.add_argument(
        "-k",
        dest="clock_khz",
        type=float,
        default=3072,
        help="PDM Clock Frequency (kHz), defaults to 3072",
    )
    parser.add_argument(
        "-o",
        dest="output",
        type=pl.Path,
        help="HDF5 file or directory path (defaults to target path)",
    )

    args = parser.parse_args()

    if args.target.is_file():
        assert args.target.suffix in INP_FILE_EXTENSIONS
        inp_files = [args.target]
        inp_root = args.target.parent
    else:
        inp_root = args.target
        inp_files = []
        [inp_files.extend(inp_root.rglob("*" + ext)) for ext in INP_FILE_EXTENSIONS]

    singleton_out = False
    if args.output:
        if args.output.suffix == "":
            out_root = args.output
        elif args.output.suffix == ".h5" and args.target.is_file():
            out_root = args.output.parent
            singleton_out = True
        else:
            raise RuntimeError(
                "Output must be a directory name or HDF5 filename:" f' "{args.output}"'
            )
    else:
        out_root = inp_root

    with (
        PoolExecutor(4) as executor,
        tqdm(total=len(inp_files), unit="file") as progress,
    ):
        futures = []
        for inpf in inp_files:
            if singleton_out:
                outf = args.output
            else:
                outf = pl.Path(
                    str(out_root.joinpath(inpf.relative_to(inp_root)).with_suffix(""))
                    + "_pdm"
                ).with_suffix(".h5")
            outf.parent.mkdir(parents=True, exist_ok=True)
            # process_file(inpf, outf, args.clock_khz * 1000)
            # progress.update()
            future = executor.submit(process_file, inpf, outf, args.clock_khz * 1000)
            future.add_done_callback(lambda _: progress.update())
            futures.append(future)
        wait(futures)


if __name__ == "__main__":
    main()
