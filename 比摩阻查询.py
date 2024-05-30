""""
 Created on 2024-05-26
    比摩阻、动压查询程序
 create by: 阳世浩-3210104897  孔嘉麒-3210105320
"""

import pandas as pd
import os

work_path = r'E:\Users\DELL\Desktop\暖通空调\大作业\设计'
os.chdir(work_path)

# 查询文件
friction_loss_df = pd.read_csv('比摩阻查询.csv', index_col=0)
friction_loss_df.columns = friction_loss_df.columns.astype(float)
friction_loss_df.index = friction_loss_df.index.astype(float)

dynamic_pressure_df = pd.read_csv('动压查询.csv')
dynamic_pressure_df['风速'] = dynamic_pressure_df['风速'].astype(float)

# 读取数据
data_df = pd.read_csv('数据表.csv')

# 线性插值函数
def linear_interpolate(x, x0, x1, y0, y1):
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

# 查询比摩阻
def get_friction_loss(diameter, velocity):
    if diameter in friction_loss_df.columns and velocity in friction_loss_df.index:
        return friction_loss_df.loc[velocity, diameter]
    else:
        # 线性插值
        available_diameters = friction_loss_df.columns
        available_velocities = friction_loss_df.index

        if diameter not in available_diameters:
            lower_diameter = available_diameters[available_diameters < diameter].max()
            upper_diameter = available_diameters[available_diameters > diameter].min()
        else:
            lower_diameter = upper_diameter = diameter

        if velocity not in available_velocities:
            lower_velocity = available_velocities[available_velocities < velocity].max()
            upper_velocity = available_velocities[available_velocities > velocity].min()
        else:
            lower_velocity = upper_velocity = velocity

        if lower_velocity == upper_velocity:
            r1 = friction_loss_df.loc[lower_velocity, lower_diameter]
            r2 = friction_loss_df.loc[lower_velocity, upper_diameter]
        else:
            q11 = friction_loss_df.loc[lower_velocity, lower_diameter]
            q21 = friction_loss_df.loc[upper_velocity, lower_diameter]
            q12 = friction_loss_df.loc[lower_velocity, upper_diameter]
            q22 = friction_loss_df.loc[upper_velocity, upper_diameter]

            r1 = linear_interpolate(velocity, lower_velocity, upper_velocity, q11, q21)
            r2 = linear_interpolate(velocity, lower_velocity, upper_velocity, q12, q22)

        return linear_interpolate(diameter, lower_diameter, upper_diameter, r1, r2)

# 查询动压
def get_dynamic_pressure(velocity):
    if velocity in dynamic_pressure_df['风速'].values:
        return dynamic_pressure_df[dynamic_pressure_df['风速'] == velocity]['动压'].values[0]
    else:
        # 线性插值
        available_velocities = dynamic_pressure_df['风速'].values
        lower_velocity = available_velocities[available_velocities < velocity].max()
        upper_velocity = available_velocities[available_velocities > velocity].min()
        
        p1 = dynamic_pressure_df[dynamic_pressure_df['风速'] == lower_velocity]['动压'].values[0]
        p2 = dynamic_pressure_df[dynamic_pressure_df['风速'] == upper_velocity]['动压'].values[0]
        
        return linear_interpolate(velocity, lower_velocity, upper_velocity, p1, p2)

# 查询并写入
for idx, row in data_df.iterrows():
    velocity = row['风速']
    diameter = row['管道直径']
    
    data_df.at[idx, '动压'] = get_dynamic_pressure(velocity)
    data_df.at[idx, '平均比摩阻'] = get_friction_loss(diameter, velocity)

# 写入
data_df.to_csv('数据表.csv', index=False)
