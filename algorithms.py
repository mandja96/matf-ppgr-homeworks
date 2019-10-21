import numpy as np
import math
from PIL import Image

points = []
points_proj = []

canonical_points = [[1, 0, 0], 
                    [0, 1, 0], 
                    [0, 0, 1],
                    [1, 1, 1]]


def cramers_rule(points):
    delta = np.float32([[points[0][0], points[1][0], points[2][0]],
                        [points[0][1], points[1][1], points[2][1]],
                        [points[0][2], points[1][2], points[2][2]]])

    delta1 = np.float32([[points[3][0], points[1][0], points[2][0]],
                         [points[3][1], points[1][1], points[2][1]],
                         [points[3][2], points[1][2], points[2][2]]])
 
    delta2 = np.float32([[points[0][0], points[3][0], points[2][0]],
                         [points[0][1], points[3][1], points[2][1]],
                         [points[0][2], points[3][2], points[2][2]]])

    delta3 = np.float32([[points[0][0], points[1][0], points[3][0]],
                         [points[0][1], points[1][1], points[3][1]],
                         [points[0][2], points[1][2], points[3][2]]])
    
    delta_det = (np.linalg.det(delta))
    delta1_det = (np.linalg.det(delta1))
    delta2_det = (np.linalg.det(delta2))
    delta3_det = (np.linalg.det(delta3))

    
    lambda1 = delta1_det / delta_det
    lambda2 = delta2_det / delta_det
    lambda3 = delta3_det / delta_det

    return (lambda1, lambda2, lambda3)

def projection_matrix_P(points, points_proj):
    (lambda1, lambda2, lambda3) = cramers_rule(points)
    projection_matrix = np.array([[x*lambda1 for x in points[0]],
                                  [x*lambda2 for x in points[1]],
                                  [x*lambda3 for x in points[2]]])
    projection_matrix = np.transpose(projection_matrix)
    
    (lambda1p, lambda2p, lambda3p) = cramers_rule(points_proj)
    projection_matrix_prim = np.array([[x*lambda1p for x in points_proj[0]],
                                       [x*lambda2p for x in points_proj[1]],
                                       [x*lambda3p for x in points_proj[2]]])
    projection_matrix_prim = np.transpose(projection_matrix_prim)
    
    P = projection_matrix_prim.dot(np.linalg.inv(projection_matrix))
    return (P, lambda1, lambda2, lambda3)

def naive(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original): 
    img_copy = Image.new('RGB', (img_original.size[0], img_original.size[1]), "black")

    coords = zip(xs, ys)
    for (a,b) in coords:
        a = a * img_original.size[0] / proj_width
        b = img_original.size[1] * b / proj_height
        point = [a, b, 1]
        points.append(point)

    coords = zip(xs_proj, ys_proj)
    for (a,b) in coords:
        a = a * img_original.size[0] / proj_width
        b = img_original.size[1] * b / proj_height
        point_proj = [a, b, 1]
        points_proj.append(point_proj)

    (P, lambda1, lambda2, lambda3) = projection_matrix_P(points, points_proj)
    P_inverse = np.linalg.inv(P)

    cols = img_copy.size[0]
    rows = img_copy.size[1]

    for i in range(cols):        
        for j in range(rows):    
            new_coordinates = P_inverse.dot([i, j, 1]) # lambda * X' = P * X
            new_coordinates = [x / new_coordinates[2] / lambda3  for x in new_coordinates]
            
            if (new_coordinates[0] >= 0 and new_coordinates[0] < cols-1 and \
            new_coordinates[1] >= 0 and new_coordinates[1] < rows-1):
                #tmp1 = img.getpixel((math.floor(new_coordinates[0]), math.floor(new_coordinates[1])))
                tmp2 = img_original.getpixel((math.ceil(new_coordinates[0]), math.ceil(new_coordinates[1])))
                img_copy.putpixel((i, j), tmp2)

    img_copy.save("out.bmp")

def dlt(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original):
    img_copy = Image.new('RGB', (img_original.size[0], img_original.size[1]), "black")

    coords = zip(xs, ys)
    for (a,b) in coords:
        a = a * img_original.size[0] / proj_width
        b = img_original.size[1] * b / proj_height
        point = [a, b, 1]
        points.append(point)

    coords = zip(xs_proj, ys_proj)
    for (a,b) in coords:
        a = a * img_original.size[0] / proj_width
        b = img_original.size[1] * b / proj_height
        point_proj = [a, b, 1]
        points_proj.append(point_proj)

    big_matrix = []
    for i in range(len(xs)):
        big_matrix.append( [0, 0, 0, 
            -points_proj[i][2]*points[i][0], -points_proj[i][2]*points[i][1], -points_proj[i][2]*points[i][2], 
            points_proj[i][1]*points[i][0], points_proj[i][1]*points[i][1], points_proj[i][1]*points[i][2]])
        
        big_matrix.append([points_proj[i][2]*points[i][0], points_proj[i][2]*points[i][1], points_proj[i][2]*points[i][2],
            0, 0, 0,
            -points_proj[i][0]*points[i][0], -points_proj[i][0]*points[i][1], -points_proj[i][0]*points[i][2]])

    
    U, D, V = np.linalg.svd(big_matrix, full_matrices = True)
    V[8].round()
    P_matrix_DLT = V[8]
    P_matrix_DLT = np.array(P_matrix_DLT).reshape((3, 3))
    P_matrix_DLT_inverse = np.linalg.pinv(P_matrix_DLT)

    print(P_matrix_DLT)

    cols = img_copy.size[0]
    rows = img_copy.size[1]

    for i in range(cols):        
        for j in range(rows):    
            new_coordinates = P_matrix_DLT_inverse.dot([i, j, 1])
            
            if (new_coordinates[0] >= 0 and new_coordinates[0] < cols-1 and \
            new_coordinates[1] >= 0 and new_coordinates[1] < rows-1):
                #tmp1 = img.getpixel((math.floor(new_coordinates[0]), math.floor(new_coordinates[1])))
                tmp2 = img_original.getpixel((math.ceil(new_coordinates[0]), math.ceil(new_coordinates[1])))
                img_copy.putpixel((i, j), tmp2)

    img_copy.save("out.bmp")