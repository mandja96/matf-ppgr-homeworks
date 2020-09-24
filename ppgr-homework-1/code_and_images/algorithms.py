import numpy as np
import math
from PIL import Image

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

def transform_coordinates(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original):
    points = []
    points_proj = []

    coords = zip(xs, ys)
    for (a,b) in coords:
        a = ( a * img_original.size[0] ) / proj_width
        b = ( img_original.size[1] * b ) / proj_height
        point = [a, b, 1]
        points.append(point)

    coords = []
    coords = zip(xs_proj, ys_proj)
    for (a,b) in coords:
        a = ( a * img_original.size[0] ) / proj_width
        b = ( img_original.size[1] * b ) / proj_height
        point_proj = [a, b, 1]
        points_proj.append(point_proj)

    return (points, points_proj)

def naive(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original): 
    points, points_proj = transform_coordinates(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original)

    img_copy = Image.new('RGB', (img_original.size[0], img_original.size[1]), "black")

    (P, _, _, _) = projection_matrix_P(points, points_proj)
    P_inverse = np.linalg.inv(P)

    cols = img_copy.size[0]
    rows = img_copy.size[1]

    for i in range(cols):        
        for j in range(rows):    
            new_coordinates = P_inverse.dot([i, j, 1]) # lambda * X' = P * X
            new_coordinates = [(t / new_coordinates[2]) for t in new_coordinates]
            
            if (new_coordinates[0] >= 0 and new_coordinates[0] < cols-1 and \
            new_coordinates[1] >= 0 and new_coordinates[1] < rows-1):
                tmp1 = img_original.getpixel((math.floor(new_coordinates[0]), math.floor(new_coordinates[1])))
                tmp2 = img_original.getpixel((math.ceil(new_coordinates[0]), math.ceil(new_coordinates[1])))
                img_copy.putpixel((i, j), tmp1)
                img_copy.putpixel((i, j), tmp2)
    img_copy.save("out.bmp")

def naive_return(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original): 
    points, points_proj = transform_coordinates(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original)

    (P, _, _, _) = projection_matrix_P(points, points_proj) 
    return P

def dlt(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original):
    P = naive_return(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original)

    img_copy = Image.new('RGB', (img_original.size[0], img_original.size[1]), "black")
    points, points_proj = transform_coordinates(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original)
    
    P_matrix_DLT = dlt_basic(points, points_proj)

    P_scaled = [(x / P_matrix_DLT[0] * P[0][0]) for x in P_matrix_DLT]
    P_matrix_DLT_reshaped = np.array(P_scaled).reshape((3, 3))
    P_matrix_DLT_inverse = np.linalg.inv(P_matrix_DLT_reshaped)

    cols = img_copy.size[0]
    rows = img_copy.size[1]

    for i in range(cols):        
        for j in range(rows):    
            new_coordinates = P_matrix_DLT_inverse.dot([i, j, 1])
            new_coordinates = [(x / new_coordinates[2]) for x in new_coordinates]
            
            if (new_coordinates[0] >= 0 and new_coordinates[0] < cols-1 and \
                new_coordinates[1] >= 0 and new_coordinates[1] < rows-1):
                tmp1 = img_original.getpixel((math.floor(new_coordinates[0]), math.floor(new_coordinates[1])))
                tmp2 = img_original.getpixel((math.ceil(new_coordinates[0]), math.ceil(new_coordinates[1])))
                img_copy.putpixel((i, j), tmp1)
                img_copy.putpixel((i, j), tmp2)

    img_copy.save("out.bmp")

def dlt_basic(points, points_proj):   
    points = [[a/c, b/c, 1] for [a,b,c] in points]
    points_proj = [[a/c, b/c, 1] for [a,b,c] in points_proj] 

    big_matrix = []
    n = len(points)
    for i in range(n):
        big_matrix.append( [0, 0, 0, 
         -points_proj[i][2]*points[i][0], -points_proj[i][2]*points[i][1], -points_proj[i][2]*points[i][2], 
         points_proj[i][1]*points[i][0], points_proj[i][1]*points[i][1], points_proj[i][1]*points[i][2]])     

        big_matrix.append([points_proj[i][2]*points[i][0], points_proj[i][2]*points[i][1], points_proj[i][2]*points[i][2],
         0, 0, 0,
         -points_proj[i][0]*points[i][0], -points_proj[i][0]*points[i][1], -points_proj[i][0]*points[i][2]])

    _, _, V = np.linalg.svd(big_matrix, full_matrices = True)
    P_matrix_DLT = V[8]*(-1) # (-1 jer eto u Pythonu je tako čudno)
    return P_matrix_DLT    

