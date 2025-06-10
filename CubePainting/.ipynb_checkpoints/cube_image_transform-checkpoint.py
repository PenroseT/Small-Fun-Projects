from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2
from os import path
import pickle
from matplotlib.colors import ListedColormap

# The weights used in the color distance measurements.
# This was done in a rather imprecise way. If I wanted
# to recreate the painting, I would probably use more
# perceptually uniform color model such as CIELAB.
weights1 = (2, 4, 3)
weights2 = (3, 4, 2)

#########################################################
############# INPUT COLOR AND IMAGE METHODS ############# 
#########################################################

def plot_color(color, size=(5, 5)):
    # Plots the color given in RGB coordinates as a big colorful square
    
    c = ListedColormap([tuple(color/255)])
    fig, ax  = plt.subplots(figsize=size)
    colplot = ax.imshow(np.ones(size), cmap = c)
    plt.axis('off')
    plt.show()
    
    return colplot

def plot_color_comparison(color1, color2, size=(5, 5), adjust=False):
    # Plots two colors side by side and shows their distance
    
    c1 = ListedColormap([tuple(color1/255)])
    c2 = ListedColormap([tuple(color2/255)])
    dist = rgb_distance(color1, color2, adjust=adjust)
    
    fig, axs  = plt.subplots(1, 2, figsize=(2*size[0], size[1]))
    colplot1 = axs[0].imshow(np.ones(size), cmap = c1)
    colplot2 = axs[1].imshow(np.ones(size), cmap = c2)
    axs[0].set_xlabel(f"RGB: {tuple(color1)}", fontsize=20, color="white")
    axs[1].set_xlabel(f"RGB: {tuple(color2)}", fontsize=20, color="white")
    
    for i in range(2):
        axs[i].spines['top'].set_visible(False)
        axs[i].spines['right'].set_visible(False)
        axs[i].spines['bottom'].set_visible(False)
        axs[i].spines['left'].set_visible(False)
        axs[i].get_xaxis().set_ticks([])
        axs[i].get_yaxis().set_ticks([])
        
    plt.suptitle(f"Distance={np.round(dist, 2)}", fontsize=30, color="white")
    
    plt.show()

def read_image(image_path, resize=False, size=(40, 30)):
    # Creates a numpy array from the image specified by the path

    image_original = cv2.imread(image_path, 1)
    image_original = cv2.cvtColor(image_original, cv2.COLOR_BGR2RGB)
    
    if resize:
        image_original = cv2.resize(image_original, size)

    return image_original

def plot_image(image):
    
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.axis("off")
    plt.show()

###########################################
############# PALETTE METHODS #############
###########################################

def convert_hex_to_rgb(color_hex):
    # HEX string --> RGB tuple format converter
    
    color_hex = color_hex.strip("#")
    color_rgb = np.array(tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)))
    
    return color_rgb
    
def convert_palette_to_RGB(palette_hex):
    # Takes the palette colors written in the hex format
    # and writes the palette as a list of RGB tuples
    
    palette_rgb = []
    
    for col in list(palette_hex.values()):
        palette_rgb.append(convert_hex_to_rgb(col))
    
    return palette_rgb

def create_scarce_palette(palette_hex, color_counts):
    # Takes the dictionary that contains hex codes
    # for the colors and their counts and converts it to a tuple consisting
    # of a list of counts and list of rgb codes for colors
    
    palette_rgb = convert_palette_to_RGB(palette_hex)
    palette_counts = list(color_counts.values())
    color_num = [sum(palette_counts)]
    
    scarce_palette = (palette_rgb, palette_counts, color_num)
    
    return scarce_palette

def load_my_palette():
    # Loads the palette in pickled files
    # specified by names given in the code
    
    with open("colors.pickle", "rb") as handle:
        my_colors = pickle.load(handle)
    with open("colors_rgb.pickle", "rb") as handle:
        my_colors_rgb = pickle.load(handle)
    
    scrc = create_scarce_palette(my_colors_rgb, my_colors)
    
    return scrc

def load_my_palette2(equal=False):
    # Loads the palette 2 in pickled files
    # specified by names given in the code
    
    if equal:
        with open("colors2eq.pickle", "rb") as handle:
            my_colors = pickle.load(handle)
        with open("colors_rgb2eq.pickle", "rb") as handle:
            my_colors_rgb = pickle.load(handle)   
    elif not equal:
        with open("colors2.pickle", "rb") as handle:
            my_colors = pickle.load(handle)
        with open("colors_rgb2.pickle", "rb") as handle:
            my_colors_rgb = pickle.load(handle)
    
    
    scrc = create_scarce_palette(my_colors_rgb, my_colors)
    
    return scrc

def multiply_palette(scarce_palette, m=13):
    # Multiply number of colors in palette by a factor m
    
    scarce_palette_m_counts = np.copy(scarce_palette[1])
    
    for i in range(len(scarce_palette[1])):
        scarce_palette_m_counts[i] = m*scarce_palette[1][i]

    scarce_palette_m = (scarce_palette[0], scarce_palette_m_counts,  [sum(scarce_palette_m_counts)])
    
    return scarce_palette_m

