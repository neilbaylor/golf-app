import math, json
TEE=(200,1400); GC=(825,325)   # green centre (map px)
S=0.24
ang=math.atan2(GC[0]-TEE[0], TEE[1]-GC[1])     # angle of tee->green from map-up, clockwise
def T(p):
    x=(p[0]-TEE[0])*S; y=(TEE[1]-p[1])*S          # x right, y up (yards)
    c,s=math.cos(ang),math.sin(ang)
    return (round(x*c - y*s,1), round(x*s + y*c,1))   # rotate so green is straight up
if __name__=='__main__':
    print('angle deg', math.degrees(ang))
    for n,p in [('tee',TEE),('green',GC),('fw_start',(330,1020)),('fw_mid',(400,800)),('fw_bend',(470,660)),('A',(410,590)),('B',(485,578)),('E2',(532,542)),('bigD',(445,830)),('bunker',(718,315)),('prac_green',(370,360)),('prac_bunker',(318,295)),('path1',(150,540)),('path2',(250,290)),('path3',(380,160)),('bluff1',(640,700)),('bluff2',(900,420)),('green_back',(890,290)),('green_front',(755,368))]:
        print(n, T(p))
