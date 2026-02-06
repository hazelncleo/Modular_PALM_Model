#include "udf.h"

DEFINE_CG_MOTION(noisy_vibration,dt,vel,omega,time,dtime){
	
	real A; real noise_A;
	real f; real noise_f;
	real t = CURRENT_TIME;
	real PI = 3.14159265358979323846;
	
	A       = RP_Get_Real("user/vibration_amplitude");
	f       = RP_Get_Real("user/vibration_frequency");
	noise_A = RP_Get_Real("user/noise_amplitude");
	noise_f = RP_Get_Real("user/noise_frequency");
	
	real rot_freq       = 2 * PI * f;
	real noise_rot_freq = 2 * PI * noise_f;

	vel[0] = 0; 
	vel[1] = 0;
	vel[2] = (A * rot_freq * sin(rot_freq * t)) + (noise_A * noise_rot_freq * sin(noise_rot_freq * t));
}