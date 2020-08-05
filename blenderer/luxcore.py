import bpy

from utilities import formatted_time


def render_luxcore_rgb(output_directory: str="."):
    """Render an RGB image using the given engine into the output directory.

    Notes
    -----
    Choices for config device are 'CPU' or 'OPENCL'.
    Choices for config engine are 'BIDIR' or 'PATH'.
    Choices for config sampler are 'SOBEL', 'METROPOLIS', or 'RANDOM'.

    The current time is appended to the rendered image so that
    each render has a unique filename.
    """
    bpy.context.scene.render.filepath = "{}/rgb_{}.png" .format(output_directory, formatted_time())
    bpy.context.scene.render.engine = 'LUXCORE'
    bpy.context.scene.luxcore.config.device = 'CPU'
    bpy.context.scene.luxcore.config.engine = 'BIDIR'
    bpy.context.scene.luxcore.config.sampler = 'METROPOLIS'
    bpy.context.scene.luxcore.denoiser.enabled = True
    bpy.context.scene.luxcore.denoiser.type = 'OIDN'
    bpy.context.scene.luxcore.halt.enable = True
    bpy.context.scene.luxcore.halt.use_time = True  # can also use_samples instead
    bpy.context.scene.luxcore.halt.time = 60  # can use samples instead

    bpy.ops.render.render(write_still=True)
