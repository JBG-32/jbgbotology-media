import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
from matplotlib import font_manager
plt.rcParams['mathtext.fontset']='cm'
CH='#EDE6D6'; GO='#F5B942'; CY='#3FE0FF'; EM='#FF4A2E'; VI='#9B84FF'
# Equation: old (removed) and new (established)
def eq(tex,fn,color,size=44):
    fig=plt.figure(figsize=(10,1.6),dpi=108); fig.patch.set_alpha(0)
    fig.text(0.5,0.5,tex,fontsize=size,color=color,ha='center',va='center')
    fig.savefig(fn,transparent=True); plt.close(fig)
eq(r'$\mathcal{R}^{(4)}_{\mu\nu}=\int_{\Sigma^{(8)}}\Omega_{abcd}\,\Psi^{ab}\wedge\bar{\Psi}^{cd}\,d\Sigma$','eq_old.png',CH,40)
eq(r'$G_4=\dfrac{G_{12}}{\mathrm{Vol}(\Sigma_8)}$','eq_new.png',CH,52)
# Sky map: real cubic harmonic K4 = x^4+y^4+z^4-3/5 (illustrative orientation)
lon=np.linspace(-np.pi,np.pi,720); lat=np.linspace(-np.pi/2,np.pi/2,360)
L,B=np.meshgrid(lon,lat); x=np.cos(B)*np.cos(L); y=np.cos(B)*np.sin(L); z=np.sin(B)
# rotate frame (not aligned to galactic plane)
a=np.radians(35); b=np.radians(20)
x1=x*np.cos(a)-y*np.sin(a); y1=x*np.sin(a)+y*np.cos(a); z1=z
y2=y1*np.cos(b)-z1*np.sin(b); z2=y1*np.sin(b)+z1*np.cos(b)
K=x1**4+y2**4+z2**4-0.6
fig=plt.figure(figsize=(10,5.6),dpi=108); fig.patch.set_alpha(0)
ax=fig.add_subplot(111,projection='mollweide'); ax.set_facecolor((0,0,0,0))
from matplotlib.colors import LinearSegmentedColormap
cm=LinearSegmentedColormap.from_list('c',['#0B1426','#2a3ea8',VI,CY,'#ffffff'])
ax.pcolormesh(L,B,K,cmap=cm,shading='auto',alpha=0.85)
ax.grid(True,color=(1,1,1,0.25),lw=0.6); ax.set_xticklabels([]); ax.set_yticklabels([])
for s in ax.spines.values(): s.set_edgecolor((1,1,1,0.5))
fig.savefig('skymap.png',transparent=True,bbox_inches='tight',pad_inches=0.05); plt.close(fig)
print('ok')
