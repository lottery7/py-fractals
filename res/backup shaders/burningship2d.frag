#version 430

#define PI 3.141592654

uniform int MAX_ITER;
uniform vec2 RES;
uniform dvec2 OFFSET;
uniform double ZOOM;
uniform int DRAW_LINES;
uniform float PHI;
uniform vec4 COLOR;
uniform float POWER;
uniform int AA;

out vec4 frag_color;

dvec2 zsqr(dvec2 z) { return dvec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y); }
dvec2 zmul(dvec2 a, dvec2 b) { return dvec2(a.x*b.x - a.y*b.y, a.x*b.y + a.y*b.x); }

vec3 apply_color(float i)
{
	return 0.5 - 0.5 * cos(i*POWER*0.025 + COLOR.rgb);
}

float compute(vec2 frag_coord)
{
	dvec2 c = 2.0 * frag_coord - RES.xy;
	c = c / min(RES.x, RES.y) / ZOOM + OFFSET;
	mat2 rot = mat2(cos(PI*PHI), -sin(PI*PHI), sin(PI*PHI), cos(PI*PHI));
	c = rot*(c-OFFSET) + OFFSET;

	dvec2 z = c;
	int i = 0;
	const float lim = 512.0;
	while (dot(z, z) < lim && ++i < MAX_ITER)
	{
		dvec2 z0 = dvec2(abs(z.x), -abs(z.y));
		z = z0;
		for(int j = 1; j < POWER; j++)
			z = zmul(z, z0);
		z += c;
	}
	if (i >= MAX_ITER) return 0.0;

	// Smooth color
	vec2 zf = vec2(z);
	float l = float(i);
	float sl = l - log( log(dot(zf, zf)) / log(lim) ) / log(POWER);
	return sl;
}

vec3 render(vec2 frag_coord)
{
	float iterations = compute(frag_coord);
	vec3 col = apply_color(iterations);
	return col;
}

void main() {
	if (bool(DRAW_LINES))
	{
		vec2 pos = gl_FragCoord.xy;
		if (int(pos.x) == int(RES.x / 2) || int(pos.y) == int(RES.y / 2))
		{
			frag_color = vec4(1, 0, 0, 1);
			return;
		}
	}

	vec3 col = vec3(0);
    for (int i = 0; i < AA; i++)
    for (int j = 0; j < AA; j++)
        col += render(gl_FragCoord.xy + vec2(i, j) / float(AA));
    col /= float(AA*AA);
	frag_color = vec4(col, 1);
}
