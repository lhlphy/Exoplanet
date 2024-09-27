# B´arðarbunga basalts, T=1787 K.txt
# MORB, T=861 K.txt
# Fasnia, T=1640 K.txt
# B-Nat, T=1648 K.txt
# B-glass, T=1654 K.txt

# CaFeSiO F3, T=1627 K.txt
# CaFeSiO F4, T=1673 K.txt
# CaFeSiO F5, T=1673 K.txt
# CaFeSiO F6, T=1673 K.txt
# CaFeSiO F7, T=1673 K.txt
# CaFeSiO F10, T=1673 K.txt
# CaFeSiO F11, T=1823 K.txt
# CaFeSiO F12, T=1823 K.txt

#命名中温度有问题


import numpy as np
from scipy.interpolate import interp1d  
import matplotlib.pyplot as plt  

def remove_duplicate(wave_combined, IS_combined):
    # 移除重复的波长值并取平均  
    unique_waves, indices = np.unique(wave_combined, return_index=True)  
    IS_combined_unique = [np.mean(IS_combined[wave_combined == wave]) for wave in unique_waves]  
    # convert IS_conbined_unique from list to numpy_array
    IS_combined_unique = np.array(IS_combined_unique)

    return unique_waves, IS_combined_unique


class lava_Albedo:
    def __init__(self, type = 'low'):
        self.type = type
        def Alow():
            # load data, can combined them to get low albedo curve
            CaFeSiOF4 = np.loadtxt(f"lava_lib/CaFeSiO F11, T=1823 K.txt", delimiter=',')
            Bglass = np.loadtxt(f"lava_lib/B-glass, T=1654 K.txt", delimiter=',')
            MORB = np.loadtxt(f'lava_lib/MORB, T=1653 K.txt', delimiter=',')

            # 数据提取，第一列是波长，第二列是波长对应的反射率 
            wave_list1 =  CaFeSiOF4[:,0]
            IS1 = CaFeSiOF4[:,1]

            wave_list2 = MORB[:,0] 
            IS2 = MORB[:,1] 

            # 合并数据  
            wave_combined = np.concatenate((wave_list1, wave_list2))  
            IS_combined = np.concatenate((IS1, IS2))

            wave_combined, IS_combined = remove_duplicate(wave_combined, IS_combined)
            return wave_combined, IS_combined
        
        def Ahigh():
            # load data, can combined them to get high albedo curve
            CaFeSiOF6 = np.loadtxt(f"lava_lib/CaFeSiO F6, T=1673 K.txt", delimiter=',')
            Teide = np.loadtxt(f"lava_lib/Teide, T=1187 K.txt", delimiter = ',')
            Forsterite = np.loadtxt('lava_lib/Forsterite, T=1473 K.txt', delimiter= ',')
            Hawaiian = np.loadtxt('lava_lib/Hawaiian basalt, T=1573 K.txt', delimiter= ',')
            
            wave_list1 =  CaFeSiOF6[:,0]
            IS1 = CaFeSiOF6[:,1]
            
            wave_list2 = Teide[:,0]
            IS2 = Teide[:,1]
            IS2 = IS2[wave_list2 < 2.71]
            wave_list2 = wave_list2[wave_list2 < 2.71]
            
            wave_list3 = Teide[:,0]
            IS3 = Teide[:,1]
            IS3 = IS3[(wave_list3 < 3.7) & (wave_list3 > 3.237)]
            wave_list3 = wave_list3[(wave_list3 < 3.7) & (wave_list3 > 3.237)]
            
            wave_list4 = Forsterite[:,0]
            IS4 = Forsterite[:,1]
            IS4 = IS4[(wave_list4 < 8.4) & (wave_list4 > 3.7)]
            wave_list4 = wave_list4[(wave_list4 < 8.4) & (wave_list4 > 3.7)]
            
            wave_list5 = Teide[:,0]
            IS5 = Teide[:,1]
            IS5 = IS5[ (wave_list5 < 10.4) & (wave_list5 > 8.4)]
            wave_list5 = wave_list5[(wave_list5 < 10.4) & (wave_list5 > 8.4)]
            
            wave_list6 = Hawaiian[:,0]
            IS6 = Hawaiian[:,1]
            IS6 = IS6[wave_list6 > 10.4]
            wave_list6 = wave_list6[wave_list6 > 10.4]
            
            wave_combined = np.concatenate((wave_list1, wave_list2, wave_list3, wave_list4, wave_list5, wave_list6))
            IS_combined = np.concatenate((IS1, IS2, IS3, IS4, IS5, IS6))
            data_combined = np.array([wave_combined,IS_combined])
            data_combined = data_combined[:, data_combined[0,:].argsort()]
            
            wave_combined = data_combined[0,:]
            IS_combined = data_combined[1,:]

            wave_combined, IS_combined = remove_duplicate(wave_combined, IS_combined)
            return wave_combined, IS_combined
            
        if type =='low':
            # 读取数据并拼接
            wave_combined, IS_combined = Alow()
            # 创建插值函数  
            self.interp_func = interp1d(wave_combined, IS_combined, kind='slinear')  
            
        elif type == 'high':
            wave_combined, IS_combined = Ahigh()
            # 创建插值函数
            self.interp_func = interp1d(wave_combined, IS_combined, kind='slinear')
            
        elif type == 'mode1': # have the same low-albedo at <1.5 micron, and same albedo at 5-12 micron, but clearly diverge between 1.5-5 micron.
            wave_combined_l, IS_combined_l = Alow()
            wave_combined_h, IS_combined_h = Ahigh()
            
            # concatenate low and high albedo curve
            IS_combined = np.concatenate((IS_combined_l[wave_combined_l < 1.5], 
                        IS_combined_h[(wave_combined_h > 1.5) & (wave_combined_h < 5)], IS_combined_l[wave_combined_l > 5]))
            wave_combined = np.concatenate((wave_combined_l[wave_combined_l < 1.5], 
                        wave_combined_h[(wave_combined_h > 1.5) & (wave_combined_h < 5)], wave_combined_l[wave_combined_l > 5]))
            
            # 创建插值函数
            self.interp_func = interp1d(wave_combined, IS_combined, kind='slinear')
            
        self.Wmax = np.max(wave_combined)
        self.Wmin = np.min(wave_combined)
        # print(self.Wmin, self.Wmax)
            
            
    # 计算插值光谱数据  
    def A_interp(self, lam):
        return self.interp_func(lam)
    
    def albedo_plotter(self):
        wave_list = np.linspace(self.Wmin, self.Wmax, 1000)
        Aspectrum = self.A_interp(wave_list)
        plt.plot(wave_list, Aspectrum, color = 'b', label = self.type)
        plt.show()
        plt.xlabel('Wavelength ($\mu$m)')
        plt.ylabel('Albedo')
        plt.legend()
        plt.savefig(f'lava_lib/{self.type}.png')
        plt.close()
        
