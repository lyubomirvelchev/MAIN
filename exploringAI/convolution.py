from PIL import Image
import numpy as np
import copy
import time

img = Image.open('king_leonidas.jpg')
grey_img = img.convert('L')
original_img_array = np.array(grey_img)

kernel = np.array([
    [1 / 256, 4 / 256, 6 / 256, 4 / 256, 1 / 256],
    [4 / 256, 16 / 256, 24 / 256, 16 / 256, 4 / 256],
    [6 / 256, 24 / 256, 36 / 256, 24 / 256, 6 / 256],
    [4 / 256, 16 / 256, 24 / 256, 16 / 256, 4 / 256],
    [1 / 256, 4 / 256, 6 / 256, 4 / 256, 1 / 256]
])

big_kernel = np.array([
    [1, 4, 6, 8, 9, 8, 6, 4, 1],
    [4, 16, 24, 32, 36, 32, 24, 16, 4],
    [6, 24, 36, 48, 54, 48, 36, 24, 6],
    [8, 32, 48, 64, 72, 64, 48, 32, 8],
    [9, 36, 54, 72, 81, 72, 54, 36, 9],
    [8, 32, 48, 64, 72, 64, 48, 32, 8],
    [6, 24, 36, 48, 54, 48, 36, 24, 6],
    [4, 16, 24, 32, 36, 32, 24, 16, 4],
    [1, 4, 6, 8, 9, 8, 6, 4, 1]
], dtype=np.float32) / 2209


def convolve_once(img_array, kernel):
    number_of_iterations = 0
    output_height = img_array.shape[0] - kernel.shape[0] + 1
    output_width = img_array.shape[1] - kernel.shape[1] + 1
    new_img = np.zeros((output_height, output_width))
    for i in range(output_height):
        for j in range(output_width):
            for ii in range(kernel.shape[0]):
                for jj in range(kernel.shape[1]):
                    new_img[i, j] += kernel[ii, jj] * img_array[i + ii, j + jj]
                    number_of_iterations += 1
    print("Number of iterations: {}".format(number_of_iterations))
    return new_img

def convolve_using_numpy(img_array, kernel):
    number_of_iterations = 0
    output_height = img_array.shape[0] - kernel.shape[0] + 1
    output_width = img_array.shape[1] - kernel.shape[1] + 1
    new_img = np.zeros((output_height, output_width))
    for i in range(output_height):
        for j in range(output_width):
            new_img[i, j] = np.sum(kernel * img_array[i:i + kernel.shape[0], j:j + kernel.shape[1]])
            number_of_iterations += 1
    print("Number of iterations: {}".format(number_of_iterations))
    return new_img

grey_img.show()
img_array = copy.deepcopy(original_img_array)
start = time.time()
for i in range(1):
    img_array = convolve_once(img_array, big_kernel)
    to_img = Image.fromarray(img_array)
    to_img.show()
    print("Image shape at iteration {}: {}".format(i, img_array.shape))
print("Time taken: {}".format(time.time() - start))

grey_img.show()
img_array = copy.deepcopy(original_img_array)
start = time.time()
for i in range(1):
    img_array = convolve_using_numpy(img_array, big_kernel)
    to_img = Image.fromarray(img_array)
    to_img.show()
    print("Image shape at iteration {}: {}".format(i, img_array.shape))
print("Time taken: {}".format(time.time() - start))
