from PIL import Image
import sys

def convert_png_to_ico(png_path, ico_path):
    try:
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=[(256, 256)])
        print(f"Successfully converted {png_path} to {ico_path}")
    except Exception as e:
        print(f"Error converting: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_ico.py <input.png> <output.ico>")
    else:
        convert_png_to_ico(sys.argv[1], sys.argv[2])
