import bpy

try:
    from utilities import formatted_time
except ImportError:
    from datetime import datetime
    def formatted_time():
        return datetime.now().isoformat(timespec="milliseconds")


def render_rgb(output_directory='.', device='CPU', engine='PATH', sampler='SOBEL'):
    """Render an RGB image using the given engine into the output directory.

    Parameters
    ----------
    output_directory: str
        The directory where the rendered image is saved
    device: str
        The hardware to use to render the image
    engine: str
        The type of path tracing to perform: unidirectional or bidirectional
    sampler: str
        The sampler to use with the path tracing integrator

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
    bpy.context.scene.luxcore.config.device = device
    bpy.context.scene.luxcore.config.engine = engine

    if engine == 'BIDIR':
        bpy.context.scene.luxcore.config.bidir_path_maxdepth = 10   # eye depth
        bpy.context.scene.luxcore.config.bidir_light_maxdepth = 10  # light depth
        bpy.context.scene.luxcore.config.sampler = sampler

        if sampler == 'METROPOLIS':
            bpy.context.scene.luxcore.config.metropolis_largesteprate = 0.40
            bpy.context.scene.luxcore.config.metropolis_maxconsecutivereject = 512
            bpy.context.scene.luxcore.config.metropolis_imagemutationrate = 0.10

        bpy.context.scene.luxcore.config.use_animated_seed = True
        bpy.context.scene.luxcore.config.light_strategy = "LOG_POWER"

    bpy.context.scene.luxcore.config.path.use_clamping = False

    # denoising
    bpy.context.scene.luxcore.denoiser.enabled = True
    bpy.context.scene.luxcore.denoiser.type = 'OIDN'
    bpy.context.scene.luxcore.denoiser.max_memory_MB = 8192

    # halt conditions
    bpy.context.scene.luxcore.halt.enable = True
    bpy.context.scene.luxcore.halt.use_time = True
    bpy.context.scene.luxcore.halt.use_samples = False
    bpy.context.scene.luxcore.halt.time = 60
    bpy.context.scene.luxcore.halt.samples = 8192

    # caches
    bpy.context.scene.luxcore.config.photongi.enabled = True
    bpy.context.scene.luxcore.config.envlight_cache.enabled = False
    bpy.context.scene.luxcore.config.dls_cache.enabled = False

    # color management
    bpy.context.scene.display_settings.display_device = 'sRGB'
    bpy.context.scene.view_settings.view_transform = 'Filmic'
    bpy.context.scene.view_settings.exposure = 0.0
    bpy.context.scene.view_settings.gamma = 1.0
    bpy.context.scene.sequencer_colorspace_settings.name = "sRGB"

    bpy.ops.render.render(write_still=True)
