#version 120

#define MAX_RAY_LENGTH 100.0

uniform int MAX_ITER;
uniform vec2 RES;
uniform float POWER;
uniform float ZOOM;
uniform float PHI;
uniform float THETA;
uniform int CUT;
uniform vec4 COLOR;
uniform vec4 BG_COLOR;
uniform int MAX_STEPS;
uniform float AO_COEF;
uniform int SHADOWS;
uniform int AA;

// Quaternion square
vec4 qsqr( vec4 a )
{
    return vec4( a.x*a.x - a.y*a.y - a.z*a.z - a.w*a.w,
                 2.0*a.x*a.y,
                 2.0*a.x*a.z,
                 2.0*a.x*a.w);
}
// Quaternion multiplication
vec4 qmul(vec4 a, vec4 b)
{
    return vec4(
        a.x * b.x - a.y * b.y - a.z * b.z - a.w * b.w,
        a.y * b.x + a.x * b.y + a.z * b.w - a.w * b.z,
        a.z * b.x + a.x * b.z + a.w * b.y - a.y * b.w,
        a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y);
}

// Rotation around X axis
mat3 rotate_x(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(1, 0, 0),
        vec3(0, c, -s),
        vec3(0, s, c)
    );
}

// Rotation around Y axis
mat3 rotate_y(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, 0, s),
        vec3(0, 1, 0),
        vec3(-s, 0, c)
    );
}

// Rotation around Z axis
mat3 rotate_z(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, -s, 0),
        vec3(s, c, 0),
        vec3(0, 0, 1)
    );
}

// Distance function for Mandelbrot set
float get_mandelbrot_distance(vec3 pos)
{
    vec4 c = vec4(pos.x-0.4, pos.y, pos.z, 0);  // Take first three coordinates for quaternion
    vec4 z = c;  // Skip one iteration
    float dzmod = 1.0;
    float zmod = length(z);
    
    for (int i = 0; i < MAX_ITER; i++)
    {
        // Derivative value at this iteration
        dzmod = POWER * pow(zmod, POWER-1.0) * dzmod + 1.0;

        // Raise to natural power
        vec4 z0 = z;
        for (int j = 1; j < POWER; j++)
            z = qmul(z, z0);
        z += c;

        // Calculate modulus
        zmod = length(z);
        if (zmod > 2.0)
            break;
    }
    // Resulting distance
    float dist = 0.5 * zmod / dzmod * log(zmod);

    // Cut
    if (bool(CUT))
    dist = max(dist, pos.y);

    return dist;
}

// Calculates distance to all objects and returns minimum
float get_distance(vec3 position)
{
    float mandelbrot_distance = get_mandelbrot_distance(position);
    float dist = mandelbrot_distance;
    
    return dist;
}

// Ray marching function
float ray_march(vec3 ray_origin, vec3 ray_direction, out float ao)
{
    // Total traveled distance
    float all_distance = 0.0;
    // Current position
    vec3 current_position = ray_origin;

    // Loop
    int i;
    for (i = 0; i < MAX_STEPS; i++)
    {
        // Distance from current position
        float dist = get_distance(current_position);
        all_distance += dist;
        // Minimum distance error
        float min_dist = all_distance / (4.0*max(RES.x, RES.y));
        if (dist < min_dist)  // Ray hit object
        {
            ao = clamp(1.0 - float(i) / AO_COEF, 0.0, 1.0);
            return all_distance;
        }
        if (all_distance > MAX_RAY_LENGTH)  // Ray went too far
            break;
        // Shift current position
        current_position += dist * ray_direction;
    }
    // Ray went away, ambient occlusion not needed
    ao = 1.0;
    return MAX_RAY_LENGTH;

}

// Function that calculates normal at given point.
vec3 get_normal(vec3 point)
{
    // epsilon
    vec2 e = vec2(1.0,-1.0)*0.00001;
    return normalize( e.xyy*get_distance(point + e.xyy) +
					  e.yyx*get_distance(point + e.yyx) +
					  e.yxy*get_distance(point + e.yxy) +
					  e.xxx*get_distance(point + e.xxx) );
}

// Returns pixel color with lighting
float get_light(vec3 position)
{
    // Light source
    vec3 light_source = vec3(-2.0, 3.0, 0.0);
    // Light direction
    vec3 light_direction = normalize(light_source-position);
    // Normal
    vec3 normal = get_normal(position);
    // Diffusion
    float diffusion = clamp(dot(normal, light_direction), 0.0, 1.0);
    // If needed, consider shadow
    if (bool(SHADOWS))
    {
        // Temporary variable
        float t;
        float dist = ray_march(position + normal * 0.001, light_direction, t);
        // If there is something between object and source, create shadow (darken)
        if (dist < length(light_source - position))
            diffusion *= 0.3;
    }
    return diffusion;
}

vec3 render(vec2 frag_coord)
{
    // Final pixel color
    vec3 col;
    // Scale pixel coordinate
    vec2 uv = (frag_coord - 0.5*RES) / RES.y;
    // Rotation matrix
    mat3 RT = rotate_x(THETA)*rotate_y(PHI);
    // View direction
    vec3 ray_direction = normalize(vec3(uv, -1.0));
    ray_direction *= RT;
    // Location
    vec3 ray_origin = vec3(0, 0, ZOOM)*RT;

    // Ambient occlusion
    float ao;
    // Distance to object
    float dist = ray_march(ray_origin, ray_direction, ao);

    if (dist < MAX_RAY_LENGTH)  // Ray hit object
    {
        // Location of point where ray hit
        vec3 position = ray_origin + ray_direction * dist;
        // Pixel color with lighting
        dist = get_light(position);
        // Paint in selected color
        col = mix(vec3(dist), vec3(COLOR), 0.5);
        // Apply ambient occlusion
        col *= ao*ao;
    }
    else  // Ray didn't hit object
    {
        // Paint in sky color
        col = vec3(BG_COLOR);
    }
    return col;
}

void main()
{
    vec3 col = vec3(0);
    for (int i = 0; i < AA; i++)
    for (int j = 0; j < AA; j++)
        col += render(gl_FragCoord.xy + vec2(i, j) / float(AA));
    col /= float(AA*AA);

    // Assign calculated color to pixel
    gl_FragColor = vec4(col, 1.0);
}