############################################
############# TRANSFORM METHODS ############
############################################

def rgb_distance(color1, color2, adjust=False):
    # Calculates the distance between two colors using parameters
    # guessed phenomenologically based on the available cubes and
    # the lighting under which cubes were shot.
    
    col1norm = color1/255
    col2norm = color2/255
    
    if adjust:
        Rmean = (int(color1[0])+int(color2[0]))/2
        if Rmean < 128:
            dist = np.sqrt(sum([weights1[i]*(col1norm[i]-col2norm[i])**2 for i in range(3)]))
        else:
            dist = np.sqrt(sum([weights2[i]*(col1norm[i]-col2norm[i])**2 for i in range(3)]))
    else:
        dist = np.sqrt(sum([(col1norm[i]-col2norm[i])**2 for i in range(3)]))
        
    return dist

def rgb_scarce_distance(color1, color2, fraction, scarcity_weight=0.1, adjust=False):
    # The distance between colors is calculated with taking into the account
    # the fraction of remaining colors. The influence of the fraction on
    # the distance is parametrized by artanh(1/frac) function
    
    col1norm = color1/255
    col2norm = color2/255
    
    if fraction > 0.0:
        scarcity_factor = 2.0*np.arctanh(scarcity_weight*(1.0-fraction))-1.0
    else:
        scarcity_factor = np.inf
    
    if adjust:
        Rmean = (int(color1[0])+int(color2[0]))/2
        if Rmean < 128:
            dist = scarcity_factor*np.sqrt(sum([weights1[i]*(col1norm[i]-col2norm[i])**2 for i in range(3)]))
        else:
            dist = scarcity_factor*np.sqrt(sum([weights2[i]*(col1norm[i]-col2norm[i])**2 for i in range(3)]))
    else:
        dist = scarcity_factor*np.sqrt(sum([(col1norm[i]-col2norm[i])**2 for i in range(3)]))
        
    return dist

#----------------BASIC TRANSFORM----------------#

def choose_color(color_inp, color_palette, adjust=False):
    # Picks a color from the palette defined by the available 
    # cubes by searching for the cube with the smallest color distance.
    
    color_min = color_palette[0]
    dist_min = rgb_distance(color_inp, color_min, adjust=adjust)
    
    for idx, color in enumerate(color_palette[1: ]):
        dist = rgb_distance(color_inp, color, adjust=adjust)
        if dist < dist_min:
            color_min = color_palette[idx+1]
            dist_min = dist
    
    return color_min

def transform_image(image, color_palette, adjust=False):
    # Represents the image using the pixels closest
    # to the chosen palette
    
    xdim, ydim, znum = image.shape
    image_transform = np.copy(image)
    

    for i in range(xdim):
        for j in range(ydim):
            color = np.zeros(znum)
            color = choose_color(image[i, j], color_palette, adjust=False)
            image_transform[i, j] = color
    
    return image_transform

#----------------SCARCE TRANSFORM----------------#


def choose_color_scarce(color_inp, scarce_palette, scarcity_weight=0.1, adjust=False):
    # Color is chosen with regard to a scarce_arctanh distance 
    
    color_min = scarce_palette[0][0]
    dist_min = rgb_scarce_distance(color_inp, color_min, scarce_palette[1][0]/scarce_palette[2][0],
                                   scarcity_weight=scarcity_weight, adjust=adjust)
    idx_min = 0
    
    for idx, color in enumerate(scarce_palette[0][1: ]):
        dist = rgb_scarce_distance(color_inp, color, scarce_palette[1][idx+1]/scarce_palette[2][0],
                                    scarcity_weight=scarcity_weight, adjust=adjust)
        if dist < dist_min:
            color_min = scarce_palette[0][idx+1]
            dist_min = dist
            idx_min=idx+1
    
    # Decrement the color fraction
    scarce_palette[1][idx_min]-=1
    scarce_palette[2][0]-=1
    
    return color_min

def transform_image_scarce(image, scarce_palette, scarcity_weight=1.0, adjust=False):
    # Scarce image transform function
    
    xdim, ydim, znum = image.shape
    image_transform = np.copy(image)
        
    color_num = scarce_palette[2][0]
    
    if color_num < image.shape[0]*image.shape[1]:
        raise Exception("There is not enough colors to recreate the image")
    
    for i in range(xdim):
        for j in range(ydim):
            color = np.zeros(znum)
            color = choose_color_scarce(image[i, j], scarce_palette,
                                        scarcity_weight=scarcity_weight, adjust=False)
            image_transform[i, j] = color
        
    return image_transform

def apply_permuted(matrix, func):
    # Matrix has to be 3x3 and func acts on arrays
    
    xdim, ydim, zdim = matrix.shape
    matrix = matrix.reshape(xdim*ydim, zdim)
    
    idcs = np.arange(0, xdim*ydim, 1)
    
    rng = np.random.default_rng()
    shuffled_idcs = rng.permuted(idcs)
    inverse_idcs = np.argsort(shuffled_idcs)
    matrix = matrix[shuffled_idcs, :]
    
    for i in range(xdim*ydim):
        matrix[i] = func(matrix[i])
    
    
    matrix = matrix[inverse_idcs, :]
    matrix = matrix.reshape(xdim, ydim, zdim)
    
    return matrix

