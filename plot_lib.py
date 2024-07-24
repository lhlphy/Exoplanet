import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

def IDS_plot(name, Obs_wave):
    # load data
    I_specular = np.load(f'temp/{name}/variables/I_specular.npy')
    I_intensity = np.load(f'temp/{name}/variables/I_intensity.npy')
    I_diffuse = np.load(f'temp/{name}/variables/I_diffuse.npy')
    Theta_list = np.load(f'temp/{name}/variables/Theta.npy')
    Wave_list = np.load(f'temp/{name}/variables/wave_list.npy')
    Thermal = np.load(f'temp/{name}/variables/Thermal.npy')

    if type(Obs_wave) == float:
        Obs_wave = np.array([Obs_wave])

    # interpolate
    # print(Wave_list.shape, I_specular.T.shape)
    spls = interp1d(Wave_list, I_specular.T, kind='cubic', fill_value='extrapolate')
    spli = interp1d(Wave_list, I_intensity.T, kind='cubic', fill_value='extrapolate')
    spld = interp1d(Wave_list, I_diffuse.T, kind='cubic', fill_value='extrapolate')
    splt = interp1d(Wave_list, Thermal.T, kind='cubic', fill_value='extrapolate')
    I_s = spls(Obs_wave).T
    I_i = spli(Obs_wave).T
    I_d = spld(Obs_wave).T
    I_t = splt(Obs_wave).T

    theta = np.linspace(0, 2*np.pi, 200)
    Theta_list[np.size(Theta_list)//2] += 1e-10
    spls = interp1d(Theta_list, I_s, kind='cubic', fill_value='extrapolate')
    spli = interp1d(Theta_list, I_i, kind='cubic', fill_value='extrapolate')
    spld = interp1d(Theta_list, I_d, kind='cubic', fill_value='extrapolate')
    splt = interp1d(Theta_list, I_t, kind='cubic', fill_value='extrapolate')
    I_s = spls(theta)
    I_i = spli(theta)
    I_d = spld(theta)
    I_t = splt(theta)

    # plot
    plt.rcParams['font.size'] = 12
    i = 0
    # plt.figure(figsize=(8, 5))

    # plt.plot(theta, I_s[0,:] * 1e6, label='Specular')
    # plt.plot(theta, I_d[0,:] * 1e6, label='Diffuse')
    # plt.plot(theta, I_t[0,:] * 1e6, label='Thermal')

    # plt.xlabel('Orbital angle (rad)')
    # plt.ylabel('Contrast ratio (ppm)')
    # plt.legend()
    # plt.show()
    # os.makedirs(f'temp/P0', exist_ok= True)
    # plt.savefig(f'temp/P0/compare.png')
    # plt.close()

    fig, ax = plt.subplots(figsize=(9,6))
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=0.3)
    plt.rcParams['ytick.direction'] = 'in'# 刻度线显示在内部
    plt.rcParams['xtick.direction'] = 'in'# 刻度线显示在内部

    axpos = [0.1, 0.15, 0.7, 0.7]
    bwith = 2
    ax.spines['bottom'].set_linewidth(bwith)
    ax.spines['left'].set_linewidth(bwith)
    ax.spines['top'].set_linewidth(bwith)
    ax.spines['right'].set_linewidth(bwith)
    ax.set_position(axpos)
    #ax.axhline(y=np.average(Tc[3:]), color='gray', ls='-', )
    ax.plot(theta, I_s[i,:] * 1e6, label='Specular', color='k')
    ax.set_ylim(ymin=0, ymax= np.max(I_s[i,:])*1.1e6)
    ax.set_xlabel('Orbital angle (rad)', fontsize=18)
    ax.set_ylabel('Contrast ratio (ppm)', fontsize=18)
    ax.tick_params(length=6, width=2)
    ax.spines['right'].set_visible(False)

    lambda_color = 'blue'
    labmda_ax = ax.twinx()
    labmda_ax.set_position(axpos)
    labmda_ax.plot(theta, I_d[i,:] * 1e6, label='Diffuse', color=lambda_color)
    labmda_ax.set_ylim(ymin=0, ymax= np.max(I_d[i,:])*1.1e6)
    labmda_ax.set_xlabel('Orbital angle (rad)', fontsize=18)
    labmda_ax.tick_params(length=6, width=2, color=lambda_color, labelcolor=lambda_color)
    labmda_ax.set_ylabel('Contrast ratio (ppm)', fontsize=18, color=lambda_color)
    labmda_ax.spines['right'].set(color=lambda_color, linewidth=2.0, linestyle=':')

    omglog_color = 'red'
    omglog_ax = ax.twinx()
    # 使用科学计数法的刻度
    omglog_ax.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    # 获取 y 轴 OffsetText 对象
    offset_text = omglog_ax.yaxis.get_offset_text()
    # 调整位置示例，偏移 (dx, dy) 单位是像素 (points)
    offset_text.set_position((1.12, 0))
    # 调整字体大小
    offset_text.set_size(18)  # 或者使用 offset_text.set_fontsize(12)
    omglog_ax.spines['right'].set_position(('data', np.max(theta)*1.15))
    omglog_ax.set_ylim(0, np.max(I_t[i,:])*1.1e6)
    omglog_ax.set_position(axpos)
    omglog_ax.plot(theta, I_t[i,:] * 1e6, label='Thermal', color=omglog_color)
    omglog_ax.set_ylabel('Contrast ratio (ppm)', fontsize=18, color=omglog_color)
    omglog_ax.tick_params(length=6, width=2, color=omglog_color, labelcolor=omglog_color)
    omglog_ax.spines['right'].set(color=omglog_color, linewidth=2.0, linestyle='-.')
    fig.legend(['Specular', 'Diffuse', 'Thermal'])
    plt.show()
    os.makedirs(f'temp/P0', exist_ok= True)
    plt.savefig(f'temp/P0/compare.png')
    plt.close()



if __name__ =='__main__':
    IDS_plot('R3 0.001 AU', np.array([5]) * 1e-6)