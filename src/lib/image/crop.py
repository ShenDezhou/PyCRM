#! /bin/python
# encoding: utf-8
from PIL import Image
import os
import sys

input_folder =r"d:\1"
output_folder = r"d:\\"
def crop_file(input_file,output_file,pattern = "RGB"):
    icon = Image.open(input_file).convert(pattern)
    base_ratio_x = 1.0 * 3840 / 2160
    base_ratio_y = 1.0 / base_ratio_x
    xratio = 1.0 * icon.size[0] / icon.size[1]
    yratio = 1.0 * icon.size[1] / icon.size[0]

    if icon.width > icon.height:
        base_ratio = base_ratio_x
        if xratio > base_ratio:
            dest = (int(3840 / 2), int(yratio * 3840 / 2))
        else:
            dest = (int(2160 * xratio / 2), int(2160 / 2))
    else:
        base_ratio = base_ratio_y
        if yratio > base_ratio:
            dest = (int(2160 / 2), int(yratio * 2160 / 2))
        else:
            dest = (int(3840 * xratio / 2), int(3840 / 2))

    icon = icon.resize(dest, resample=1)
    icon.thumbnail((dest[0], dest[1]), resample=1)
    icon.save(output_file)

def crop(input_folder, output_folder, pattern = "art"):
    for dir,_,files in os.walk(input_folder):
        print input_folder
        index = 1
        for f in files:
            input_file = os.path.join(input_folder,f)
            _,file_ext = os.path.splitext(f)
            output_file = os.path.join(output_folder,"%s_%d.png"%(pattern,index))
            print input_file,output_file
            crop_file(input_file,output_file)
            index += 1


print 'job done'

if __name__ == "__main__":
    input= input_folder
    if len(sys.argv) > 1:
        input = sys.argv[1]
        if os.path.isfile(input):
            output = os.path.join(os.path.dirname(input),"out_"+os.path.basename(input))
            crop_file(input,output)
            sys.exit(0)
    output = os.path.join(input, "output")
    if len(sys.argv) > 2:
        output = sys.argv[2]
        if not os.path.exists(output):
            os.makedirs(output)
    crop(input,output)
    sys.exit(0)
