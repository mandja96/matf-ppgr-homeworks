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
void Q2AxisAngle(Eigen::Vector4d q);

int main(){
    double phi, theta, psi;
    
    /* Test primer 1 */
    
    //phi = -0.244978663;
    //theta = -1.09491408;
    //psi = 1.32581766;
    
    /* Moj test primer */
    phi = 20 * PI / 180;
    theta = -45 * PI / 180;
    psi = -60 * PI / 180;

    std::cout << std::endl << "Uneti uglovi su: " << std::endl;
    std::cout << phi * 180 / PI << ", " << theta * 180 / PI << ", " << psi * 180 / PI << std::endl << std::endl; 
    std::cout << "---------------------------------------------" << std::endl;
    auto M = Euler2A(phi, theta, psi);
    auto par = AxisAngle(M);
    Eigen::Vector3d p = par.first;
    double angle = par.second;

    auto A = Rodrigez(p, angle);
    
    std::vector<double> uglovi = A2Euler(A);

    auto q = AxisAngle2Q(p, angle);
    Q2AxisAngle(q);

    return 0;
}

Eigen::Matrix3d Euler2A(const double& phi, 
                        const double& theta, 
                        const double& psi){
    std::cout << "Euler2A" << std::endl << std::endl;

    Eigen::Matrix3d Rx;
    Rx << 1, 0, 0,
          0, cos(phi), -sin(phi),
          0, sin(phi), cos(phi);
   
    Eigen::Matrix3d Ry; 
    Ry << cos(theta), 0, sin(theta),
          0, 1, 0,
         -sin(theta), 0, cos(theta);

    Eigen::Matrix3d Rz;
    Rz << cos(psi), -sin(psi), 0,
          sin(psi), cos(psi), 0,
          0, 0, 1;
                
    Eigen::Matrix3d M;
    M << cos(theta)*cos(psi),
         cos(psi)*sin(theta)*sin(phi)-cos(phi)*sin(psi),
         cos(phi)*cos(psi)*sin(theta)+sin(phi)*sin(psi),
         cos(theta)*sin(psi),
         cos(phi)*cos(psi)+sin(theta)*sin(phi)*sin(psi),
         cos(phi)*sin(theta)*sin(psi)-cos(psi)*sin(phi),
         -sin(theta),
         cos(theta)*sin(phi),
         cos(theta)*cos(phi);

    std::cout << "Rezultat Euler2A: " << std::endl;
    std::cout << M << std::endl << std::endl;
    std::cout << "Matrica dobijena mnozenjem Rz*Ry*Rx:" << std::endl;
    std::cout << Rz*Ry*Rx << std::endl << std::endl;

    std::cout << "---------------------------------------------" << std::endl;
    return M;    
}


std::pair<Eigen::Vector3d, double> AxisAngle(Eigen::Matrix3d& A){
    std::cout << "AxisAngle" << std::endl << std::endl;

    Eigen::Vector3d p;
    p << 0, 0, 0;
    double angle = 0.0;
    Eigen::Vector3d u, u_p;
    int determinant = A.determinant();

    // A.T * A = E znači da kolone matrice A
    // predstavljaju ortonormirani reper prostora koji
    // je slika baznog repera    
    auto tmp = A.transpose() * A;
    if(tmp.isIdentity()){
        std::cout << "Matrica A.T*A jeste jedinična." << std::endl;
        //std::cout << tmp << std::endl <<std::endl;
    }

    if( tmp.isIdentity() && determinant == 1 ){
        // matrica A JESTE matrica kretanja

        Eigen::Vector3d firstRow = A.row(0);
        firstRow(0) = firstRow(0) - 1;
        Eigen::Vector3d secondRow = A.row(1);
        secondRow(1) = secondRow(1) - 1;
        Eigen::Vector3d thirdRow = A.row(2);
        thirdRow(2) = thirdRow(2) - 1;

        firstRow = firstRow.normalized();
        secondRow = secondRow.normalized();
        thirdRow = thirdRow.normalized();

        Eigen::Vector3d zeroVector;
        zeroVector << 0, 0, 0;
        Eigen::Vector3d cross1 = firstRow.cross(secondRow);
        if ( cross1 != zeroVector ){
            p << cross1(0), cross1(1), cross1(2);
        }
        else {
            Eigen::Vector3d cross2 = firstRow.cross(thirdRow);
            if ( cross2 != zeroVector ) {
                p << cross2(0), cross2(1), cross2(2);
            }
            else {
                Eigen::Vector3d cross3 = secondRow.cross(thirdRow);
                p << cross3(0), cross3(1), cross3(2);
            }
        }
        p = p.normalized();
        
        u = A.row(0);
        u(0) = u(0) - 1;
        if( u == zeroVector ){
            u = A.row(1);
            u(1) = u(1) - 1;
            
            if ( u == zeroVector ){
                u = A.row(2);
                u(2) = u(2) - 1;
            }
        } 
        u = u.normalized();

        u_p = A * u;
        u_p = u_p.normalized();
        angle = acos(u.dot(u_p));
    }

    else{
        // matrica A NIJE matrica kretanja
        std::cout << "Matrix is not valid." << std::endl;
    }

    std::cout << "Vektor p: " << std::endl << p << std::endl << std::endl;
    std::cout << "Ugao φ u radijanima: " << angle << std::endl;
    std::cout << "Ugao φ u stepenima: " << angle * 180 / PI << std::endl << std::endl;

    std::cout << "Mešoviti proizvod [u, up, p] = ";
    Eigen::Matrix3f mixedProductMatrix;
    mixedProductMatrix << u(0), u(1), u(2), 
                          u_p(0), u_p(1), u_p(2),
                          p(0), p(1), p(2);

    double mixedProduct = mixedProductMatrix.determinant();
    std::cout << mixedProduct << std::endl;

    if(mixedProduct < 0){
        std::cout << "Menjamo smer. Vektor oko kog rotiramo je sada: " << std::endl <<
            -p << std::endl << std::endl;
        p = -p;
    }
    else{
        std::cout << "Ne menjamo smer vektora p!" << std::endl << std::endl;
    }

    std::pair<Eigen::Vector3d, double> par = {p, angle};
    std::cout << "---------------------------------------------" << std::endl;
    return par;
}

