#include "udf.h"

DEFINE_CG_MOTION(simple_vibration,dt,vel,omega,time,dtime){
	
	real A; real f;
	real t = CURRENT_TIME;
	real PI = 3.14159265358979323846;
	
	A = RP_Get_Real("user/vibration_amplitude");
	f = RP_Get_Real("user/vibration_frequency");

	real rot_freq = 2*PI*f;

	vel[0] = 0; 
	vel[1] = 0;
	vel[2] = A * rot_freq * sin(rot_freq * t); // Derivative of A * (1 - cos(rot_freq t)) wrt t
}