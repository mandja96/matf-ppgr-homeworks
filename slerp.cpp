#define GL_SILENCE_DEPRECATION
#define TIMER_INTERVAL 50
#define TIMER_ID 0

#include "transform.hpp"
#include <GLUT/glut.h>

static float animation_parameter;
static int animation_active;

static void on_display(void);
static void on_reshape(int width, int height);
static void on_keyboard(unsigned char key, int x, int y);
static void on_timer(int value);

static void calculate_qs(void);
static bool flag_q1_close_to_q2 = false;
Eigen::Vector4d slerp(Eigen::Vector4d& q1, Eigen::Vector4d& q2, float tm, float t);

static double x_1, x_2, y_1, y_2, z_1, z_2;
static double alpha_1, beta_1, gamma_1;
static double alpha_2, beta_2, gamma_2; 
static double x_cur, y_cur, z_cur;
static double alpha_cur, beta_cur, gamma_cur;

static Eigen::Matrix3d matrix_A;
static std::pair<Eigen::Vector3d, double> axis_angle;
static Eigen::Vector4d q_1;
static Eigen::Vector4d q_2;
static Eigen::Vector4d q_s;

static double cos_angle;
static double angle;
static double tm;

static void draw_object(void);
static void draw_axis(void);
static void draw_start_and_end(void);

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
    tm = 3;
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
                glutTimerFunc(TIMER_INTERVAL, on_timer, TIMER_ID);
            }
            break;

        case 'n':
        case 'N':
            if(!animation_active){
                animation_active = 1;
                glutTimerFunc(TIMER_INTERVAL, on_timer, TIMER_ID);
            }
        case 's':
        case 'S':
            animation_active = 0;
            break;
        case 'r':
        case 'R':   
            animation_active = 0; 
            animation_parameter = 0;
            glutPostRedisplay();
            break;
    }
}

static void on_timer(int value)
{
    if (value != TIMER_ID)
        return;

    if(animation_parameter >= tm-0.08){    
        animation_active = 0;
        glutPostRedisplay();
    }

    animation_parameter += 0.05;
    glutPostRedisplay();

    if (animation_active) {
        glutTimerFunc(TIMER_INTERVAL, on_timer, TIMER_ID);
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
    gluLookAt(4, 4, 4, 
              0, 0, 0, 
              0, 1, 0);

    glPushMatrix();
        glScalef(4, 4, 4);
        draw_axis();
    glPopMatrix();

    glLineWidth(5);
    glPushMatrix();
        draw_object();
    glPopMatrix();

    glPushMatrix();
        draw_start_and_end();
    glPopMatrix();

    glutSwapBuffers();
}

static void draw_start_and_end(void){
    glPushMatrix();
        glColor3f(.6, .6, .6);
        std::pair<Eigen::Vector3d, double> q2_axis_angle = Q2AxisAngle(q_1);    
        Eigen::Matrix3d matrix_A = Rodrigez(q2_axis_angle.first, q2_axis_angle.second);
        GLdouble matrixTransform[16] = 
            {matrix_A(0, 0), matrix_A(1, 0), matrix_A(2,0), 0,
             matrix_A(0, 1), matrix_A(1, 1), matrix_A(2,1), 0,
             matrix_A(0, 2), matrix_A(1, 2), matrix_A(2,2), 0,
             x_1, y_1, z_1, 1};        
    
        glMultMatrixd(matrixTransform);
        glPushMatrix();
            glLineWidth(2);
            glScalef(0.4, 0.4, 0.4);
            glutWireIcosahedron();
        glPopMatrix();
        draw_axis();

    glPopMatrix();

    glPushMatrix();
        glColor3f(.6, .6, .6);
        q2_axis_angle = Q2AxisAngle(q_2);    
        matrix_A = Rodrigez(q2_axis_angle.first, q2_axis_angle.second);
        GLdouble matrixTransform2[16] = 
            {matrix_A(0, 0), matrix_A(1, 0), matrix_A(2,0), 0,
             matrix_A(0, 1), matrix_A(1, 1), matrix_A(2,1), 0,
             matrix_A(0, 2), matrix_A(1, 2), matrix_A(2,2), 0,
             x_2, y_2, z_2, 1};        
    
        glMultMatrixd(matrixTransform2);
        glPushMatrix();
            glLineWidth(2);
            glScalef(0.4, 0.4, 0.4);
            glutWireIcosahedron();
        glPopMatrix();
        draw_axis();

    glPopMatrix();
}

static void draw_object(void){
    glPushMatrix();
        glColor3f(.9, .9, .9);


        // alpha_cur = (1-animation_parameter/tm)*alpha_1 + animation_parameter/tm*alpha_2; 
        // beta_cur = (1-animation_parameter/tm)*beta_1 + animation_parameter/tm*beta_2;
        // gamma_cur = (1-animation_parameter/tm)*gamma_1 + animation_parameter/tm*gamma_2;

        // Eigen::Matrix3d matrix_A = Euler2A(alpha_cur, beta_cur, gamma_cur);

        x_cur = (1-animation_parameter/tm)*x_1 + animation_parameter/tm*x_2;
        y_cur = (1-animation_parameter/tm)*y_1 + animation_parameter/tm*y_2;
        z_cur = (1-animation_parameter/tm)*z_1 + animation_parameter/tm*z_2;

        if(flag_q1_close_to_q2){
            q_s = q_1;
            flag_q1_close_to_q2 = false;
        }
        else {
            q_s = slerp(q_1, q_2, tm, animation_parameter);
        }

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
            glScalef(0.4, 0.4, 0.4);
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
    x_1 = 2; y_1 = 2; z_1 = 0;
    x_2 = -2; y_2 = 0; z_2 = 2;
    alpha_1 = -PI/6; beta_1 = PI; gamma_1 = 3*PI/4;
    alpha_2 = -PI/2; beta_2 = PI/3; gamma_2 = 3*PI/2;

    matrix_A = Euler2A(alpha_1, beta_1, gamma_1);
    axis_angle = AxisAngle(matrix_A);
    q_1 = AxisAngle2Q(axis_angle.first, axis_angle.second);

    matrix_A = Euler2A(alpha_2, beta_2, gamma_2);
    axis_angle = AxisAngle(matrix_A);
    q_2 = AxisAngle2Q(axis_angle.first, axis_angle.second);

    // jedinicni su
    cos_angle = q_1.dot(q_2);

    // hocemo da idemo kracim putem, pa obrnemo kvaternion 
    if(cos_angle < 0){
        q_1 = -q_1;
        cos_angle = -cos_angle;
    }

    if(cos_angle > 0.95){
        // vrati q1 kao qs ili radi lerp
        flag_q1_close_to_q2 = true;
    }

    angle = acos(cos_angle);
}

Eigen::Vector4d slerp(Eigen::Vector4d& q1, Eigen::Vector4d& q2, float tm, float t){
    Eigen::Vector4d res;
    
    res = sin(angle*(1-t/tm))/sin(angle)*q_1 
            + sin(angle*t/tm)/sin(angle)*q_2;
    return res;
}
