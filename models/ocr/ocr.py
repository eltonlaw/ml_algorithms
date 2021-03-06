import numpy as np 
import cv2 
from time import sleep
from skimage import filters,measure
from scipy.ndimage.measurements import find_objects
import os
from matplotlib import pyplot as plt

np.random.seed(2)
np.set_printoptions(threshold=10000000)

####################################################################
def binarize(image):
    val,binary_image = cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # Otsu method to seperate foreground from background
    cv2.imwrite("./binary_image.png",binary_image)
    return binary_image
####################################################################
def pad(image,ii,write=False):
    """ Pad image so that it's dimensions are square """ 
    # Tuple of 2 lists with 255 elements to be appended/prepended 
    final_dim = max(shape[0],shape[1])
    req_p= abs(shape[0]-shape[1])
    add = np.ones((req_p/2,final_dim))*255
    if req_p % 2 == 0:
        req_p_s = (add,add)    
    else: 
        req_p_s = (add,np.ones((req_p/2+1,final_dim))*255)

    if shape[0] > shape[1]: # Columns < Rows, add extra columns of whitespace
        new_image = np.concatenate((np.transpose(req_p_s[0]),image),axis=1)
        new_image = np.concatenate((new_image,np.transpose(req_p_s[1])),axis=1)
    elif shape[1] > shape[0]:
        new_image = np.concatenate((req_p_s[0],image),axis=0)
        new_image = np.concatenate((new_image,req_p_s[1]),axis=0)
    else: # No change necessary if dimensions are already equal
        print "passed"
        return image
    
    if write == True:
        output_path = "./output/symbols_pad/"+str(ii)+".png"
        cv2.imwrite(output_path,new_image)
    return new_image
####################################################################
### Return symbols in a file
def get_symbols(image,write=False):
    image = myImage
    otsu_th = filters.threshold_otsu(image)
    boolean_matrix = image < otsu_th
    #boolean_matrix = image < 1
    all_labels = measure.label(boolean_matrix)  
    symbols_index = find_objects(all_labels)
    symbols = []
    for c,symbol_i in enumerate(symbols_index):
        symbol = myImage[symbol_i]
        symbols.append(symbol)
        if write == True:
            path = os.path.join("./output/symbols/"+str(c)+".jpg")
            cv2.imwrite(path,symbol)
    return symbols
####################################################################
### Count Number of Black Pixels in a symbol
def count_pixels(image):
    pixels = {}
    n_black= 0 
    b_positions = []
    for row,__ in enumerate(image):
        for column,_ in enumerate(image[row]):
            if image[row][column] == 0: 
                b_positions.append((row,column))
                n_black+=1
#    print "Total pixels:",len(image[0])*len(image[0])
#    print "# of black pixels:",blk_pixel_count
#    print "% of black pixels:",float(blk_pixel_count)/(len(image[0])*len(image[0])) 
    n_total = len(image[0])*len(image[0])
    n_white = n_total - n_black
    bw_ratio = np.around(n_black/float(n_white),decimals=4)
    pixels = {"n_black":n_black,"n_white":n_white,"n_total":n_total,"bw_ratio":bw_ratio,"b_positions":b_positions}
    return pixels

####################################################################
### Image Convolution(1) Row
def conv1(image,ii,write=False):
    print "\n conv1()"
    new_image = np.empty(np.shape(image)) 
    convolution =[[0.2,0.2,0.2,0.2,0.2]]

    padded_image=np.pad(image,((0,0),(2,2)),"constant",constant_values=255)
    for row,x in enumerate(image):
        for column,y in enumerate(image[row]):
            column+=2
            new_image[row][column-2]=np.dot(convolution[0],padded_image[row][column-2:column+3])
    new_image = new_image.astype("uint8")
    if write == True:
        output_path = "./output/convolution1/"+str(ii)+".jpg"
        cv2.imwrite(output_path,new_image)

    print "Convolution applied. Output of conv1() to path './output/convolution1/'"
    return new_image.astype("uint8")
### Image Convolution(2) Column
def conv2(image,ii,write=False):
    print "\n conv2()"
    new_image = np.empty(np.shape(image)) 
    convolution =[[0.2],[0.2],[0.2],[0.2],[0.2]]

    padded_image=np.pad(image,((2,2),(0,0)),"constant",constant_values=255)
    for row,x in enumerate(image):
        row+=2
        for column,y in enumerate(image[row-2]):
            x_ = [[padded_image[row-2:row+3][i][column]] for i in range(5)]
            total = 0
            # Dot product
            for a,b in zip(x_,convolution):
                            total+=a[0]*b[0]
            new_image[row-2][column]= total
    new_image = new_image.astype("uint8")
    if write == True:
        output_path = "./output/convolution2/"+str(ii)+".jpg"
        cv2.imwrite(output_path,new_image)
    print "Convolution applied. Output of conv2() to path './output/convolution2/'"
    return new_image

