import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.image import imread
from pathlib import Path
from datetime import datetime
import argparse
import subprocess
import shutil
import sys


# ---------------------------------------------------------------------------
# ffmpeg auto-installer
# ---------------------------------------------------------------------------


def ensure_ffmpeg() -> str:
    """
    Return the path to an ffmpeg executable, installing it automatically if
    it's not already on the system PATH.

    Strategy:
      1. Check PATH — if ffmpeg is already installed, use it.
      2. Check if imageio-ffmpeg is installed and use its bundled binary.
      3. Try to pip-install imageio-ffmpeg (which ships its own ffmpeg binary).
      4. On Windows, also try winget as a last resort.
    """
    # 1. Already on PATH?
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"Found ffmpeg on PATH: {ffmpeg_path}")
        return ffmpeg_path

    # 2. imageio-ffmpeg already installed?
    ffmpeg_path = _ffmpeg_from_imageio()
    if ffmpeg_path:
        return ffmpeg_path

    # 3. Try pip-installing imageio-ffmpeg
    print("ffmpeg not found — installing imageio-ffmpeg (bundled ffmpeg binary)...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "imageio-ffmpeg"],
        )
        ffmpeg_path = _ffmpeg_from_imageio()
        if ffmpeg_path:
            return ffmpeg_path
    except subprocess.CalledProcessError:
        pass

    # 4. Windows-only: try winget
    if sys.platform == "win32" and shutil.which("winget"):
        print("Trying winget to install ffmpeg...")
        try:
            subprocess.check_call(
                ["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--silent"]
            )
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                return ffmpeg_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    print(
        "\nCould not auto-install ffmpeg.\n"
        "Please install it manually:\n"
        "  Windows : winget install --id Gyan.FFmpeg  (or https://ffmpeg.org/download.html)\n"
        "  macOS   : brew install ffmpeg\n"
        "  Linux   : sudo apt install ffmpeg\n"
        "Then re-run this script."
    )
    sys.exit(1)


def _ffmpeg_from_imageio():
    """Return the ffmpeg binary path bundled with imageio-ffmpeg, or None."""
    try:
        import imageio_ffmpeg

        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and Path(path).exists():
            print(f"Using bundled ffmpeg from imageio-ffmpeg: {path}")
            return path
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Filename parser
# ---------------------------------------------------------------------------


def parse_datetime_from_filename(filename: str) -> str:
    """Parse datetime from filename like 2026-02-19_18-33-06.jpg"""
    stem = Path(filename).stem
    try:
        dt = datetime.strptime(stem, "%Y-%m-%d_%H-%M-%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return stem


# ---------------------------------------------------------------------------
# Main animator
# ---------------------------------------------------------------------------


def animate_images(
    folder: str,
    fps: float = 4,
    extensions: tuple = (".jpg", ".jpeg", ".png", ".bmp", ".gif"),
    output: str = None,
):
    folder_path = Path(folder)
    if not folder_path.is_dir():
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    image_files = sorted(
        f for f in folder_path.iterdir() if f.suffix.lower() in extensions
    )

    if not image_files:
        print(f"No image files found in '{folder}' with extensions {extensions}")
        sys.exit(1)

    print(f"Found {len(image_files)} images — animating at {fps} FPS")

    images = [imread(str(f)) for f in image_files]
    titles = [parse_datetime_from_filename(f.name) for f in image_files]

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor("#1a1a1a")
    ax.set_facecolor("#1a1a1a")
    ax.axis("off")

    im = ax.imshow(images[0], animated=True)
    title = ax.set_title(
        titles[0],
        color="white",
        fontsize=14,
        fontweight="bold",
        pad=12,
        fontfamily="monospace",
    )
    counter_text = ax.text(
        0.98,
        0.02,
        f"1 / {len(images)}",
        transform=ax.transAxes,
        color="#aaaaaa",
        fontsize=10,
        ha="right",
        va="bottom",
        fontfamily="monospace",
    )

    plt.tight_layout()

    def update(frame_idx):
        im.set_data(images[frame_idx])
        im.set_extent([0, images[frame_idx].shape[1], images[frame_idx].shape[0], 0])
        title.set_text(titles[frame_idx])
        counter_text.set_text(f"{frame_idx + 1} / {len(images)}")
        return im, title, counter_text

    interval_ms = 1000 / fps
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(images),
        interval=interval_ms,
        blit=True,
        repeat=True,
    )

    if output:
        out_path = Path(output)
        suffix = out_path.suffix.lower()
        print(f"Saving to {out_path} ...")

        if suffix == ".gif":
            writer = animation.PillowWriter(fps=fps)
            ani.save(str(out_path), writer=writer, dpi=100)

        elif suffix == ".mp4":
            ffmpeg_path = ensure_ffmpeg()
            # Tell matplotlib exactly where the binary is
            plt.rcParams["animation.ffmpeg_path"] = ffmpeg_path
            writer = animation.FFMpegWriter(
                fps=fps,
                codec="h264",
                extra_args=["-pix_fmt", "yuv420p"],
            )
            ani.save(str(out_path), writer=writer, dpi=100)

        else:
            print(f"Unsupported output format '{suffix}'. Use .gif or .mp4")
            sys.exit(1)

        print(f"Saved: {out_path}")
        plt.close(fig)
    else:
        plt.show()

    return ani


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Animate image files in a folder using matplotlib.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Path to the folder containing image files",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=4.0,
        help="Frames per second for the animation",
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        default=[".jpg", ".jpeg", ".png", ".bmp", ".gif"],
        help="Image file extensions to include",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Save animation to this file (e.g. out.gif or out.mp4)",
    )

    args = parser.parse_args()
    animate_images(
        args.folder, fps=args.fps, extensions=tuple(args.ext), output=args.output
    )
