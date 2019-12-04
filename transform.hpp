#ifndef _TRANSFORM_
#define _TRANSFORM_

#include <iostream>
#include <vector>
#include <math.h>

#include "Eigen/Eigen/Eigen"

#define PI 3.141592653


Eigen::Matrix3d Euler2A(const double& phi, 
                        const double& theta, 
                        const double& psi);

std::pair<Eigen::Vector3d, double> AxisAngle(Eigen::Matrix3d& A);
Eigen::Matrix3d Rodrigez(Eigen::Vector3d p, const double& angle);
std::vector<double> A2Euler(Eigen::Matrix3d A);
Eigen::Vector4d AxisAngle2Q(Eigen::Vector3d p, double angle);
std::pair<Eigen::Vector3d, double> Q2AxisAngle(Eigen::Vector4d q);

#endif