####################################################################
### Scale Image
# Helper Function
def get_i_list(a,b):
    """ Given a range of floats return a list of  integers in range"""
    array = [a]
    r = int(np.floor(b)-np.ceil(a)) +1
    array.extend([int(ii+np.ceil(a))    for ii in range(r)])
    if (array[-1] !=b):
        array.append(b)
    return array
def scale(image,ii,scale_size=(16,16),write=False):
    print "\n scale()"
    # Parameters
    original_img = image
    original_size = np.shape(original_img)
    scaled_img = np.ones(scale_size)
    ratio= ((np.shape(original_img)[0]-1)/float(scale_size[0]),(np.shape(original_img)[1]-1)/float(scale_size[1]))
    threshold = 0.2
    for i in range(scale_size[0]): # For 48 iterations
        x_0 = i* ratio[0]
        x_1 = (i+1) *ratio[0]-1
        for j in range(scale_size[1]): # For 32 iterations
            y_0 = j*ratio[1]
            y_1 =(j+1)*ratio[1]-1

            area = 0
            for x_i,y_i in zip([x_0,x_1],[y_0,y_1]):
                if y_i != int(original_size[1]):
                    x_list = get_i_list(x_0,x_1)
                    y_list = get_i_list(y_0,y_1)
                    counter = 0
                    for l in x_list:
                        for m in y_list:
                            if type(l) == int and type(m) == int: 
                                counter +=1
                                area += original_img[l][m]

                            if type(l) == float or type(m) == float:
                                fraction,fraction2 = 1,1
                                if x_list[-1] == l:
                                                fraction = l - np.floor(l)
                                elif x_list[0] == l:
                                                fraction = np.ceil(l) - l
                                if y_list[-1] == m:
                                                fraction2 = m - np.floor(m)
                                elif y_list[0] == m:
                                                fraction2 = np.ceil(m) - m
                                counter+=fraction*fraction2
                                area += original_img[int(l)][int(m)]*fraction*fraction2
                    if y_i == int(original_size[1]):
                        continue
                # Normalize total area, returns value between 0-255
            scaled_img[i][j] = area/counter

            if scaled_img[i][j] < (255*(1-threshold)):
                # Lower 80% of pixels will be converted to black
                scaled_img[i][j] = 0
            else: 
                scaled_img[i][j] = 255
    scaled_img = scaled_img.astype("uint8")
    if write == True:
        output_path = "./output/scaled/"+str(ii)+".jpg"
        cv2.imwrite(output_path,scaled_img)
    print "Image scaled to",scale_size,"output sent to path './output/scaled/'"
    return scaled_img

####################################################################
## Edge Detection
def round_45(angle):
    """ Round to 0,45,90,135"""
    if angle < 22.5:
        return 0
    elif angle < 67.5:
        return 45 
    elif angle < 112.5:
        return 90
    else:
        return 135

def get_neighbours(x,y,img):
    return [[img[x-1][y-1],img[x][y-1],img[x+1][y-1]],
            [img[x-1][y],img[x][y],img[x+1][y]],
            [img[x-1][y+1],img[x][y+1],img[x+1][y+1]]]
def non_max_suppression(magnitude,direction,image,neighbours):
    """At every pixel,pixel is checked if it is a local max in it's neighbourhood in the direction of gradient"""
    if direction == 0:
        n_left,n_right = neighbours[0][1],neighbours[2][1]
    elif direction == 45:
        n_left,n_right = neighbours[2][0],neighbours[0][2]
    elif direction == 90:
        n_left,n_right = neighbours[1][0],neighbours[1][2]
    elif direction == 135:
        n_left,n_right = neighbours[0][0],neighbours[2][2]

    if (n_left and n_right) < magnitude:
        return magnitude
    else: 
        return 0
def hysteresis_thresholding(minVal,maxVal,image):
    image=np.pad(image,((1,1),(1,1)),"constant",constant_values=0)
    for i,x in enumerate(image[1:-1,1:-1]):
        for j,y in enumerate(image[1:-1,1:-1][i]):
            if image[i][j] > maxVal:
                image[i][j] = 255
            elif image[i][j] < minVal:
                image[i][j] = 0
            else:
                if (image[i+1][j] or image[i-1][j] or image[i][j+1] or image[i][j-1]) > maxVal:
                    image[i][j] = 128
    return image

