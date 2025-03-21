#version 120

#define MAX_RAY_LENGTH 100.0

uniform int MAX_ITER;
uniform vec2 RES;
uniform float POWER;
uniform float ZOOM;
uniform float PHI;
uniform float THETA;
uniform int CUT;
uniform vec3 C;
uniform vec4 COLOR;
uniform vec4 BG_COLOR;
uniform int MAX_STEPS;
uniform float ROTATE_Y;
uniform float AO_COEF;
uniform int SHADOWS;
uniform int AA;


// Rotation around the X axis
mat3 rotate_x(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(1, 0, 0),
        vec3(0, c, -s),
        vec3(0, s, c)
    );
}

// Rotation around the Y axis
mat3 rotate_y(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, 0, s),
        vec3(0, 1, 0),
        vec3(-s, 0, c)
    );
}

// Rotation around the Z axis
mat3 rotate_z(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, -s, 0),
        vec3(s, c, 0),
        vec3(0, 0, 1)
    );
}

float get_julia_distance(vec3 pos)
{
    vec3 z = pos.xzy;
    vec3 c = C;
    float dzmod = 1.0;
    float zmod = length(z);


    for (int i = 0; i < MAX_ITER; i++)
    {
        // Derivative value at this iteration
        dzmod = POWER * pow(zmod, POWER-1.0) * dzmod + 1.0;

        // Exponentiation
        float r = zmod; // modulus
        float a = POWER*atan(z.y, z.x) + ROTATE_Y;
        float b = POWER*asin(z.z / r);
        z = c + pow(r, POWER) * vec3(cos(a)*cos(b), sin(a)*cos(b), sin(b));

        // Calculate the modulus (will have to calculate anyway)
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

// Calculates the distance to all objects and returns the minimum
float get_distance(vec3 position)
{
    float julia_distance = get_julia_distance(position);
    float dist = julia_distance;

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
        // Distance from the current position
        float dist = get_distance(current_position);
        all_distance += dist;
        // Minimum distance error
        float min_dist = all_distance / (4.0*max(RES.x, RES.y));
        if (dist < min_dist) // Ray hit an object
        {
            ao = clamp(1.0 - float(i) / AO_COEF, 0.0, 1.0);
            return all_distance;
        }
        if (all_distance > MAX_RAY_LENGTH) // Ray went too far
            break;
        // Shift the current position
        current_position += dist * ray_direction;
    }
    // Ray went out, ambient occlusion is not needed
    ao = 1.0;
    return MAX_RAY_LENGTH;

}

// Function that calculates the normal at a given point.
vec3 get_normal(vec3 point)
{
    // epsilon
    vec2 e = vec2(1.0,-1.0)*0.00001;
    return normalize( e.xyy*get_distance(point + e.xyy) +
                    e.yyx*get_distance(point + e.yyx) +
                    e.yxy*get_distance(point + e.yxy) +
                    e.xxx*get_distance(point + e.xxx) );
}

// Returns the pixel color with lighting taken into account
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
    // If needed, take shadows into account
    if (bool(SHADOWS))
    {
        // Temporary variable
        float t;
        float dist = ray_march(position + normal * 0.001, light_direction, t);
        // If there is something between the object and the source, create a shadow (darken)
        if (dist < length(light_source - position))
            diffusion *= 0.3;
    }
    return diffusion;
}

vec3 render(vec2 frag_coord)
{
    // Final pixel color
    vec3 col;
    // Scaling the pixel coordinate
    vec2 uv = (frag_coord - 0.5*RES) / RES.y;
    /// Rotation matrix
    mat3 RT = rotate_x(THETA)*rotate_y(PHI);
    // View direction
    vec3 ray_direction = normalize(vec3(uv, -1.0));
    ray_direction *= RT;
    // Location
    vec3 ray_origin = vec3(0, 0, ZOOM)*RT;

    // Ambient occlusion
    float ao;
    // Distance to the object
    float dist = ray_march(ray_origin, ray_direction, ao);

    if (dist < MAX_RAY_LENGTH) // Ray hit an object
    {
        // Location of the point where the ray hit
        vec3 position = ray_origin + ray_direction * dist;
        // Pixel color with lighting taken into account
        dist = get_light(position);
        // Paint in the selected color
        col = mix(vec3(dist), vec3(COLOR), 0.5);
        // Apply ambient occlusion
        col *= ao*ao;
    }
    else // Ray did not hit an object
    {
        // Paint in the sky color
        col = vec3(BG_COLOR);
    }
    return col;
}
void main()
{

    vec3 col = vec3(0);
    for (int j = 0; j < AA; j++)
    for (int i = 0; i < AA; i++)
        col += render(gl_FragCoord.xy + vec2(i,j) / float(AA));
    col /= float(AA*AA);

    // Assign the calculated pixel color
    gl_FragColor = vec4(col, 1.0);
}