# 实例化类，作为对象导入其他程序模块
LA = lava_Albedo('low')

# run as main program to plot albedo curve
if __name__ == '__main__':
    print('lava_data.py processing...')
    LAl = lava_Albedo('low')
    wave = np.linspace(LAl.Wmin,LAl.Wmax,1000)
    Spectrum = LAl.A_interp(wave)
    S1 = np.array([wave,Spectrum])
    np.savetxt('lava_lib/S_l.txt', S1, fmt='%f') 
    plt.plot(wave, Spectrum, color = 'b')
    # plt.savefig('lava_lib/high_albedo.png')

    LAh = lava_Albedo('high')
    wave = np.linspace(LAh.Wmin,LAh.Wmax,1000)
    Spectrum = LAh.A_interp(wave)
    S2 = np.array([wave,Spectrum])
    np.savetxt('lava_lib/S_h.txt', S2, fmt='%f')
    plt.plot(wave, Spectrum, color = 'r')
    
    LAm1 = lava_Albedo('mode1')
    wave = np.linspace(LAm1.Wmin,LAm1.Wmax,1000)
    Spectrum = LAm1.A_interp(wave)
    S2 = np.array([wave,Spectrum])
    np.savetxt('lava_lib/S_m1.txt', S2, fmt='%f')
    plt.plot(wave, Spectrum, color = 'g')

    plt.xlabel('Wavelength ($\mu$m)')
    plt.ylabel('Albedo')
    plt.legend(['Low albedo', 'high albedo', 'band high albedo'])
    plt.savefig('lava_lib/albedo_comp.png')
    plt.close()
    
    LAl.albedo_plotter()
    LAh.albedo_plotter()
    LAm1.albedo_plotter()
