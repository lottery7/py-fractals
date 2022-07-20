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

// Поворот вокруг оси X
mat3 rotate_x(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(1, 0, 0),
        vec3(0, c, -s),
        vec3(0, s, c)
    );
}

// Поворот вокруг оси Y
mat3 rotate_y(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, 0, s),
        vec3(0, 1, 0),
        vec3(-s, 0, c)
    );
}

// Поворот вокруг оси Z
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

// Вычисляет расстояние до всех объектов и возвращает минимальное
float get_distance(vec3 position)
{
//    position = mod(position - 0.5*OFF, OFF) - 0.5*OFF;
    float dist = get_mandelbox_distance(position);
    return dist;
}

// Функция "пускания" луча
float ray_march(vec3 ray_origin, vec3 ray_direction, out float ao)
{
    // Всё пройденное расстояние
    float all_distance = 0.0;
    // Текущая позиция
    vec3 current_position = ray_origin;

    // Цикл
    int i;
    for (i = 0; i < MAX_STEPS; i++)
    {
        // Расстояние от текущей позиции
        float dist = get_distance(current_position);
        all_distance += dist;
        // Минимальная погрешность расстояния
        float min_dist = all_distance / (4.0*max(RES.x, RES.y));
        if (dist < min_dist)  // Луч попал в объект
        {
            ao = clamp(1.0 - float(i) / float(AO_COEF), 0.0, 1.0);
            return all_distance;
        }
        if (all_distance > MAX_RAY_LENGTH)  // Луч ушёл слишком далеко
            break;
        // Сдвигаем текущую позицию
        current_position += dist * ray_direction;
    }
    // Луч ушёл, ambient occlusion не нужен
    ao = 1.0;
    return MAX_RAY_LENGTH;

}

// Функция, которая вычисляет нормаль в заданной точке
vec3 get_normal(vec3 point)
{
    // epsilon
    vec2 e = vec2(1.0,-1.0)*0.00001;
    return normalize( e.xyy*get_distance(point + e.xyy) +
					  e.yyx*get_distance(point + e.yyx) +
					  e.yxy*get_distance(point + e.yxy) +
					  e.xxx*get_distance(point + e.xxx) );
}

// Возвращает цвет пикселя с учётом освещения
float get_light(vec3 position)
{
    // Источник света
    vec3 light_source = vec3(0, 50, 50);
    // Направление света
    vec3 light_direction = normalize(light_source-position);
    // Нормаль
    vec3 normal = get_normal(position);
    // Свет
    float light = clamp(dot(normal, light_direction), 0.0, 1.0);
    // Если надо, то учитываем тень
    if (bool(SHADOWS))
    {
        float t; // Временная переменная
        float dist = ray_march(position + normal * 0.001, light_direction, t);
        // Если между объектом и источником что-то есть, то затемняем
        if (dist < length(light_source - position))
            light *= 0.3;
    }
    return light;
}

vec3 render(vec2 frag_coord)
{
    // Конечный цвет пикселя
    vec3 col;
    // Масштабирование координаты пикселя
    vec2 uv = (frag_coord - 0.5*RES) / min(RES.y, RES.x);
    // Направление взгляда
    vec3 ray_direction = normalize(vec3(uv, -1.0));
    mat3 RT = rotate_x(THETA)*rotate_y(PHI);
    ray_direction *= RT;
    // Местоположение
    vec3 ray_origin = OFFSET;

    // Ambient occlusion
    float ao;
    // Расстояние до объекта
    float dist = ray_march(ray_origin, ray_direction, ao);

    if (dist < MAX_RAY_LENGTH)  // Луч попал в объект
    {
        // Местоположение точки, куда попал луч
        vec3 position = ray_origin + ray_direction * dist;
        // Цвет пикселя с учётом освещения
        dist = get_light(position);
        // Покраска в выбранный цвет
        col = mix(vec3(dist), vec3(COLOR), 0.5);
        // Применяем ambient occlusion
        col *= ao*ao*ao;
    }
    else  // Луч не попал в объект
    {
        // Красим в цвет неба
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

    // Присваиваем вычисленный цвет пикселю
    gl_FragColor = vec4(col, 1.0);
}











