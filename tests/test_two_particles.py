# FIDIMAG:
from fidimag.micro import Sim, FDMesh
from fidimag.micro import UniformExchange, UniaxialAnisotropy, Demag
from fidimag.common.neb_cartesian import NEB_Sundials
import numpy as np

# For timing purposes --------------------------------
import time

class Timer:

    def __init__(self):
        self.t1 = 0
        self.t2 = 0

    def start(self):
        self.t1 = time.clock()

    def end(self):
        self.t2 = time.clock()

    def interval(self):
        return self.t2 - self.t1

# ----------------------------------------------------

# CrCo Material Parameters
# Parameters
A = 1e-12
Kx = 1e5
# Strong anisotropy
Ms = 3.8e5


"""
We will define two particles using a 4 sites mesh, letting the
sites in the middle as Ms = 0

"""


def two_part(pos):

    x, y = pos[0], pos[1]

    if x > 7 or x < 3:
        return Ms
    else:
        return 0

# Finite differences mesh
mesh = FDMesh(nx=10,
              ny=3,
              nz=3,
              dx=1, dy=1, dz=1,
              unit_length=1e-9
              )


# Simulation Function
def relax_neb(k, maxst, simname, init_im, interp, save_every=10000):
    """
    Execute a simulation with the NEB function of the FIDIMAG code, for an
    elongated particle (long cylinder)

    The simulations are made for a specific spring constant 'k' (a float),
    number of images 'init_im', interpolations between images 'interp'
    (an array) and a maximum of 'maxst' steps.
    'simname' is the name of the simulation, to distinguish the
    output files.

    --> vtks and npys are saved in files starting with the 'simname' string

    """

    # Prepare simulation
    # We define the cylinder with the Magnetisation function
    sim = Sim(mesh)
    sim.Ms = two_part

    sim.add(UniformExchange(A=A))

    # Uniaxial anisotropy along x-axis
    sim.add(UniaxialAnisotropy(Kx, axis=(1, 0, 0)))

    # Define many initial states close to one extreme. We want to check
    # if the images in the last step, are placed mostly in equally positions
    init_images = init_im

    # Number of images between each state specified before (here we need only
    # two, one for the states between the initial and intermediate state
    # and another one for the images between the intermediate and final
    # states). Thus, the number of interpolations must always be
    # equal to 'the number of initial states specified', minus one.
    interpolations = interp

    neb = NEB_Sundials(sim,
                       init_images,
                       interpolations=interpolations,
                       spring=k,
                       name=simname)

    neb.relax(max_steps=maxst,
              save_vtk_steps=save_every,
              save_npy_steps=save_every,
              stopping_dmdt=1e-2)


def test_energy_barrier_2particles():
    # Initial images: we set here a rotation interpolating
    def mid_m(pos):
        if pos[0] > 1:
            return (0, 0.1, 0.9)
        else:
            return (-0.1, 0, 0.8)

    init_im = [(-1, 0, 0), mid_m, (1, 0, 0)]
    interp = [10, 10]

    # Define different ks for multiple simulations
    krange = ['1e10']

    for k in krange:
        # print 'Computing for k = {}'.format(k)
        relax_neb(float(k), 2000,
                  'neb_2particles_k{}_10-10int'.format(k),
                  init_im,
                  interp,
                  save_every=5000)

    # Get the energies from the last state
    data = np.loadtxt('neb_2particles_k1e10_10-10int_energy.ndt')[-1][1:]

    ebarrier = np.abs(np.max(data) - np.min(data)) / (1.602e-19)

    assert ebarrier < 0.017
    assert ebarrier > 0.005
