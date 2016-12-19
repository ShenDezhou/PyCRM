# encoding:UTF-8
from PIL import Image
import os

# input_folder =u"E:\艺术照"
# output_folder = u"E:\艺术照1"
# pattern = "art"
# for dir,_,files in os.walk(input_folder):
#     print input_folder
#     index = 1
#     for f in files:
#         input_file = os.path.join(input_folder,f)
#         _,file_ext = os.path.splitext(f)
#         output_file = os.path.join(output_folder,"%s_%d.jpg"%(pattern,index))
#         print input_file,output_file
#         icon = Image.open(input_file).convert("CMYK")
#         base_ratio_x = 1.0* 3840 / 2160
#         base_ratio_y = 1.0 / base_ratio_x
#         xratio = 1.0 * icon.size[0] / icon.size[1]
#         yratio = 1.0 * icon.size[1] / icon.size[0]
#
#         if icon.width > icon.height:
#             base_ratio = base_ratio_x
#             if xratio > base_ratio:
#                 dest = (int(3840 / 2), int(yratio * 3840 / 2))
#             else:
#                 dest = (int(2160 * xratio / 2), int(2160 / 2))
#         else:
#             base_ratio = base_ratio_y
#             if yratio > base_ratio:
#                 dest = (int(2160 / 2), int(yratio * 2160 / 2))
#             else:
#                 dest = (int(3840 * xratio / 2), int(3840 / 2))
#
#         icon = icon.resize(dest, resample=1)
#         # icon.thumbnail(dest, resample=1)
#         icon.save(output_file)
#         index+= 1

input_folder =u"E:\美照"
output_folder = u"E:\美照1"
pattern = "beauty"
for path,dir,files in os.walk(input_folder):
    print dir
    folder = 1
    for d in dir:
        print d
        index = 1
        subfolder = os.path.join(input_folder,d)
        for _,_,subfiles in os.walk(subfolder):
            for f in subfiles:
                input_file = os.path.join(subfolder,f)
                _,file_ext = os.path.splitext(f)
                output_file = os.path.join(output_folder,"%s_%d_%d.jpg"%(pattern,folder,index))
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
                # icon.thumbnail(dest, resample=1)
                icon.save(output_file)
                index+= 1
        folder += 1
print 'job done'