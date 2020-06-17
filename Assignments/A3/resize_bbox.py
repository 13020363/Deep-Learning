import cv2, re
contents = open('data.csv')
#contents = open('test_labels.csv.bak')
content=[]

for row in contents:
   content.append(row) 
   
for line in content:
    file_type = line.split(',')[0].split('.')[-1]
    file_num = line.split(',')[0].split('_')[-1]
    person_name = line.split(',')[3]
    clase_name = re.sub(' ', '_', person_name)
    file_name = clase_name + '_' + file_num
    
    if file_type == 'jpeg':
        try:
            image = cv2.imread('/home/ubuntu/Facescrub/images/' + clase_name + '/' + file_name)
            height, width, depth = image.shape
            
            xmin = int(line.split(',')[4])
            ymin = int(line.split(',')[5])
            xmax = int(line.split(',')[6])
            ymax = int(line.split(',')[7])
            
            scale_x = 640/width
            scale_y = 480/height
            xmin = int(xmin * scale_x)
            ymin = int(ymin * scale_y)
            xmax = int(xmax * scale_x)
            ymax = int(ymax * scale_y)
        
            print(line.split(',')[0] + ',' +  640 + ',' +  480 + ',' + line.split(',')[3] + ',' + xmin + ',' + ymin + ',' + xmax + ',' + ymax)
            img = cv2.resize(image,(640,480))
            cv2.imwrite('/home/ubuntu/Facescrub/images/' + clase_name + '/' + file_name,img)
        except:
            None
    else:
        None