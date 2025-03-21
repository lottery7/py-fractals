#version 120

#define MAX_RAY_LENGTH 100.0
//#define OFF 100.0

uniform int MAX_ITER;
uniform vec2 RES;
uniform float PHI;
uniform float THETA;
uniform vec4 COLOR;
uniform vec4 BG_COLOR;
uniform int MAX_STEPS;
uniform float ROTATE_Y;
uniform float AO_COEF;
uniform int SHADOWS;
uniform vec3 OFFSET;
uniform float SCALE;
uniform float FOLDING;
uniform float OUT_RAD;
uniform float IN_RAD;
uniform int AA;

float OUT_RAD_SQR = OUT_RAD * OUT_RAD;
float IN_RAD_SQR = IN_RAD * IN_RAD;

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

float get_mandelbox_distance(vec3 pos)
{
    vec3 offset = pos;
    vec3 z = offset;
    float dz = 1.0;
    for (int i = 0; i < MAX_ITER; i++)
    {
        z = clamp(z, -FOLDING, FOLDING) * 2.0 - z;

        float zdot = dot(z,z);
        if (zdot < IN_RAD_SQR)
        {
            float temp = OUT_RAD_SQR / IN_RAD_SQR;
            z *= temp;
            dz *= temp;
        }
        else if (zdot < OUT_RAD_SQR)
        {
            float temp = OUT_RAD_SQR / zdot;
            z *= temp;
            dz *= temp;
        }

        z = SCALE * z + offset;
        dz = dz * abs(SCALE) + 1.0;
    }
    float r = length(z);
    return r / abs(dz);
}

// Calculates the distance to all objects and returns the minimum
float get_distance(vec3 position)
{
//  position = mod(position - 0.5*OFF, OFF) - 0.5*OFF;
    float dist = get_mandelbox_distance(position);
    return dist;
}

// Ray "launching" function
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
        if (dist < min_dist)  // Ray hit the object
        {
            ao = clamp(1.0 - float(i) / float(AO_COEF), 0.0, 1.0);
            return all_distance;
        }
        if (all_distance > MAX_RAY_LENGTH)  // Ray went too far
            break;
        // Shift the current position
        current_position += dist * ray_direction;
    }
    // Ray went away, ambient occlusion is not needed
    ao = 1.0;
    return MAX_RAY_LENGTH;

}

// Function that calculates the normal at a given point
vec3 get_normal(vec3 point)
{
    // epsilon
    vec2 e = vec2(1.0,-1.0)*0.00001;
    return normalize( e.xyy*get_distance(point + e.xyy) +
                     e.yyx*get_distance(point + e.yyx) +
                     e.yxy*get_distance(point + e.yxy) +
                     e.xxx*get_distance(point + e.xxx) );
}

// Returns the pixel color taking into account lighting
float get_light(vec3 position)
{
    // Light source
    vec3 light_source = vec3(0, 50, 50);
    // Light direction
    vec3 light_direction = normalize(light_source-position);
    // Normal
    vec3 normal = get_normal(position);
    // Light
    float light = clamp(dot(normal, light_direction), 0.0, 1.0);
    // If necessary, take into account the shadow
    if (bool(SHADOWS))
    {
        float t; // Temporary variable
        float dist = ray_march(position + normal * 0.001, light_direction, t);
        // If there is something between the object and the source, then darken
        if (dist < length(light_source - position))
            light *= 0.3;
    }
    return light;
}

vec3 render(vec2 frag_coord)
{
    // Final pixel color
    vec3 col;
    // Scaling the pixel coordinate
    vec2 uv = (frag_coord - 0.5*RES) / min(RES.y, RES.x);
    // View direction
    vec3 ray_direction = normalize(vec3(uv, -1.0));
    mat3 RT = rotate_x(THETA)*rotate_y(PHI);
    ray_direction *= RT;
    // Location
    vec3 ray_origin = OFFSET;

    // Ambient occlusion
    float ao;
    // Distance to the object
    float dist = ray_march(ray_origin, ray_direction, ao);

    if (dist < MAX_RAY_LENGTH)  // Ray hit the object
    {
        // Location of the point where the ray hit
        vec3 position = ray_origin + ray_direction * dist;
        // Pixel color taking into account lighting
        dist = get_light(position);
        // Painting in the selected color
        col = mix(vec3(dist), vec3(COLOR), 0.5);
        // Apply ambient occlusion
        col *= ao*ao*ao;
    }
    else  // Ray did not hit the object
    {
        // Paint in the sky color
        col = BG_COLOR.xyz;
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

    // Assign the calculated color to the pixel
    gl_FragColor = vec4(col, 1.0);
}