# Edge Detector
def edge_detector(image,ii,write=False):
    print "\n edge_detector()"
    image=np.pad(image,((1,1),(1,1)),"constant",constant_values=0)
    temp_img = np.copy(image)
    x_mask = [[-1,0,1],[-2,0,2],[-1,0,1]]
    y_mask = [[-1,-2,-1],[0,0,0],[1,2,1]]
    for i,x in enumerate(image[1:-1,1:-1]):
        for j,y in enumerate(image[1:-1,1:-1][i]):
            ns = get_neighbours(i,j,image)
            g_x = np.sum(np.multiply(x_mask,ns))
            if g_x == 0: g_x = 0.001
            g_y = np.sum(np.multiply(y_mask,ns))
            G = np.sqrt(np.square(g_x) + np.square(g_y))
            theta = round_45(np.arctan(float(g_y)/g_x))
            temp_img[i+1][j+1] = non_max_suppression(G,theta,image,ns)
    edges_img = hysteresis_thresholding(100,200,temp_img)
    edges_img = edges_img.astype("uint8")
    if write == True:
        output_path = "./output/edges/"+str(ii)+".jpg"
        cv2.imwrite(output_path,edges_img)

    return edges_img

####################################################################
## Thinning an image
def neighbours(x,y,image):
    try:
        P2 = image[x-1][y]
        P3 = image[x-1][y+1]
        P4 = image[x][y+1],
        P5 = image[x+1][y+1]
        P6 = image[x+1][y]
        P7 = image[x+1][y-1],
        P8 = image[x][y-1]
        P9 = image[x-1][y-1]
    except:
        return []
    return [P2,P3,P4[0],P5,P6,P7[0],P8,P9]
def n_transitions(neighbours):
    """  the number of transitions from white to black, (0 -> 1) in the sequence P2,P3,P4,P5,P6,P7,P8,P9,P2. (Note the extra P2 at the end - it is circular)."""
    transitions = 0 
    for i_0,i_1 in zip(neighbours,(neighbours+[neighbours[0]])[1:]):
        if i_0 == 255 and i_1 == 0:
            transitions +=1
    return transitions
def n_black(neighbours):
    return neighbours.count(0)

   # image[i][j]
   # image = cv2.imread("./output/scaled/0.jpg",0)
   # test_conditions(i,j,image,1)
   # test_conditions(i,j,image,2)

def test_conditions(i,j,image,step_i):
    ns = neighbours(i,j,image)

    # Condition 0
    if len(ns) == 8: P2,P3,P4,P5,P6,P7,P8,P9 = ns 
    else: return False
    
    if image[i][j] != 0: return False # Condition 1
    
    if not (2 <= n_black(ns) <= 6): return False # Condition 2
    
    if n_transitions(ns) != 1: return False # Condition 3

    # Condition 4 & 5 (depends on step number)
    if step_i == 1:
        if (P2 or P4 or P6) != 255: return False
        if (P4 or P6 or P8) != 255: return False
    elif step_i == 2:
        if (P2 or P4 or P8) != 255: return False
        if (P2 or P6 or P8) != 255: return False
    else: raise ValueError("step_i must be one of (1,2)")

    return True # If the program has satisfied all conditions and gotten this far, return true

def thin(image,ii,write=False):
    print "\n thin()"
    changed = True
    total_runs = 0
    temp_image = np.ones((np.shape(image)[0]+2,np.shape(image)[1]+2))*255
    temp_image[1:-1,1:-1] = image
    image = temp_image
    while changed == True:
        c = 0 # Resets counter, no change this loop yet
        # First Pass
        for step_i in [1,2]:
            changes = []
            for i,x in enumerate(image): # For each row...
                for j,y in enumerate(image[i]): # For each column...
                    if (test_conditions(i,j,image,step_i)):
                        changes.append((i,j))
                        c+=1
                # Simultaneous update
            for i,j in changes: # All pixels satisfying step_i  conditions are set to white 
                image[i][j] = 255
            #print "CHANGES",step_i,":",changes
        if c > 0:
            total_runs +=1
        else:
            changed = False

    image = image.astype("uint8")
    if write == True:
        output_path = "./output/thinned/"+str(ii)+".jpg"
        cv2.imwrite(output_path,image)
    print "Image thinned: Ran",total_runs,"passes" 
    return image
