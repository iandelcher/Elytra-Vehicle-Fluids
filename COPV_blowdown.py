import CoolProp.CoolProp as CP
import math
import sys
#==============#
#===INITIAL====#
#==============#

#PERFORMANCE PARAMETERS
fluid = 'Nitrogen'
FUEL_MDOT_REQ = 1.791 #kg/s
P_SET = 150 * 6894.76   #psi --> Pa
BURN_DURATION = 41      #s

#COPV#
V_COPV = 22 / 1000                #L --> m^3
R = 296.80                        #J/kg*K
P_0 = 6000 * 6894.76              #psi --> Pa
T_0 = 305                         #K
RHO_PRESS = CP.PropsSI('D', 'P', P_0, 'T', T_0, fluid)
M_0 = RHO_PRESS * V_COPV
 
#PROPELLANT TANK 
V_PROP = 90 / 1000            #L --> m^3
V_TANK = 100 / 1000            #L --> m^3
T_TANK = 305           #K --> m^3
V_ULL = V_TANK - V_PROP
RHO_RP1 = 810                 #kg/m^3; 

#LINES
line_OD = 1 * 0.0254          
line_ID = 1 * 0.0254

#time (seconds) 
t_step = 0.01



#calculate mdot for choked flow thorugh orifice (line)
#first version of this will not include choked flow 
def calc_choked(ID, P, T, gamma, R):
    A = math.pi * ((ID/2) ** 2)
    mdot = (A * P)/(math.sqrt(T)) * math.sqrt(gamma/R) * ((gamma + 1)/2) ** (-(gamma + 1)/(2 * (gamma-1)))
    return mdot




#change in mass from required flow rate
def delta_m(): 
    Vdot = FUEL_MDOT_REQ / RHO_RP1                   #Vdot out of propellant tank, -Vdot_tank = Vdot_pressurant
    mdot_in = P_SET * Vdot / (R * T_TANK)       #isothermal in the propellant tank 
    dm = mdot_in * t_step
    dv_tank = Vdot * t_step
    return dm, dv_tank

#----now I have a change in mass for the COPV, I can recalculate density for P and T ----#

#START HERE
def blowdown():
    COPV_Pi = P_0
    COPV_Ti = T_0
    COPV_Mi = M_0

    rho_press = RHO_PRESS
    v_gas_tank = V_ULL
    v_prop_tank = V_PROP

    time = 0
    
    #caluculate constant entropy based on our previous P and T
    s_constant = CP.PropsSI('S', 'P', COPV_Pi, 'T', COPV_Ti, fluid)

    #moved it up here, should be okay since making assumption that entropy is conservative

    while time <= BURN_DURATION: 
        #new changes in system: mass decrease in COPV, volume decrease in tank
        dm, dv_tank = delta_m() 
        COPV_Mi = COPV_Mi - dm
        rho_press = COPV_Mi / V_COPV  #calculate new density, COPV volume constant

        #Two state postulate: finding T and P based on our new density an entropy from before (s_constant)
        COPV_T_new = CP.PropsSI('T', 'Dmass', rho_press, 'S', s_constant, fluid)
        COPV_P_new = CP.PropsSI('P', 'Dmass', rho_press, 'S', s_constant, fluid)

        #update P and T
        COPV_Ti = COPV_T_new
        COPV_Pi = COPV_P_new
        
        #update prop left in tank 
        v_prop_tank = v_prop_tank - dv_tank
        v_gas_tank = v_gas_tank + dv_tank

        if COPV_Mi <= 0 and v_prop_tank > 0: 
            print(f"Hey there Elon, your COPV tank ran out of nitrogen while your fuel tank still has {v_prop_tank} L left. Bummer!")
            break
        elif COPV_Pi < P_SET:
            print(f"Your COPV tank is at a pressure {COPV_Pi / 6894.76} psi, which is below your set tank pressure at time {time}. Your rocket will fail. Bummer!")
            break
        elif v_prop_tank <= 0: 
            print(f"There is no more propellant left in the tank at time t = {time:.3f}")
            print (f"Final COPV {fluid} mass: {COPV_Mi:.3f} kg")
            print(f"Final COPV temperature: {COPV_Ti:.3f} K")
            print(f"Final COPV pressure: {(COPV_Pi / 6894.76):.3f} psi")
            break

        
        if round(time % 1, 2) == 0: 
            print(f"### CONDITIONS AT TIME {time:.3f}: ")
            print(f"COPV MASS: {COPV_Mi:.3f} kg")
            print(f"COPV Temperature: {COPV_Ti:.3f} K")
            # Note: If COPV_Pi is in Pascals, you might want (COPV_Pi / 6894.76) for PSI
            print(f"COPV Pressure: {(COPV_Pi/6894.76):.3f} psi")
            print(f"RP1 left: {(v_prop_tank * 1000):.3f} L")

        time += t_step


        


#ONLY INCORPORATE LATER
        
def temp_mass_average(SET_PRESSURE, V_GAS_TANK, dm, COPV_Ti, TANK_Ti):
    
    ullage_mass = (SET_PRESSURE * V_GAS_TANK) / (R * TANK_Ti)
    
    Tf = (dm * (COPV_Ti) + ullage_mass * (TANK_Ti)) / (ullage_mass + dm)

#AND THIS WILL AFFECT OUR EFFECTIVE VOLUME OR OUR PRESSURE. I DONT HAVE CONSISTENT DENSITY, HOW SHOULD I USE TWO STATE

#want to do a mass average calculation for fuel tank temperature 
# Tf = (dm(Tnew) + (ullage_mass)(Tf)) / (ullage_mass + dm)




#QUESTIONS
#also how do I incorporate this mass flow thorugh the choked portion? 

#also should calculate the initial mass in the ullage to be at the set pressure
#have to find a way to get this new temperature to affect the new volume of the ullage (can I use two state postulate? Ullage volume + new temperature? set entropy? somehting like that?)


if __name__ == "__main__":
    # This block runs when the script is executed directly
    blowdown()