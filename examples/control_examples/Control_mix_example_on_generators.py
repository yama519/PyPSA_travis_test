"""
This example shows the effect of application of each controller and mix of them
on Generator component. The effect of each controller and mix of them are
compared in a graph against no control case.
"""
# importing important modules
from __future__ import print_function, division
import pandas as pd
import pypsa
import matplotlib.pyplot as plt

power_inj = [0, 0.03, 0.05, 0.07]

# defining network
n = pypsa.Network()

n_buses = 4
for i in range(n_buses):
    n.add("Bus", "My bus {}".format(i), v_nom=.4, v_mag_pu_set=1.02)

    n.add("Generator", "My Gen {}".format(i), bus="My bus {}".format(
        (i) % n_buses), control="PQ", p_set=power_inj[i],
        v1=0.9, v2=0.94, v3=0.96, v4=1.01, s_nom=0.1, set_p1=50, set_p2=100,
        power_factor=0.98, power_factor_min=0.9, damper=0.1)
for i in range(n_buses-1):
    n.add("Line", "My line {}".format(i), bus0="My bus {}".format(i),
          bus1="My bus {}".format((i+1) % n_buses), x=0.1, r=0.01)


def run_pf():
    n.lpf()
    n.pf(use_seed=True, inverter_control=True)

# run pf without controller and save the results
run_pf()
Generators_Result = pd.DataFrame(index=[n.buses.index], columns=[])
Generators_Result['power_inj'] = power_inj
Generators_Result['no_control'] = n.buses_t.v_mag_pu.values.T

# now apply reactive power as a function of voltage Q(U) or q_v controller,
# parameters (v1,v2,v3,v4,s_nom,damper) are already set in (n.add('Generator' ...))
n.generators.type_of_control_strategy = 'q_v'
# run pf and save the results
run_pf()
Generators_Result['q_v_control'] = n.buses_t.v_mag_pu.values.T

# now apply fixed power factor controller (fixed_cosphi), parameters
# (power_factor, damper) are already set in (n.add(Generator...))
n.generators.q_set = 0  # to clean up q_v effect
n.generators.type_of_control_strategy = 'fixed_cosphi'
# run pf and save the results
run_pf()
Generators_Result['fixed_pf_control'] = n.buses_t.v_mag_pu.values.T

# now apply power factor as a function of real power (cosphi_p), parameters
# (set_p1,set_p2,s_nom,damper,power_factor_min) are already set in (n.add(Generator...))
n.generators.q_set = 0  # to clean fixed_cosphi effect
n.generators.type_of_control_strategy = 'cosphi_p'
# run pf and save the results
run_pf()
Generators_Result['cosphi_p_control'] = n.buses_t.v_mag_pu.values.T

# now apply mix of controllers
n.generators.q_set = 0  # clean the previous controller effect
# q_v controller
n.generators.loc['My Gen 1', 'type_of_control_strategy'] = 'q_v'
n.generators.loc['My Gen 1', 'v1'] = 0.9
n.generators.loc['My Gen 1', 'v2'] = 0.94
n.generators.loc['My Gen 1', 'v3'] = 0.96
n.generators.loc['My Gen 1', 'v4'] = 1.01

# fixed_cosphi controller
n.generators.loc['My Gen 2', 'type_of_control_strategy'] = 'fixed_cosphi'
n.generators.loc['My Gen 2', 'power_factor'] = 0.95

# cosphi_p controller
n.generators.loc['My Gen 3', 'type_of_control_strategy'] = 'cosphi_p'
n.generators.loc['My Gen 3', 'set_p1'] = 50
n.generators.loc['My Gen 3', 'set_p2'] = 100
n.generators.loc['My Gen 3', 'power_factor_min'] = 0.9
# run pf and save the results
run_pf()
Generators_Result['mix_controllers'] = n.buses_t.v_mag_pu.values.T

# plotting effect of each controller on v_mag_pu and compare them
plt.plot(Generators_Result['power_inj'], Generators_Result['no_control'],
         linestyle='--', label="no_controller applied")
plt.plot(Generators_Result['power_inj'], Generators_Result['cosphi_p_control'],
         label="cosphi_p control")
plt.plot(Generators_Result['power_inj'], Generators_Result['q_v_control'],
         label="q_v control")
plt.plot(Generators_Result['power_inj'], Generators_Result['fixed_pf_control'],
         label="fixed_cosphi control")
plt.plot(Generators_Result['power_inj'], Generators_Result['mix_controllers'],
         label="mix_of_controllers")
plt.axhline(y=1.02, color='y', linestyle='--', label='max_v_mag_pu_limit',
            linewidth=3, alpha=0.5)
plt.axhline(y=0.9, color='r', linestyle='--', label='min_v_mag_pu_limit',
            linewidth=3, alpha=0.5)

plt.xlabel('Active_power_injection (MW)')
plt.ylabel('V_mag_pu (per unit)')
plt.title("Application of controllers and mix of them on Generator component")
plt.legend()
plt.show()