def transform_image_scarce_permute(image, scarce_palette, scarcity_weight=1.0, adjust=False):
    # Scarce image transform function
    
    xdim, ydim, zdim = image.shape
    image_transform = np.copy(image)
    image_transform = image_transform.reshape(xdim*ydim, zdim)
    
    rng = np.random.default_rng()
    idcs = np.arange(0, xdim*ydim, 1)
    shuffled_idcs = rng.permuted(idcs)
    inverse_idcs = np.argsort(shuffled_idcs)
    
    image_transform = image_transform[shuffled_idcs, :]
        
    color_num = scarce_palette[2][0]
    
    if color_num < xdim*ydim:
        raise Exception("There is not enough colors to recreate the image")

    for i in range(xdim*ydim):
         image_transform[i, :] = choose_color_scarce(image_transform[i, :], scarce_palette,
                                                     scarcity_weight=scarcity_weight, adjust=False)

    image_transform = image_transform[inverse_idcs, :]
    image_transform = image_transform.reshape(xdim, ydim, zdim)
        
    return image_transform

#----------------MONTE CARLO METHODS----------------#

def swap_mc(image, image_original, adjust=False):
    # Perform a single random two-pixel swap on the image 
    
    x_src, x_tgt = np.random.randint(0, image.shape[0]), np.random.randint(0, image.shape[0])
    y_src, y_tgt = np.random.randint(0, image.shape[1]), np.random.randint(0, image.shape[1])
    
    src_dist_init = rgb_distance(image[x_src, y_src, :], image_original[x_src, y_src, :], adjust=adjust)
    tgt_dist_init = rgb_distance(image[x_tgt, y_tgt, :], image_original[x_tgt, y_tgt, :], adjust=adjust)

    src_dist_fin = rgb_distance(image[x_src, y_src, :], image_original[x_tgt, y_tgt, :], adjust=adjust)
    tgt_dist_fin = rgb_distance(image[x_tgt, y_tgt, :], image_original[x_src, y_src, :], adjust=adjust)
    
    delta_dist = (src_dist_fin-src_dist_init)+(tgt_dist_fin-tgt_dist_init)
    
    if delta_dist <=0:
        
        col_tgt = image[x_tgt, y_tgt, :]
        image[x_tgt, y_tgt, :] = image[x_src, y_src, :]
        image[x_src, y_src, :] = col_tgt
    
    return image

def transform_mc(image, image_original, steps=10000, adjust=False):
    # Perform the Monte Carlo transform of the image
    
    for i in range(steps):
        swap_mc(image, image_original, adjust=adjust)

    return image

############################################
############# DISPLAY METHOD ###############
############################################

def display_all(image_original, scarce_palette, imagesize=(40, 30), m=1,
                scarcity_weight=0.9, adjust=False, nsteps=100000, save=False, name="test"):
    # Takes the original image and scarce palette
    # and displays the original image along the 
    # transforms and Monte Carlo refinements
    
    # Resizes the image to wanted size
    image = cv2.resize(image_original, imagesize)
    
    # Sequential algorithm
    scrc = multiply_palette(scarce_palette, m=m)
    image_scarce = transform_image_scarce(image, scrc, adjust=adjust, scarcity_weight=scarcity_weight)
    image_scarce_cp = np.copy(image_scarce)
    
    # Permuted algorithm
    scrc = multiply_palette(scarce_palette, m=m)
    image_scarce_permute = transform_image_scarce_permute(image, scrc, adjust=adjust, scarcity_weight=scarcity_weight)
    image_scarce_permute_cp = np.copy(image_scarce_permute)
    
    # Monte Carlo refinement for both alhorithms
    image_scarce_permute_mc = transform_mc(image_scarce_permute_cp, image, adjust=adjust, steps=nsteps)
    image_scarce_mc = transform_mc(image_scarce_cp, image, adjust=adjust, steps=nsteps)


    fig, axs = plt.subplots(1, 5, figsize=(20, 10))

    axs[0].imshow(image)
    axs[0].set_title("Original", fontsize=35)
    axs[0].axis("off")

    axs[1].imshow(image_scarce)
    axs[1].set_title("Sequential", fontsize=35)
    axs[1].axis("off")
    
    axs[2].imshow(image_scarce_mc)
    axs[2].set_title("Sequential+MC", fontsize=35)
    axs[2].axis("off")
    
    axs[3].imshow(image_scarce_permute)
    axs[3].set_title("Permuted", fontsize=35)
    axs[3].axis("off")

    axs[4].imshow(image_scarce_permute_mc)
    axs[4].set_title("Permuted+MC", fontsize=35)
    axs[4].axis("off")

    plt.tight_layout()

    plt.axis("off")
    if save==True:
        plt.savefig("images/transforms/"+name+".jpg")
        
    plt.show()