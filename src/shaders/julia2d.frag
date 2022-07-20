#version 120

#define PI 3.141592654

uniform int MAX_ITER;
uniform vec2 RES;
uniform vec2 OFFSET;
uniform float ZOOM;
uniform int DRAW_LINES;
uniform vec2 C;
uniform float PHI;
uniform vec4 COLOR;
uniform float POWER;
uniform int AA;

vec2 zsqr(vec2 z) { return vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y); }
vec2 zmul(vec2 a, vec2 b) { return vec2(a.x*b.x - a.y*b.y, a.x*b.y + a.y*b.x); }
vec2 zdiv(vec2 a, vec2 b)
{
	float real = (a.x * b.x + a.y * b.y) / (b.x * b.x + b.y * b.y);
	float imagine = (a.y * b.x - a.x * b.y) / (b.x * b.x + b.y * b.y);
	return vec2(real, imagine);
}
vec2 zexp(vec2 a)
{
	return exp(a.x)*vec2(cos(a.y), sin(a.y));
}

vec3 apply_color(float i)
{
	return 0.5 - 0.5 * cos(i*POWER*0.025 + COLOR.rgb);
}

float compute(vec2 frag_coord)
{
	// Computing z value
	vec2 z = 2.0 * frag_coord - RES.xy;
	z = z / min(RES.x, RES.y) / ZOOM + OFFSET;
	mat2 rot = mat2(cos(PI*PHI), -sin(PI*PHI), sin(PI*PHI), cos(PI*PHI));
	z = rot*(z-OFFSET) + OFFSET;

	// Main computing
	int i = 0;
	const float lim = 512.0;
	while (dot(z, z) < lim && ++i < MAX_ITER)
	{
		vec2 z0 = z;
		for (int j = 1; j < POWER; j++)
			z = zmul(z0, z);
		z += C;
	}
	if (i == MAX_ITER) return 0.0;

	// Smooth color
	vec2 zf = vec2(z);
	float l = float(i);
	float sl = l - log( log(dot(zf, zf)) / log(lim) ) / log(POWER);
	return sl;
}

vec3 render(vec2 frag_coord)
{
	float iterations = compute(frag_coord);
	vec3 color = apply_color(iterations);
	return color;
}

void main()
{
	if (bool(DRAW_LINES))
	{
		vec2 pos = gl_FragCoord.xy;
		if (int(pos.x) == int(RES.x / 2) || int(pos.y) == int(RES.y / 2))
		{
			gl_FragColor = vec4(1, 0, 0, 1);
			return;
		}
	}

	vec3 col = vec3(0);
    for (int i = 0; i < AA; i++)
    for (int j = 0; j < AA; j++)
        col += render(gl_FragCoord.xy + vec2(i, j) / float(AA));
    col /= float(AA*AA);
	gl_FragColor = vec4(col, 1);
}