import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider

# --- 1. 视觉风格升级：暗黑霓虹风 ---
plt.style.use('dark_background')

# --- 发动机参数 ---
r = 1.0    # 曲柄半径
l = 3.5    # 连杆长度
bore = 1.5 # 气缸孔径
z_head = 4.5 

# --- 绘图设置 ---
fig = plt.figure(figsize=(12, 9))
fig.patch.set_facecolor('#0a0a0a') # 深灰近黑背景
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0a0a0a')
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-2.5, 2.5)
ax.set_zlim(-2, 6)
ax.set_title('V8 Engine Cylinder - 3D Simulation', fontsize=18, color='#00ffff', pad=20)
ax.axis('off')

# --- 初始化绘图对象 (使用炫酷配色) ---

# 1. 气缸 (幽灵白，半透明)
theta = np.linspace(0, 2*np.pi, 60)
x_cyl = bore * np.cos(theta)
y_cyl = bore * np.sin(theta)
# 缸头和缸底
ax.plot(x_cyl, y_cyl, z_head, color='#333333', linewidth=1, alpha=0.5)
ax.plot(x_cyl, y_cyl, -1, color='#333333', linewidth=1, alpha=0.3)
# 缸壁纵向线条 (增加密度)
for i in range(0, 60, 6):
    ax.plot([x_cyl[i], x_cyl[i]], [y_cyl[i], y_cyl[i]], [-1, z_head], color='#444444', linewidth=0.5, alpha=0.3)

# 2. 运动部件
# 曲轴 (亮白)
crank_line, = ax.plot([], [], [], color='#ffffff', linewidth=6, solid_capstyle='round')
# 连杆 (霓虹蓝)
rod_line, = ax.plot([], [], [], color='#00ccff', linewidth=5, solid_capstyle='round')
# 活塞 (霓虹紫)
piston_head, = ax.plot([], [], [], color='#ff00ff', linewidth=2)
piston_body = [ax.plot([], [], [], color='#ff00ff', linewidth=1, alpha=0.4)[0] for _ in range(12)]

# 3. 气门 (进气: 荧光绿, 排气: 荧光红)
intake_valve_line, = ax.plot([], [], [], color='#00ff00', linewidth=4)
exhaust_valve_line, = ax.plot([], [], [], color='#ff3333', linewidth=4)
intake_pos = np.array([-0.8, 0, z_head])
exhaust_pos = np.array([0.8, 0, z_head])

# 4. 火花 (金黄色爆炸)
spark_point, = ax.plot([], [], [], marker='*', color='#ffff00', markersize=30, markeredgecolor='white', visible=False)

# 5. 气体粒子 (更密集的粒子流)
num_particles = 150
gas_particles, = ax.plot([], [], [], 'o', markersize=3, alpha=0.8)
np.random.seed(100)
p_x = (np.random.rand(num_particles) - 0.5) * 2 * (bore - 0.1)
p_y = (np.random.rand(num_particles) - 0.5) * 2 * (bore - 0.1)
p_z_ratios = np.random.rand(num_particles)

# 6. 状态文字 (HUD 风格)
status_text = ax.text2D(0.05, 0.92, "", transform=ax.transAxes, fontsize=20, fontweight='bold', color='white')
desc_text = ax.text2D(0.05, 0.85, "", transform=ax.transAxes, fontsize=12, color='#aaaaaa')

# --- 速度控制滑块 ---
ax_slider = plt.axes([0.25, 0.05, 0.5, 0.03], facecolor='#222222')
speed_slider = Slider(
    ax=ax_slider,
    label='RPM Control ',
    valmin=0,
    valmax=20,
    valinit=4,
    color='#00ccff',
    initcolor='none'
)
speed_slider.label.set_color('white')
speed_slider.valtext.set_color('white')

# 全局角度变量
current_angle = 0.0

