#cd /home/ubuntu/Facescrub
import os, sys, re
images_dir = sys.argv[1]
person_names = os.listdir(images_dir)
rows = open("labels.csv",encoding='windows-1254')
find_str = ','
find_str2 = '\d*,'
row_dic = {}
image_dic = {}

for row in rows:
    result1 = re.search(find_str, row)
    beg = result1.start()
    row_new = row[beg + 1:]
    result2 = re.search(find_str2, row_new)
    end = result2.end()
    row_id = row_new[:end - 1]
    row_dic[row_id] = row

#retrieving dir
for person_name in person_names:
    person_dir = os.path.join(images_dir, person_name)
    image_names_person = os.listdir(person_dir)
        
    for image_name in image_names_person:
        image_id = image_name.split('.')[0].split('_')[-1]
        image_dic[image_id] = image_name
            
for image_num in image_dic:
    for row_num in row_dic:
        if row_num == image_num:
            print((image_dic[image_num] + ',' + row_dic[row_num]).rstrip('\n'))
            

    #            csv.writer('final_labels.csv')