def dlt_basic_scaled(points, points_proj):    
    points = [[a/c, b/c, 1] for [a,b,c] in points]
    points_proj = [[a/c, b/c, 1] for [a,b,c] in points_proj]

    P_matrix_DLT = dlt_basic(points, points_proj)
    #P_matrix_DLT = P_matrix_DLT.reshape((3,3))
    P_matrix, _, _, _ = projection_matrix_P(points, points_proj) 
    P_matrix_DLT_scaled = [(x / P_matrix_DLT[0] * P_matrix[0][0]) for x in P_matrix_DLT]
    P_matrix_DLT_rescaled = np.array(P_matrix_DLT_scaled).reshape((3, 3))
    return P_matrix_DLT_rescaled

def normalize(ps):
    # prvi korak je centar mase
    mass_center_x = sum([a[0] for a in ps]) / len(ps)
    mass_center_y = sum([a[1] for a in ps]) / len(ps)
    
    # drugi korak je translacija
    points_prim = [[a[0]-mass_center_x, a[1]-mass_center_y] for a in ps]
    k = homo_coeff(points_prim)

    T_matrix = [[math.sqrt(2)/k, 0, mass_center_x*(-1)],
                 [0, math.sqrt(2)/k, mass_center_y*(-1)],
                 [0, 0, 1]]
    return T_matrix

def homo_coeff(points_prim):
    coeff = sum([math.sqrt(point_prim[0]*point_prim[0] + point_prim[1]*point_prim[1])                  for point_prim in points_prim]) / len(points_prim)
    return coeff

def dlt_normalize(points, points_proj):    
    T_matrix = normalize(points) # 3x3
    T_prim_matrix = normalize(points_proj) # 3x3
    
    T_matrix = np.array(T_matrix).reshape((3,3))
    T_prim_matrix = np.array(T_prim_matrix).reshape((3,3))
  
    points = np.transpose(points) # 3x6
    points_proj = np.transpose(points_proj) # 3x6
    
    M_line = T_matrix.dot(points) # 3x6
    M_prim_line = T_prim_matrix.dot(points_proj) # 3x6
    
    M_line = np.transpose(M_line) # 6x3
    M_prim_line = np.transpose(M_prim_line) # 6x3
    dlt_matrix = dlt_basic(M_line, M_prim_line) # 3x3
    
    dlt_matrix = np.array(dlt_matrix).reshape((3, 3))
    result = (np.linalg.inv(T_prim_matrix)).dot(dlt_matrix).dot(T_matrix)

    return result

def dltN(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original):    
    img_copy = Image.new('RGB', (img_original.size[0], img_original.size[1]), "black")
    points, points_proj = transform_coordinates(xs, ys, xs_proj, ys_proj, proj_width, proj_height, img_original)

    P_matrix_DLTN = dlt_normalize(points, points_proj)
    P, _, _, _ = projection_matrix_P(points, points_proj)

    tmp = P_matrix_DLTN.flatten()
    P_scaled = [(t / tmp[0] * P[0][0]) for t in tmp]
    P_matrix_DLTN_reshaped = np.array(P_scaled).reshape((3, 3))
    P_matrix_DLTN_inverse = np.linalg.inv(P_matrix_DLTN_reshaped)

    cols = img_copy.size[0]
    rows = img_copy.size[1]

    for i in range(cols):        
        for j in range(rows):    
            new_coordinates = P_matrix_DLTN_inverse.dot([i, j, 1])
            new_coordinates = [(x / new_coordinates[2]) for x in new_coordinates]
            
            if (new_coordinates[0] >= 0 and new_coordinates[0] < cols-1 and \
                new_coordinates[1] >= 0 and new_coordinates[1] < rows-1):
                tmp1 = img_original.getpixel((math.floor(new_coordinates[0]), math.floor(new_coordinates[1])))
                tmp2 = img_original.getpixel((math.ceil(new_coordinates[0]), math.ceil(new_coordinates[1])))
                img_copy.putpixel((i, j), tmp1)
                img_copy.putpixel((i, j), tmp2)

    img_copy.save("out.bmp")