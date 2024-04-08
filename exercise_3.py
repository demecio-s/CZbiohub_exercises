# Measure the eccentricity of each nucleus you detected and plot the results 
# as a histogram. Label the histogram such that we can understand the data it shows.

import matplotlib.pyplot as plt  # tool for plotting
import tifffile as tiff
import numpy as np
import skimage as ski  # tool for image analysis, here used for segmentation and finding eccentricities
from scipy import ndimage  # tool used for image analysis, here used for segmentation
from matplotlib import rc  # formatting figures
rc('font', **{'size': 16})
rc('axes', **{'labelsize': 16, 'linewidth': 1})
rc('xtick', **{'direction': 'in', 'top': True, 'minor.visible': True})
rc('ytick', **{'direction': 'in', 'right': True, 'minor.visible': True})


def eccentricity(maj_axis, min_axis):
    return np.sqrt(abs(maj_axis**2 - min_axis**2)) / maj_axis


with tiff.TiffFile('Assoc_RDEng_test.tif') as images:
    for iter, page in enumerate(images.pages, 1):
        image = page.asarray()

        # creating threshold for region based segmentation similar to: 
        # https://scikit-image.org/docs/stable/user_guide/tutorial_segmentation.html#region-based-segmentation
        std_dev = image.std()
        min = image.min()

        # looking for edges of nuclei
        edges = np.zeros_like(image)
        edges[image <= (min + std_dev)] = 1
        edges[image > (min + std_dev)] = 2
        elevation_map = ski.filters.sobel(image)

        segment = ski.segmentation.watershed(elevation_map, edges)

        # removing small holes and getting edges of segmented image
        segment = ndimage.binary_fill_holes(segment-1)
        nuclei_edges = ski.feature.canny(segment)

        # labeling and locating all nuclei 
        labels, num_features = ndimage.label(segment)
        nuclei = ndimage.find_objects(labels)

        print(f"Succesfully segmented page {iter}!\n\n",
              "Beginning eccentricity measurements")

        e = []  # initialize list for eccentricty values

        # will iterate over all found objects (nuclei)
        for obj, nucleus in enumerate(nuclei, 1):
            # detect ellipsis and pick one with highest accumulator, nonzero major axes
            ellipse = ski.transform.hough_ellipse(nuclei_edges[nucleus],
                                                  accuracy=11
                                                  )
            if len(ellipse) == 0:
                continue

            ellipse.sort(order='accumulator')
            # checks until you get highest accumulator with nonzero major/minor axes and eccentricity<1
            for accum in range(len(ellipse)-1, 0, -1):
                accumulator, y_cent, x_cent, maj_axis, min_axis, orientation = ellipse[accum]
                if min_axis == np.float64(0) or maj_axis == np.float64(0):
                    continue
                elif eccentricity(maj_axis, min_axis) < 1:
                    e.append(eccentricity(maj_axis, min_axis))
                    # if obj%10 == 0:
                    #     print(f"{obj} object's eccentricity calculated!")
                    break
                else:
                    continue

        # makes histograms for each page
        plt.hist(e, bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
        plt.xlabel('Eccentricity')
        plt.ylabel('Nuclei count')
        plt.title(f"Eccentricities of nuclei in page {iter}")
        plt.savefig(f"exercise_3_figs/page_{iter}_fig.png")
        plt.close()

        print(f"Page {iter} done!")

print("All done!")