# --- 计算逻辑 ---
def get_piston_z(angle_rad):
    xc = r * np.sin(angle_rad)
    zc = r * np.cos(angle_rad)
    zp = zc + np.sqrt(l**2 - xc**2)
    return xc, 0, zc, zp

def update(frame):
    global current_angle
    
    # 从滑块获取速度 (每帧增加的角度)
    speed = speed_slider.val
    current_angle = (current_angle + speed) % 720
    angle_rad = np.radians(current_angle)
    
    # 1. 运动计算
    xc, yc, zc, zp = get_piston_z(angle_rad)
    
    # 更新曲轴连杆
    crank_line.set_data([0, xc], [0, 0])
    crank_line.set_3d_properties([0, zc])
    rod_line.set_data([xc, 0], [0, 0])
    rod_line.set_3d_properties([zc, zp])
    
    # 更新活塞
    p_top = zp + 0.5
    p_bot = zp - 0.5
    piston_head.set_data(x_cyl, y_cyl)
    piston_head.set_3d_properties(p_top)
    for i, line in enumerate(piston_body):
        idx = i * (len(x_cyl)//len(piston_body))
        line.set_data([x_cyl[idx], x_cyl[idx]], [y_cyl[idx], y_cyl[idx]])
        line.set_3d_properties([p_bot, p_top])

    # 2. 冲程逻辑
    valve_open = 0.6
    iv_z, ev_z = z_head, z_head
    spark_on = False
    p_color = 'white'
    
    stroke = ""
    detail = ""
    
    if 0 <= current_angle < 180:
        stroke = "INTAKE (进气)"
        detail = "Intake Valve OPEN | Fuel Injection"
        iv_z -= valve_open
        p_color = '#00ffff' # 青色 (冷空气)
        status_text.set_color('#00ffff')
        
    elif 180 <= current_angle < 360:
        stroke = "COMPRESSION (压缩)"
        detail = "Valves CLOSED | Pressure Rising"
        p_color = '#ffaa00' # 橙色 (升温)
        status_text.set_color('#ffaa00')
        
    elif 360 <= current_angle < 540:
        stroke = "COMBUSTION (做功)"
        detail = "IGNITION! | Power Stroke"
        p_color = '#ff0000' # 红色 (爆炸)
        status_text.set_color('#ff3333')
        if 360 <= current_angle < 390: # 火花持续时间
            spark_on = True
            
    else:
        stroke = "EXHAUST (排气)"
        detail = "Exhaust Valve OPEN | Gas Out"
        ev_z -= valve_open
        p_color = '#888888' # 灰色 (废气)
        status_text.set_color('#aaaaaa')

    # 3. 更新部件状态
    intake_valve_line.set_data([intake_pos[0], intake_pos[0]], [intake_pos[1], intake_pos[1]])
    intake_valve_line.set_3d_properties([z_head, iv_z])
    
    exhaust_valve_line.set_data([exhaust_pos[0], exhaust_pos[0]], [exhaust_pos[1], exhaust_pos[1]])
    exhaust_valve_line.set_3d_properties([z_head, ev_z])
    
    spark_point.set_data([0], [0])
    spark_point.set_3d_properties([z_head - 0.2])
    spark_point.set_visible(spark_on)
    
    # 粒子特效
    cyl_h = z_head - p_top
    if cyl_h > 0:
        pz = p_top + p_z_ratios * cyl_h
        gas_particles.set_data(p_x, p_y)
        gas_particles.set_3d_properties(pz)
        gas_particles.set_color(p_color)
        gas_particles.set_visible(True)
    else:
        gas_particles.set_visible(False)

    status_text.set_text(stroke)
    desc_text.set_text(detail)
    
    return [crank_line, rod_line, piston_head, intake_valve_line, exhaust_valve_line, spark_point, gas_particles, status_text, desc_text] + piston_body

# 使用 cache_frame_data=False 避免警告，frames=None 表示无限循环
ani = animation.FuncAnimation(fig, update, frames=None, interval=20, blit=False, cache_frame_data=False)

plt.show()
