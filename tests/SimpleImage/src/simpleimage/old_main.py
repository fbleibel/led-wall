import os
from argparse import ArgumentParser
from PyQt4 import QtCore, QtGui

# Pixels per row
NUM_PIXELS_H = 72
# Pixels per column
NUM_PIXELS_V = 36
# Teensy boards controlling tiles
NUM_TEENSY = 3

ROWS_PER_TEENSY = NUM_PIXELS_V / NUM_TEENSY

def process(path, out_dir):
    print "Reading{0}".format(path)
    image = QtGui.QImage(path)
    if image.width() != NUM_PIXELS_H or image.height() != NUM_PIXELS_V:
        print "Resizing to {0}x{1} (original size: {2}x{3})".format(
            NUM_PIXELS_H, NUM_PIXELS_V, image.width(), image.height())
        image = image.scaled( NUM_PIXELS_H, NUM_PIXELS_V )
    name, _ = os.path.splitext(os.path.basename(path))
    out_name = "{0}_teensy{{0}}.h".format(name)
    out_dir = out_dir or os.path.dirname(os.path.abspath(path))
    
    # One list per strip, one entry per pixel as a string.
    strips = []
    def components(rgb):
        """
        Returns the escaped ascii string representing the pixel colour.
        """
        components = (rgb & 0xFF0000, rgb & 0x00FF00, rgb & 0x0000FF)
        rval = []
        for i, c in enumerate(components):
            char = c >> (8 * (3 - i))
            rval.append(r"\x{0:02x}".format(char))
        return "".join(rval)
        
    # row 0 is at the bottom
    for teensy in xrange(NUM_TEENSY):
        row_start = teensy * ROWS_PER_TEENSY
        row_end = (teensy + 1) * ROWS_PER_TEENSY
        for row in xrange(row_start, row_end, 2):
            strip = []
            # 1 strip is 2 rows, Row A is left->right, B is right->left
            image_row_A = NUM_PIXELS_H - 1 - row
            image_row_B = image_row_A - 1
            for col in xrange(NUM_PIXELS_V):
                rgb = image.pixel(image_row_A, col)
                strip.append(components(rgb))
            for col in xrange(NUM_PIXELS_V):
                rgb = image.pixel(image_row_B, NUM_PIXELS_V - col - 1)
                strip.append(components(rgb))
            strips.append(strip)
    
    lines = []
    for teensy in xrange(NUM_TEENSY):
        lines.append("\n\n")
        lines.append("/* ------------------------------\n")
        lines.append("   Teensy #{0} - image data from {1}\n".format(
            teensy + 1, name))
        lines.append("   ------------------------------ */\n")
        lines.append("const char image_data[] = \\\n")
        
        strips_per_teensy = ROWS_PER_TEENSY / 2
        start = teensy * ROWS_PER_TEENSY / 2
        end = (teensy + 1) * ROWS_PER_TEENSY / 2
        for strip_index in xrange(start, end):
            strip = strips[strip_index]
            header = "  // Strip {0}, rows {1} + {2}\n".format(
                strip_index + 1, strip_index * 2 + 1, strip_index * 2 + 2 )
            lines.append(header)
            # spaces and quotes
            character_count = 4
            line_accum = []
            for pixel_index, pixel in enumerate(strip):
                line_accum.append(pixel)
                character_count += len(pixel)
                # The next pixel would overflow
                if character_count > 80 - len(pixel): 
                    lines.append('  "{0}"'.format("".join(line_accum)))
                    character_count = 4
                    del line_accum[:]
                    # Is this the last line?
                    if strip_index == end - 1 and pixel_index == len(strip) - 1:
                        lines.append(";\n")
                    else:
                        lines.append("\n")
            if line_accum:
                # Some pixels remain.
                lines.append('  "{0}"'.format("".join(line_accum)))
                # Is this the last line?
                if strip_index == end - 1:
                    lines.append(";\n")
                else:
                    lines.append("\n")
        header_path = os.path.join(out_dir, out_name.format(teensy + 1))
        print "Writing image data to {0}".format(header_path)
        with open(header_path, "w") as fileout:
            fileout.writelines(lines)
            
def main():
    """
    """
    app = QtGui.QApplication([])
    parser = ArgumentParser()
    parser.add_argument("path", help="Path to the image to transform")
    parser.add_argument("out_dir",
                        help="Directory where to write the output files",
                        nargs="?")
    args = parser.parse_args()
    process(args.path, args.out_dir)
    
if __name__ == "__main__":
    main()

