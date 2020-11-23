from math import tan, sqrt
from PIL import Image


def transform_depth(image_path, output_path, fov):
	"""Transform a depth render to account for offsets in the way Cycles renders depth images.
	
	Parameters
	----------
	image_path: str
		The file path to the depth image to be processed
	output_path: str
		The file path to save the transformed image
	fov: float
		The angle of the field of view of the camera (in degrees)

	Returns
	-------
	None

	References: https://blender.stackexchange.com/questions/87504/blender-cycles-z-coordinate-vs-camera-centered-z-coordinate-orthogonal-distan
	"""
	im = Image.open(image_path)
	output_image = Image.new('RGBA', im.size, 1)

	width, height = im.size

	cx = width / 2
	cy = height / 2
	f = cx / tan(fov / 2)

	for x in range(width):
	    for y in range(height):
	        pixel = [0, 0, 0, 255]
	        
	        for c in range(3):
	            pixel[c] = im.getpixel((x, y))[c] * (f / sqrt(f**2 + (cx - x - 0.5)**2 + (cy - y - 0.5)**2))
	        
	        pixel = [int(p) for p in pixel]
	        
	        if im.getpixel((x, y)) != (255, 255, 255, 255):
	            output_image.putpixel((x,y), tuple(pixel))

	output_image.save(output_path)