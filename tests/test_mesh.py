from pc import Anisotropy
from pc import FDMesh
from pc import Sim
from pc import Nickel

def test_mesh1():
    mesh=FDMesh(nx=5,ny=3,nz=2,dx=0.23,dy=0.41)
    assert len(mesh.pos)==5*3*2
    assert mesh.nxy==15
    assert mesh.pos_at(0,0,0)==(0,0,0)
    assert mesh.pos_at(3,2,1)==(3*0.23,2*0.41,1)

def test_mesh2():
    mesh=FDMesh(nx=10,ny=10,nz=10)
    ni=Nickel()
    mesh.set_material(ni)
    t=ni.a/mesh.unit_length
    assert t>1
    assert mesh.pos_at(6,7,8)==(6*t,7*t,8*t)
    
    
if __name__=='__main__':
    test_mesh1()
    test_mesh2()