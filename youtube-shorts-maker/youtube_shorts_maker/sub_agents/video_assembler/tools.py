"""Tools for VideoAssemblerAgent"""

import subprocess
import re
import tempfile
import os
from google.adk.tools.tool_context import ToolContext
import google.genai.types as types


async def assemble_video(tool_context: ToolContext) -> str:
    """Assemble final YouTube Shorts video from image and audio artifacts

    Args:
        tool_context: Tool context to access state and artifacts

    Returns:
        Information about the video assembly process
    """
    temp_files = []  # Track temporary files for cleanup

    try:
        # Read content plan from context
        content_planner_output = tool_context.state.get("content_planner_output", {})
        scenes = content_planner_output.get("scenes", [])

        if not scenes:
            return "No scenes found in content plan"

        print(f"🎬 VIDEO ASSEMBLER: Starting assembly for {len(scenes)} scenes")

        # List all available artifacts
        existing_artifacts = await tool_context.list_artifacts()

        # Find image and audio files
        image_files = []
        audio_files = []

        for artifact_name in existing_artifacts:
            if artifact_name.startswith("scene_") and artifact_name.endswith(
                "_image.jpeg"
            ):
                image_files.append(artifact_name)
            elif artifact_name.startswith("scene_") and artifact_name.endswith(
                "_narration.mp3"
            ):
                audio_files.append(artifact_name)

        # Sort by scene number
        def extract_scene_number(filename):
            match = re.search(r"scene_(\d+)_", filename)
            return int(match.group(1)) if match else 0

        image_files.sort(key=extract_scene_number)
        audio_files.sort(key=extract_scene_number)

        print(f"🖼️ Found {len(image_files)} image artifacts")
        print(f"🎵 Found {len(audio_files)} audio artifacts")

        if len(image_files) != len(scenes) or len(audio_files) != len(scenes):
            return f"Missing artifacts: Expected {len(scenes)} images and audio files, found {len(image_files)} images and {len(audio_files)} audio files"

        # Load artifacts and create temporary files
        temp_image_paths = []
        temp_audio_paths = []

        for i, (image_name, audio_name) in enumerate(zip(image_files, audio_files)):
            # Load and save image artifact
            print(f"📂 Loading image artifact: {image_name}")
            image_artifact = await tool_context.load_artifact(filename=image_name)
            if image_artifact and image_artifact.inline_data:
                temp_image = tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False)
                temp_image.write(image_artifact.inline_data.data)
                temp_image.close()
                temp_image_paths.append(temp_image.name)
                temp_files.append(temp_image.name)
                print(f"💾 Created temp image: {temp_image.name}")
            else:
                return f"Failed to load image artifact: {image_name}"

            # Load and save audio artifact
            print(f"📂 Loading audio artifact: {audio_name}")
            audio_artifact = await tool_context.load_artifact(filename=audio_name)
            if audio_artifact and audio_artifact.inline_data:
                temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_audio.write(audio_artifact.inline_data.data)
                temp_audio.close()
                temp_audio_paths.append(temp_audio.name)
                temp_files.append(temp_audio.name)
                print(f"💾 Created temp audio: {temp_audio.name}")
            else:
                return f"Failed to load audio artifact: {audio_name}"

        # Build FFmpeg command with temporary file paths
        input_args = []
        filter_parts = []

        # Add inputs for each scene
        for i, (temp_image, temp_audio) in enumerate(
            zip(temp_image_paths, temp_audio_paths)
        ):
            input_args.extend(["-i", temp_image, "-i", temp_audio])

            # Get scene duration from content plan
            scene_duration = scenes[i].get("duration", 4)  # fallback to 4 seconds

            # Create video stream that displays image for scene duration
            total_frames = int(30 * scene_duration)  # 30fps * duration in seconds
            filter_parts.append(
                f"[{i*2}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
                f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,"
                f"loop={total_frames-1}:size=1:start=0[v{i}]"
            )

            # Keep audio as-is
            filter_parts.append(f"[{i*2+1}:a]anull[a{i}]")

        # Concatenate all video and audio streams
        video_inputs = "".join([f"[v{i}]" for i in range(len(scenes))])
        audio_inputs = "".join([f"[a{i}]" for i in range(len(scenes))])
        filter_parts.append(f"{video_inputs}concat=n={len(scenes)}:v=1:a=0[outv]")
        filter_parts.append(f"{audio_inputs}concat=n={len(scenes)}:v=0:a=1[outa]")

        # Create temporary output file
        temp_output = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_output.close()
        output_path = temp_output.name
        temp_files.append(output_path)

        # Build final FFmpeg command
        ffmpeg_cmd = (
            ["ffmpeg", "-y"]
            + input_args
            + [
                "-filter_complex",
                ";".join(filter_parts),
                "-map",
                "[outv]",
                "-map",
                "[outa]",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-pix_fmt",
                "yuv420p",
                "-r",
                "30",
                output_path,
            ]
        )

        print("🔧 Executing FFmpeg command...")
        print(" ".join(ffmpeg_cmd))

        # Execute FFmpeg
        subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)

        # Save final video as artifact
        with open(output_path, "rb") as f:
            video_data = f.read()

        artifact = types.Part(
            inline_data=types.Blob(mime_type="video/mp4", data=video_data)
        )

        await tool_context.save_artifact(
            filename="youtube_short_final.mp4", artifact=artifact
        )

        total_duration = sum(scene.get("duration", 4) for scene in scenes)

        result_info = {
            "status": "success",
            "scenes_processed": len(scenes),
            "total_duration": total_duration,
            "output_file": "youtube_short_final.mp4",
            "resolution": "1080x1920",
            "format": "MP4 (H.264/AAC)",
        }

        print(f"✅ Video assembly complete! Created {total_duration}s YouTube Short")
        return str(result_info)

    except subprocess.CalledProcessError as e:
        error_info = {
            "status": "ffmpeg_error",
            "error_message": str(e),
            "stderr": e.stderr,
            "stdout": e.stdout,
        }
        print(f"❌ FFmpeg failed: {e.stderr}")
        return str(error_info)

    except Exception as e:
        error_info = {"status": "error", "error_message": str(e)}
        print(f"❌ Video assembly failed: {str(e)}")
        return str(error_info)

    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    print(f"🗑️ Cleaned up temp file: {temp_file}")
            except Exception as e:
                print(f"⚠️ Failed to cleanup {temp_file}: {e}")
