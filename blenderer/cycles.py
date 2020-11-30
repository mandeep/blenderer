import bpy

try:
    from utilities import formatted_time
except ImportError:
    from datetime import datetime
    def formatted_time():
        return datetime.now().isoformat(timespec="milliseconds")


def render_rgb(output_directory="."):
    """Render an RGB image with Cycles into the output directory.

    The curren time is appended to the rendered image so that
    each render has a unique filename.
    """
    bpy.context.scene.render.filepath = "{}/rgb_{}.png" .format(output_directory, formatted_time())
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)
