# encoding:UTF-8
from PIL import Image
import os

input_folder =u"E:\艺术照1"
output_folder = u"E:\艺术照2"
pattern = "art"
for dir,_,files in os.walk(input_folder):
    print input_folder
    index = 1
    for f in files:
        input_file = os.path.join(input_folder,f)
        _,file_ext = os.path.splitext(f)
        output_file = os.path.join(output_folder,"%s_%d.jpg"%(pattern,index))
        print input_file,output_file
        icon = Image.open(input_file).convert("CMYK")
        base_ratio_x = 1.0* 3840 / 2160
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
        icon.thumbnail((dest[0]/2,dest[1]/2), resample=1)
        icon.save(output_file)
        index+= 1

print 'job done'