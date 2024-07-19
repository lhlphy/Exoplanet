import numpy as np
from parameter_list import *
import main_function as mf
from function_library import B, sym_complete
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import os
import time

def Full_spectrum(wavelength_bound, args = None, Temperature = Temperature, Albedo = Albedo, id = 0, Ntheta = 5, Nwave = 1):

    if args != None:
        id = args.id
        Albedo = args.Albedo
        Ntheta = args.Ntheta
        Nwave = args.Nwave
    
    # Create the folder to store the results
    os.makedirs(f'temp/R{id}/variables', exist_ok=True)
    os.makedirs(f'temp/R{id}/Results', exist_ok=True)

    t0 = time.time()
    """ Calculate the thermal spectrum """ 
    mf.thermal_spectrum(wavelength_bound, Temperature, Albedo= Albedo, id= id, Ntheta = Ntheta, NWavelength= Nwave)
    # Load the results
    thermal_ratio = np.load(f'temp/R{id}/Results/Ratio.npy')
    Theta_list  = np.load(f'temp/R{id}/Results/Theta.npy')
    Star_flux  = np.load(f'temp/R{id}/Results/Star_flux.npy')

    """ Calculate the reflected and diffused light   """
    if Ntheta == 1:  # Create Theta_list
        Theta_list2 = np.array([np.pi])
    else:
        Theta_list2 = np.linspace(0, np.pi, Ntheta)  # 0-pi 与 pi-2pi 重复
    Wave_list = np.linspace(wavelength_bound[0], wavelength_bound[1], Nwave)

    # 与 thermal_ratio 一致
    I_intensity = np.zeros([Nwave, Ntheta])
    I_diffuse = I_intensity.copy()
    I_specular = I_intensity.copy()

    # Create vector to store the geometry results, and using the gemotry result to generate the intensity I_xxxxxx
    G_intensity = np.zeros(Ntheta)
    G_diffuse = G_intensity.copy()
    G_specular = G_intensity.copy()

    for i, Theta in enumerate(Theta_list2):
        I, D, S = mf.global_intensity(Theta, 1, 1, 0, id, Model= 'Lambert', mode = 'geo')
        G_intensity[i] = I.sum()
        G_diffuse[i] = D.sum()
        G_specular[i] = S.sum()

    for j, wave in enumerate(Wave_list):
        coef = Albedo  *  B(wave, Temperature) 
        I_intensity[j,:] = coef * G_intensity[:]
        I_diffuse[j,:] = coef * G_diffuse[:]
        I_specular[j,:] = coef * G_specular[:]

    # symmetry
    I_intensity = sym_complete(I_intensity,1) / Star_flux
    I_diffuse = sym_complete(I_diffuse,1) / Star_flux
    I_specular = sym_complete(I_specular,1) / Star_flux
    Theta_list2 = sym_complete(Theta_list2)
    Theta_list2[Ntheta: 2*Ntheta] = 2*np.pi - Theta_list2[Ntheta: 2*Ntheta]

    if (Theta_list != Theta_list2).any():  # Check the consistency of the Theta_list [size: Ntheta*2]
        raise ValueError("Theta_list is not consistent!")
    
    # Save the results
    np.save(f'temp/R{id}/variables/I_intensity.npy', I_intensity)
    np.save(f'temp/R{id}/variables/I_diffuse.npy', I_diffuse)
    np.save(f'temp/R{id}/variables/I_specular.npy', I_specular)
    #np.save(f'temp/R{id}/variables/Theta_list.npy', Theta_list2)


    """Combine the thermal and optical results, generate the full spectrum"""

    FS = I_intensity + thermal_ratio   # Full Spectrum  [size: Nwave * (2*Ntheta)]  xaixs: Wave_list, yaixs: Theta_list

    FS_plotter(FS, Wave_list, Theta_list, Nwave, Ntheta, id)

    t1 = time.time()
    print("Total Time = ", t1 - t0, "s, Processing ALL DONE!")


def FS_plotter(FS, Wave_list, Theta_list, Nwave, Ntheta, id = 0 , Obs_wavelength = [5e-7]):
    """Plot the full spectrum
    FS: Full Spectrum (matrix: Nwave* (2*Ntheta))
    Obs_wavelength: wavelength be observed (array)
    """
    ## plot Full spectrum
    fig, ax = plt.subplots()
    #Xwave = np.linspace(Wave_list[0], Wave_list[-1], 1000)
    ## plot Contrast ratio
    for i in range(Ntheta):
        #spl = interp1d(Wave_list, FS[:,i], kind='cubic')
        ax.plot(Wave_list* 1e6, FS[:,i] *1e6, label = f'Theta = {Theta_list[i]}')
    ax.set_xlabel('Wavelength ($\mu$m)')
    ax.set_ylabel('Contrast ratio (ppm)')
    ax.set_title(f'Full Spectrum')
    ax.legend()
    plt.show()
    plt.savefig(f'temp/R{id}/Results/Constrat_ratio.png')
    plt.close()

    # plot Full Spectrum
    fig, ax = plt.subplots()
    Star_flux  = np.load(f'temp/R{id}/Results/Star_flux.npy')
    for i in range(Ntheta):
        #spl = interp1d(Wave_list, FS[:,i], kind='cubic')
        ax.plot(Wave_list* 1e6, FS[:,i]* Star_flux[:,i] , label = f'Theta = {Theta_list[i]}')
    ax.set_xlabel('Wavelength ($\mu$m)')
    ax.set_ylabel('$\mathrm{Spectrum\; of\; Planet \; (W \cdot sr^{-1}\cdot nm^{-1})}$')
    ax.set_title(f'Full Spectrum')
    ax.legend()
    plt.show()
    plt.savefig(f'temp/R{id}/Results/Full_spectrum.png')
    plt.close()

    ## plot phase curve
    if Obs_wavelength != np.ndarray:
        Obs_wavelength = np.array([Obs_wavelength])

    spl = interp1d(Wave_list, FS.T, kind = 'cubic')
    y = spl(Obs_wavelength)
    y = y.T[0]

    fig , ax = plt.subplots()
    for i, Owave in enumerate(Obs_wavelength):
        ax.plot(Theta_list, y[i,:] *1e6, label = f'Wavelength = {Owave* 1e6} $\mu$m')
    ax.set_xlabel('Orbital phase')
    ax.set_ylabel('Contrast ratio (ppm)')
    ax.set_title(f'Phase curve')
    ax.legend()
    plt.show()
    plt.savefig(f'temp/R{id}/Results/Phase_curve.png')
    plt.close()




    





