#include "udf.h"

DEFINE_CG_MOTION(simple_vibration, dt, vel, omega, time, dtime) {

	real A, f, t, rot_freq;
	A = RP_Get_Real("user/vibration_amplitude");
	f = RP_Get_Real("user/vibration_frequency");
	t = CURRENT_TIME;
	rot_freq = 2 * M_PI * f;

	vel[0] = 0;
	vel[1] = 0;
	vel[2] = A * rot_freq * sin(rot_freq * t); /* Derivative of A * (1 - cos(rot_freq * t)) wrt t */
}


DEFINE_CG_MOTION(noisy_vibration, dt, vel, omega, time, dtime) {

	real A, f, noise_A, noise_f, t, rot_freq, noise_rot_freq;
	A       = RP_Get_Real("user/vibration_amplitude");
	f       = RP_Get_Real("user/vibration_frequency");
	noise_A = RP_Get_Real("user/noise_amplitude");
	noise_f = RP_Get_Real("user/noise_frequency");
	t = CURRENT_TIME;
	rot_freq       = 2 * M_PI * f;
	noise_rot_freq = 2 * M_PI * noise_f;

	vel[0] = 0;
	vel[1] = 0;
	vel[2] = (A * rot_freq * sin(rot_freq * t)) + (noise_A * noise_rot_freq * sin(noise_rot_freq * t));
}