import bpy

try:
    from utilities import formatted_time
except ImportError:
    from datetime import datetime
    def formatted_time():
        return datetime.now().isoformat(timespec="milliseconds")


def render_aov(engine: str, aov: str, filename: str, output_directory: str="."):
    """Use the compositor to select the render pass to render.

    This function uses the compositor nodes to link the render layers
    to an output file. The AOV is found in the render layer
    and sent to the engine to render. The AOV needs to be present
    in one of the view layers for this render to complete.
    """
    bpy.context.scene.use_nodes = True
    node_tree = bpy.context.scene.node_tree

    render_layers = node_tree.nodes.get("Render Layers")

    node_tree.nodes.new(type="CompositorNodeOutputFile")
    output_file_node = node_tree.nodes.get("File Output")
    output_file_node.base_path = output_directory
    output_file_node.format.file_format = "OPEN_EXR"
    output_file_node.format.quality = 100

    output_pass = render_layers.outputs.get(aov)

    link = node_tree.links.new(output_pass, output_file_node.inputs[0])

    bpy.context.scene.render.engine = engine
    bpy.context.scene.render.filepath = "{}/{}_{}" .format(output_file_node.base_path,
                                                           aov.lower(),
                                                           formatted_time())
    bpy.ops.render.render(write_still=True)


def render_rgb(engine: str, output_directory: str="."):
    """Render an RGB image using the given engine into the output directory.

    Choices for engine are 'LUXCORE', 'CYCLES', or 'EEVEE'.
    The curren time is appended to the rendered image so that
    each render has a unique filename.
    """
    bpy.context.scene.render.filepath = "{}/rgb_{}.png" .format(output_directory, formatted_time())
    bpy.context.scene.render.engine = engine
    bpy.ops.render.render(write_still=True)


def render_normals(engine: str, output_directory: str="."):
    """Render an image with the objects in the scene shaded with their normals.

    The normals are transformed from world space into camera space. This should be
    handled in a Blender view layer with a normal material override.
    """
    bpy.context.scene.render.filepath = "{}/normal_{}.png" .format(output_directory, formatted_time())
    bpy.context.scene.render.engine = engine
    bpy.context.view_layer.use_pass_combined = False
    bpy.context.view_layer.use_pass_z = False
    bpy.context.view_layer.use_pass_normal = True
    bpy.context.view_layer.update_render_passes()
    bpy.ops.render.render(write_still=True)


def render_luxcore(output_directory: str="."):
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

def create_material_nodes(preset, mesh_name=None, color=(1.0, 1.0, 1.0)):
    """Create a new Luxcore Material with the given preset.

    The material will be added to a mesh if present.

    Notes
    -----
    In Luxcore 2.3 the following presets are available:
        Disney, Mix, Matte, Glossy, Glass, Null (Transparent), Metal, Mirror,
        Glossy Translucent, Matte Translucent, Smoke, Fire and Smoke, Colored Glass.
    """
    material = bpy.data.materials.new(name="Material")
    tree_name = "Nodes_" + material.name
    node_tree = bpy.data.node_groups.new(name=tree_name, type="luxcore_material_nodes")
    material.luxcore.node_tree = node_tree
    node_tree.use_fake_user = True

    nodes = node_tree.nodes
    output = nodes.new("LuxCoreNodeMatOutput")
    output.select = False

    material_node = nodes.new("LuxCoreNodeMat" + preset)

    if preset == 'Disney':
        material_node.inputs['Base Color'].default_value = color
        material_node.inputs['Subsurface'].default_value = 0.0
        material_node.inputs['Metallic'].default_value = 0.0
        material_node.inputs['Specular'].default_value = 0.5
        material_node.inputs['Specular Tint'].default_value = 0.0
        material_node.inputs['Roughness'].default_value = 0.0
        material_node.inputs['Anisotropic'].default_value = 0.0
        material_node.inputs['Sheen'].default_value = 0.0
        material_node.inputs['Sheen Tint'].default_value = 0.0
        material_node.inputs['Clearcoat'].default_value = 0.0
        material_node.inputs['Clearcoat Gloss'].default_value = 0.0
        material_node.inputs['Opacity'].default_value = 1.0

    if preset == 'Metal':
        material_node.inputs['Color'].default_value = color

    if preset == 'Glossy Material':
        material_node.inputs['Diffuse Color'].default_value = color

    node_tree.links.new(material_node.outputs[0], output.inputs[0])

    if mesh_name is not None:
        bpy.context.view_layer.objects.active = bpy.data.objects[mesh_name]
        mesh = bpy.context.active_object

        if mesh.material_slots is not None:
            mesh.material_slots[mesh.active_material_index].material = material
        else:
            mesh.data.materials.append(material)


def render_luxcore_rgb(output_directory='.', device='CPU', engine='PATH', sampler='SOBEL'):
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


def main():
    bpy.utils.user_resource("CONFIG")
    create_material_nodes('Disney', 'xmas_clover')
    render_luxcore()


main()