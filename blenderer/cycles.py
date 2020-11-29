from utilities import formatted_time

import bpy


def render_rgb(output_directory="."):
    """Render an RGB image with Cycles into the output directory.

    The curren time is appended to the rendered image so that
    each render has a unique filename.
    """
    bpy.context.scene.render.filepath = "{}/rgb_{}.png" .format(output_directory, formatted_time())
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)