####################################################################
## Split image into 3x3 feature vector
def get_feature_vector(image,ii,write=False):
    print "\n get_feature_vector()"
    d0 = 0
    d1 = len(image)/3
    d2 = len(image)/3 * 2
    d3 = len(image) - 1
    dividers = [(d0,d1),(d1,d2),(d2,d3)] # Since each image is n x n, we only need to find the 1/3 markers for one side to get the other side as well
    feature_vector = []
    for x_0,x_1 in dividers:
        for y_0,y_1 in dividers:
            feature_vector.append(image[x_0:x_1,y_0:y_1])
    n = 1
    for feature in feature_vector:
        p = count_pixels(feature)
        plt.subplot(3,3,n)
        subplot_title = str(p["n_black"])+"b - "+str(p["n_white"])+"w = "+str(p["bw_ratio"])+"%"
        plt.title(subplot_title,fontsize = 8)
        plt.axis("off")
        plt.imshow(feature,cmap=plt.cm.binary)
        n+=1
    if write == True:
        output_path = "./output/feature_vectors/"+str(ii)+".jpg"
        plt.savefig(output_path)
        plt.clf()
    print "Image split into features"
    return feature_vector


####################################################################
## Store descriptions and predict using stored descriptions
def euclidean_distance(A,B):
    """Inputs are two same-size matrixes, return a scalar value """
    return np.linalg.norm(np.array(A)-np.array(B))
class FeatureDescriptions():
    def __init__(self):
        self.features = {"0":[],"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[]}
    def add(self,label,feature):
        """Add a feature vector to the array """
        print "FD:Adding to label...",label
        self.features[str(label)].append(feature)
        return None
    def transform(self,symbol):
        symbol = transform_split(symbol)
        return symbol
    def predict(self,symbol):
        """ Predict an already transformed symbol """
        distances = np.ones(len(self.features))*10000 # Distance initialized at 10000 for all symbol-feature pairs)
        for i,feature in enumerate(self.features):
            for feature_i in self.features[str(i)]:
                distance = euclidean_distance(feature_i,symbol)
                if distance < distances[i]: # If a feature vector is found for a number that's closer than before then assign that distance to be the new max distance
                    distances[i] = distance
        #prediction = np.argmin(distances) # Return index of the prediction with the lowest distance
        return distances

####################################################################
## Transform and Split
def transform_split(image,write_out=False):
    #padded_img = pad(image,ii,write=True)
    conv1_img = conv1(image,ii,write=write_out)
    conv2_img = conv2(conv1_img,ii,write=write_out)
    binary_img = binarize(conv2_img)
    scaled_img = scale(binary_img,ii,scale_size=(32,32),write=write_out)
    edges = edge_detector(scaled_img,ii,write=write_out)
    thinned_img = thin(scaled_img,ii,write=write_out)
    feature_vector = get_feature_vector(thinned_img,ii,write=write_out)
    return feature_vector

####################################################################

if __name__ =="__main__":
    myImage= cv2.imread("./input.jpg",0) # 0 converts the image to greyscale
    print "Loaded image with properties..."
    print "ROWS:",len(myImage) # 206
    print "COLUMNS:",len(myImage[0]) # 253
    symbols = get_symbols(myImage,write=False)
    output_path = "./output/symbols/"
    symbols = [cv2.imread(os.path.join(output_path,img),0) for img in os.listdir(output_path)][1:]	
    print "NUMBER OF SYMBOLS:",len(symbols)
    labels = [2,1,0,6,0,1,5,3,0,4,9,9,0,7,6,6,0,1,5,4,0,4,9,1,7,2,2,1,1,3,4,1,3,7,4,7,2,1,2,3,1,5,4,4,4,1,7,4,9,7,9]
    fd = FeatureDescriptions()
    feature_label_pairs = []
    for ii,img in enumerate(symbols): 
        print "\n ====== SYMBOL:",ii," ================================================"
        #pixels = count_pixels(img)
        feature = transform_split(img,write_out=True)
        feature_label_pairs.append((feature,labels[ii]))

    np.random.shuffle(feature_label_pairs)
    split = int(0.7*(len(feature_label_pairs)))
    print "Train/Test Split:",split
    # Train Set
    for feature,label in feature_label_pairs[:split]:
        fd.add(label,feature)
    for i in range(10):
        print i,len(fd.features[str(i)])
    # Test Set
    score,total = 0.0,0.0
    for feature,label in feature_label_pairs[split:]:
        total +=1.0
        distances = fd.predict(feature)
        prediction = np.argmin(distances)
        print "Distances array:",distances
        print "Prediction,Target:",prediction,label
        if prediction == label:
            score +=1.0
    print "FINISHED =================="
    print "Model Accuracy:",score/total
            