Eigen::Matrix3d Rodrigez(Eigen::Vector3d p, const double& angle){
    std::cout << "Rodrigez" << std::endl << std::endl;
    Eigen::Matrix3d px;
    px << 0, -p(2), p(1),
         p(2), 0, -p(0),
        -p(1), p(0), 0;

    Eigen::Matrix3d R;
    Eigen::Matrix3d E;
    E << 1, 0, 0, 
         0, 1, 0, 
         0, 0, 1;
    R = p*p.transpose() + cos(angle)*(E - p*p.transpose()) + sin(angle)*px;

    std::cout << "Matrica rotacije dobijena Rodrigezovom formulom: " << std::endl;
    std::cout << R << std::endl;
    std::cout << "---------------------------------------------" << std::endl;
    return R;
}

// vraca φ, θ, ψ
std::vector<double> A2Euler(Eigen::Matrix3d A){
    std::cout << "A2Euler" << std::endl << std::endl;
    std::vector<double> angles;
    double psi, theta, phi;

    std::cout << "Determinanta ulazne matrice = " << A.determinant() << std::endl << std::endl;  

    if(A(2,0) < 1){
        if(A(2,0) > -1){
            psi = atan2(A(1,0), A(0,0));
            theta = asin(-A(2,0));
            phi = atan2(A(2,1), A(2,2));
        } 
        else {
            psi = atan2(-A(0,1), A(1,1));
            theta = PI/2;
            phi = 0;
        }
    }
    else {
        psi = atan2(-A(0,1), A(1,1));
        theta = -PI/2;
        phi = 0;
    }

    std::cout << "φ = " << phi << " [rad]" << std::endl;
    std::cout << "θ = " << theta << " [rad]" << std::endl;
    std::cout << "ψ = " << psi << " [rad]" << std::endl << std::endl;
    std::cout << "φ = " << phi * 180 / PI << " [stepeni]" << std::endl;
    std::cout << "θ = " << theta * 180 / PI << " [stepeni]" << std::endl;
    std::cout << "ψ = " << psi * 180 / PI << " [stepeni]" << std::endl << std::endl;

    std::cout << "---------------------------------------------" << std::endl;
    return angles;
} 

// vraca jednicni kvaternion q = (x,y,z,w) tako da
// Cq = Rp(φ). Vektor p je jednicni.
Eigen::Vector4d AxisAngle2Q(Eigen::Vector3d p, double phi){
    std::cout << "AxisAngle2Q" << std::endl << std::endl;

    Eigen::Vector4d q;
    double w;

    w = cos(phi/2);
    p = p.normalized();

    auto x = sin(phi/2) * p(0);
    auto y = sin(phi/2) * p(1);
    auto z = sin(phi/2) * p(2);

    q << x, y, z, w;   

    std::cout << "Kvaternion q: (" << x << ", " << y << ", " << z << ", "
        << w << ")" << std::endl << std::endl;

    std::cout << "---------------------------------------------" << std::endl;
    return q;
}

void Q2AxisAngle(Eigen::Vector4d q){
    std::cout << "Q2AxisAngle" << std::endl << std::endl;

    Eigen::Vector3d p;
    double angle = 0.0;

    q = q.normalized();


    if (q(3) < 0){
        q = -q;
    }
    angle = 2*acos(q(3));

    if(abs(q(3)) == 1){
        p << 1, 0, 0;
    }
    else {
        p << q(0), q(1), q(2);
        p = p.normalized();
    }

    std::cout << "Ugao je: " << angle << " [rad]"<< std::endl;
    std::cout << "Ugao je: " << angle*180/PI << " [stepeni]"<< std::endl;
    std::cout << "Vektor p je: " <<std::endl << p << std::endl << std::endl;
    std::cout << "---------------------------------------------" << std::endl;
}
