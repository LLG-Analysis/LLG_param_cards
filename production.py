import os
from tempfile import mkstemp
from shutil import move, copymode
import pandas as pd


# GRID
m_gluino = [ 500., 700., 900., 1100., 1300., 1500. ]
delta_m = [ 30., 40., 60., 80., 100. ]

feedback = []
param_card_in = "susyhit/slhaspectrum.in"
param_card_out = "susyhit/susyhit_slha.out"
for m_g in m_gluino:
    for delta in delta_m:
        # Modify input file
        fh, abs_path = mkstemp()
        with os.fdopen(fh,'w') as new_file:
            with open(param_card_in) as old_file:
                for line in old_file:
                    info = line.split(" ")
                    new_line = line
                    if len(info) > 9:
                        if info[3] == "1000021":
                            info[8] = '{:.6e}'.format(m_g)
                            new_line = ' '.join(info)
                            print(" ")
                            print(new_line[:-1])
                        if info[3] == "1000022":
                            info[8] = '{:.6e}'.format(m_g-delta)
                            new_line = ' '.join(info)
                            print(new_line[:-1])
                    new_file.write(new_line)
        #Copy the file permissions from the old file to the new file
        copymode(param_card_in, abs_path)
        #Remove original file
        os.remove(param_card_in)
        #Move new file
        move(abs_path, param_card_in)
        
        os.system("cd susyhit; ./run;")
        
        # Modify output file
        fh, abs_path = mkstemp()
        decay_session = False
        BR_gluon = 0
        BR_qq_sum = 0
        with os.fdopen(fh,'w') as new_file:
            with open(param_card_out) as old_file:
                control = 0
                for line in old_file:
                    info = line.split()
                    if not decay_session:
                        new_file.write(line)
                    if decay_session:
                        if control == 0 :
                            if line[0:15] == 'DECAY   1000021':
                                new_file.write(line)
                                control += 1
                                continue
                        if control == 1 :
                            control += 1
                            continue
                        if control == 2 :
                            BR_gluon = float(line.split('  2  ', 1)[0])
                            control += 1
                            continue
                        if control == 3 :
                            new_file.write(line)
                            control += 1
                            continue
                        if control >= 4 and control < 9 :
                            BR_qq = float(line.split('  3  ', 1)[0])/(1-BR_gluon)
                            BR_qq_sum += BR_qq
                            BR_qq_str = '{:.8e}'.format(BR_qq)
                            new_file.write('     ' + BR_qq_str + '    3  ' + line.split('  3  ', 1)[1])
                            control += 1
                            continue
                        if control == 9 :
                            new_file.write('#\n')
                            new_file.write('DECAY   1000022     0.00000000E+00   # neutralino1 decays')
                            control += 1
                            continue
                    if len(info) >= 3 and info[2] == "Width":
                        decay_session = True
        #Copy the file permissions from the old file to the new file
        copymode(param_card_out, abs_path)
        #Remove original file
        os.remove(param_card_out)
        #Move new file
        move(abs_path, param_card_out)
        
        os.system("mv susyhit/susyhit_slha.out grid/signal_"+str(int(m_g))+"_"+str(int(delta))+"_param_card.dat")
        
        feedback.append({
            "Signal": str(int(m_g))+"_"+str(int(delta)),
            "BR(~g -> ~chi_10 g)": BR_gluon,
            "BR_qq factor": (1-BR_gluon)*(1-BR_gluon),
            "Closure test": BR_qq_sum
        })
        
feedback = pd.DataFrame(feedback)
print(feedback)
        
    
            
 
