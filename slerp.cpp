#define GL_SILENCE_DEPRECATION
#define TIMER_INTERVAL 50

#include "transform.hpp"
#include <GLUT/glut.h>

static float animation_parameter;
static int animation_active;

static void on_display(void);
static void on_reshape(int width, int height);
static void on_keyboard(unsigned char key, int x, int y);
static void on_timer(int value);

static void calculate_qs(void);
static double x_1, x_2, y_1, y_2, z_1, z_2;
static double alpha_1, beta_1, gamma_1; 
static double alpha_2, beta_2, gamma_2; 
static double x_cur, y_cur, z_cur;
// static double alpha_cur, beta_cur, gamma_cur;

static Eigen::Matrix3d matrix_A;
static std::pair<Eigen::Vector3d, double> axis_angle;
static Eigen::Vector4d q_1;
static Eigen::Vector4d q_2;
static Eigen::Vector4d q_s;

static double cos_angle;
static double angle;

static void draw_object(void);
static void draw_axis(void);

int main(int argc, char* argv[]){
    
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE);

    glutInitWindowSize(600, 600);
    glutInitWindowPosition(100, 100);
    glutCreateWindow(argv[0]);

    glutDisplayFunc(on_display);
    glutReshapeFunc(on_reshape);
    glutKeyboardFunc(on_keyboard);

    animation_active = 0;
    animation_parameter = 0;

    calculate_qs();

    glClearColor(.05, .05, .05, 0);
    glutMainLoop();
    return 0;
}

static void on_keyboard(unsigned char key, int x, int y){
    switch(key){
        case 27:
            exit(0);
            break;
        case 'g':
        case 'G':
            if(!animation_active){
                animation_parameter = 0;
                animation_active = 1;
                glutTimerFunc(TIMER_INTERVAL, on_timer, 0);
            }
            break;
        case 's':
        case 'S':
            animation_active = 0;
            break;
        case 'r':
        case 'R':
            animation_parameter = 0;
            animation_active = 0;
            glutPostRedisplay();
            break;
    }
}

static void on_timer(int value)
{
    if (value != 0)
        return;

    if(x_cur>= x_2){    
        animation_active = 0;
        glutPostRedisplay();
    }

    animation_parameter += 0.1;
    glutPostRedisplay();

    if (animation_active) {
        glutTimerFunc(TIMER_INTERVAL, on_timer, value);
    }
}

static void on_reshape(int width, int height)
{
    glViewport(0, 0, 2*width, 2*height);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(60, (float) width / height, 1, 200);
}


static void on_display(void){
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    gluLookAt(7, 7, 7, 
              0, 0, 0, 
              0, 1, 0);

    glPushMatrix();
        glScalef(5, 5, 5);
        draw_axis();
    glPopMatrix();

    glLineWidth(5);
    glPushMatrix();
        draw_object();
    glPopMatrix();

    glutSwapBuffers();
}

static void draw_object(void){
    glPushMatrix();
        glColor3f(.9, .9, .9);

        // alpha_cur = (1-animation_parameter/5)*alpha_1 + animation_parameter/5*alpha_2; 
        // beta_cur = (1-animation_parameter/5)*beta_1 + animation_parameter/5*beta_2;
        // gamma_cur = (1-animation_parameter/5)*gamma_1 + animation_parameter/5*gamma_2;

        // std::cout << "alfa: " << alpha_cur << std::endl;
        // std::cout << "beta: " << beta_cur << std::endl;
        // std::cout << "gama: " << gamma_cur << std::endl;

        // Eigen::Matrix3d matrix_A = Euler2A(alpha_cur, beta_cur, gamma_cur);


        x_cur = (1-animation_parameter/5)*x_1 + animation_parameter/5*x_2;
        y_cur = (1-animation_parameter/5)*y_1 + animation_parameter/5*y_2;
        z_cur = (1-animation_parameter/5)*z_1 + animation_parameter/5*z_2;

        q_s = sin(angle*(1-animation_parameter/5))/sin(angle)*q_1 
            + sin(angle*animation_parameter/5)/sin(angle)*q_2;

        std::pair<Eigen::Vector3d, double> q2_axis_angle = Q2AxisAngle(q_s);    
        Eigen::Matrix3d matrix_A = Rodrigez(q2_axis_angle.first, q2_axis_angle.second);
        GLdouble matrixTransform[16] = 
            {matrix_A(0, 0), matrix_A(1, 0), matrix_A(2,0), 0,
             matrix_A(0, 1), matrix_A(1, 1), matrix_A(2,1), 0,
             matrix_A(0, 2), matrix_A(1, 2), matrix_A(2,2), 0,
             x_cur, y_cur, z_cur, 1};        
                
        glMultMatrixd(matrixTransform);
        glPushMatrix();
            glLineWidth(2);
            glScalef(0.5, 0.5, 0.5);
            glutWireIcosahedron();
        glPopMatrix();
        draw_axis();

    glPopMatrix();
}

static void draw_axis(void){
    glPushMatrix();
        glBegin(GL_LINES);
            glColor3f(1, .3, .3);
            glVertex3f(0, 0, 0);
            glVertex3f(1, 0, 0);

            glColor3f(.3, 1, .3);
            glVertex3f(0, 0, 0);
            glVertex3f(0, 1, 0);

            glColor3f(.3, .3, 1);
            glVertex3f(0, 0, 0);
            glVertex3f(0, 0, 1);
        glEnd();
    glPopMatrix();
}   

static void calculate_qs(void){
    x_1 = 0; y_1 = 0; z_1 = 5;
    x_2 = 3; y_2 = 4; z_2 = 5;
    alpha_1 = 0; beta_1 = 0; gamma_1 = 5 * PI / 6;
    alpha_2 = PI/2; beta_2 = 0.0; gamma_2 = PI/2;

    matrix_A = Euler2A(alpha_1, beta_1, gamma_1);
    axis_angle = AxisAngle(matrix_A);
    q_1 = AxisAngle2Q(axis_angle.first, axis_angle.second);

    matrix_A = Euler2A(alpha_2, beta_2, gamma_2);
    axis_angle = AxisAngle(matrix_A);
    q_2 = AxisAngle2Q(axis_angle.first, axis_angle.second);

    std::cout << q_1 << std::endl;
    std::cout << q_2 << std::endl;

    cos_angle = q_1.dot(q_2);
    if(cos_angle < 0){
        q_1 = -q_1;
        cos_angle = -cos_angle;
    }

    angle = acos(cos_angle);
}