EESchema Schematic File Version 4
LIBS:wasserschaden-cache
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:WeMos_mini U2
U 1 1 5B26FC39
P 4000 2100
F 0 "U2" H 4000 2600 60  0000 C CNN
F 1 "WeMos_mini" H 4000 1600 60  0000 C CNN
F 2 "custom:wemos" H 4550 1400 60  0001 C CNN
F 3 "" H 4550 1400 60  0000 C CNN
	1    4000 2100
	1    0    0    -1  
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:2N7000 IRFZ44N1
U 1 1 5B2A69C6
P 2700 2250
F 0 "IRFZ44N1" H 2950 2250 50  0000 L CNN
F 1 " " H 2900 2250 50  0000 L CNN
F 2 "custom:irlz44n_vertical" H 2900 2175 50  0001 L CIN
F 3 "" H 2700 2250 50  0001 L CNN
	1    2700 2250
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:Screw_Terminal_01x02 J1
U 1 1 5B2A6B15
P 2250 2750
F 0 "J1" H 2250 2850 50  0000 C CNN
F 1 "valve out" H 2600 2700 50  0000 C CNN
F 2 "Connectors_Terminal_Blocks:TerminalBlock_Altech_AK300-2_P5.00mm" H 2250 2750 50  0001 C CNN
F 3 "" H 2250 2750 50  0001 C CNN
	1    2250 2750
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:Screw_Terminal_01x02 J2
U 1 1 5B2A6B9D
P 2450 3200
F 0 "J2" H 2450 3300 50  0000 C CNN
F 1 "12V in" H 2750 3150 50  0000 C CNN
F 2 "Connectors_Terminal_Blocks:TerminalBlock_Altech_AK300-2_P5.00mm" H 2450 3200 50  0001 C CNN
F 3 "" H 2450 3200 50  0001 C CNN
	1    2450 3200
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR01
U 1 1 5B2A6BE6
P 2650 3200
F 0 "#PWR01" H 2650 2950 50  0001 C CNN
F 1 "GND" H 2650 3050 50  0000 C CNN
F 2 "" H 2650 3200 50  0001 C CNN
F 3 "" H 2650 3200 50  0001 C CNN
	1    2650 3200
	0    -1   -1   0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR02
U 1 1 5B2A6C2A
P 3500 1850
F 0 "#PWR02" H 3500 1600 50  0001 C CNN
F 1 "GND" H 3500 1700 50  0000 C CNN
F 2 "" H 3500 1850 50  0001 C CNN
F 3 "" H 3500 1850 50  0001 C CNN
	1    3500 1850
	0    1    1    0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR03
U 1 1 5B2A6C5A
P 2600 2050
F 0 "#PWR03" H 2600 1800 50  0001 C CNN
F 1 "GND" H 2600 1900 50  0000 C CNN
F 2 "" H 2600 2050 50  0001 C CNN
F 3 "" H 2600 2050 50  0001 C CNN
	1    2600 2050
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:D D1
U 1 1 5B2A6D63
P 2850 2750
F 0 "D1" H 2850 2850 50  0000 C CNN
F 1 " " H 2950 2850 50  0000 C CNN
F 2 "Diodes_SMD:D_SMA_Handsoldering" H 2850 2750 50  0001 C CNN
F 3 "" H 2850 2750 50  0001 C CNN
	1    2850 2750
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-rescue:stepdown-wasserschaden-cache-2018-10-17-20-35-24 U1
U 1 1 5B2A6F8D
P 3800 3000
F 0 "U1" H 3950 2950 60  0000 C CNN
F 1 "stepdown" H 4050 3000 60  0000 C CNN
F 2 "custom:stepdown" H 3800 3000 60  0001 C CNN
F 3 "" H 3800 3000 60  0001 C CNN
	1    3800 3000
	1    0    0    -1  
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR04
U 1 1 5B2A7077
P 3400 2900
F 0 "#PWR04" H 3400 2650 50  0001 C CNN
F 1 "GND" V 3400 2700 50  0000 C CNN
F 2 "" H 3400 2900 50  0001 C CNN
F 3 "" H 3400 2900 50  0001 C CNN
	1    3400 2900
	0    1    1    0   
$EndComp
NoConn ~ 3500 1750
NoConn ~ 3500 1950
NoConn ~ 3500 2350
NoConn ~ 3500 2450
NoConn ~ 4500 2350
NoConn ~ 4500 1850
Wire Wire Line
	2600 2450 2600 2750
Text Notes 2100 2800 0    60   ~ 0
+\n-
Text Notes 2300 3250 0    60   ~ 0
+\n-
Wire Wire Line
	2450 2650 3000 2650
Wire Wire Line
	3000 2650 3000 2750
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:+12V #PWR05
U 1 1 5B2A7A00
P 2450 2650
F 0 "#PWR05" H 2450 2500 50  0001 C CNN
F 1 "+12V" H 2450 2790 50  0000 C CNN
F 2 "" H 2450 2650 50  0001 C CNN
F 3 "" H 2450 2650 50  0001 C CNN
	1    2450 2650
	1    0    0    -1  
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:+12V #PWR06
U 1 1 5B2A7A20
P 2650 3100
F 0 "#PWR06" H 2650 2950 50  0001 C CNN
F 1 "+12V" H 2650 3240 50  0000 C CNN
F 2 "" H 2650 3100 50  0001 C CNN
F 3 "" H 2650 3100 50  0001 C CNN
	1    2650 3100
	1    0    0    -1  
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:+12V #PWR07
U 1 1 5B2A7A40
P 3400 3050
F 0 "#PWR07" H 3400 2900 50  0001 C CNN
F 1 "+12V" V 3400 3250 50  0000 C CNN
F 2 "" H 3400 3050 50  0001 C CNN
F 3 "" H 3400 3050 50  0001 C CNN
	1    3400 3050
	0    -1   -1   0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:R R1
U 1 1 5B2A7CB0
P 3000 2400
F 0 "R1" V 3080 2400 50  0000 C CNN
F 1 "20K" V 3000 2400 50  0000 C CNN
F 2 "Resistors_SMD:R_0603_HandSoldering" V 2930 2400 50  0001 C CNN
F 3 "" H 3000 2400 50  0001 C CNN
	1    3000 2400
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR08
U 1 1 5B2A7CE4
P 3000 2550
F 0 "#PWR08" H 3000 2300 50  0001 C CNN
F 1 "GND" H 3000 2400 50  0000 C CNN
F 2 "" H 3000 2550 50  0001 C CNN
F 3 "" H 3000 2550 50  0001 C CNN
	1    3000 2550
	0    -1   -1   0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR09
U 1 1 5B2A9F12
P 4700 2900
F 0 "#PWR09" H 4700 2650 50  0001 C CNN
F 1 "GND" V 4700 2700 50  0000 C CNN
F 2 "" H 4700 2900 50  0001 C CNN
F 3 "" H 4700 2900 50  0001 C CNN
	1    4700 2900
	0    -1   -1   0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:LED D2
U 1 1 5B2BDC1C
P 2550 900
F 0 "D2" H 2550 1000 50  0000 C CNN
F 1 "valve" H 2550 800 50  0000 C CNN
F 2 "LEDs:LED_D3.0mm" H 2550 900 50  0001 C CNN
F 3 "" H 2550 900 50  0001 C CNN
	1    2550 900 
	0    -1   -1   0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:R R2
U 1 1 5B2BDCBD
P 2550 1200
F 0 "R2" V 2630 1200 50  0000 C CNN
F 1 "1K" V 2550 1200 50  0000 C CNN
F 2 "Resistors_SMD:R_0603_HandSoldering" V 2480 1200 50  0001 C CNN
F 3 "" H 2550 1200 50  0001 C CNN
	1    2550 1200
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR010
U 1 1 5B2BDCFD
P 2550 1350
F 0 "#PWR010" H 2550 1100 50  0001 C CNN
F 1 "GND" H 2550 1200 50  0000 C CNN
F 2 "" H 2550 1350 50  0001 C CNN
F 3 "" H 2550 1350 50  0001 C CNN
	1    2550 1350
	1    0    0    -1  
$EndComp
Connection ~ 3000 2250
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:LED D3
U 1 1 5B2C19FD
P 1950 900
F 0 "D3" H 1950 1000 50  0000 C CNN
F 1 "LED" H 1950 800 50  0000 C CNN
F 2 "LEDs:LED_D3.0mm" H 1950 900 50  0001 C CNN
F 3 "" H 1950 900 50  0001 C CNN
	1    1950 900 
	0    -1   -1   0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:R R3
U 1 1 5B2C1A03
P 1950 1200
F 0 "R3" V 2030 1200 50  0000 C CNN
F 1 "1K" V 1950 1200 50  0000 C CNN
F 2 "Resistors_SMD:R_0603_HandSoldering" V 1880 1200 50  0001 C CNN
F 3 "" H 1950 1200 50  0001 C CNN
	1    1950 1200
	1    0    0    -1  
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR011
U 1 1 5B2C1A09
P 1950 1350
F 0 "#PWR011" H 1950 1100 50  0001 C CNN
F 1 "GND" H 1950 1200 50  0000 C CNN
F 2 "" H 1950 1350 50  0001 C CNN
F 3 "" H 1950 1350 50  0001 C CNN
	1    1950 1350
	1    0    0    -1  
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:LED D4
U 1 1 5B2C1D4C
P 2250 900
F 0 "D4" H 2250 1000 50  0000 C CNN
F 1 "info" H 2250 800 50  0000 C CNN
F 2 "LEDs:LED_D3.0mm" H 2250 900 50  0001 C CNN
F 3 "" H 2250 900 50  0001 C CNN
	1    2250 900 
	0    -1   -1   0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:R R4
U 1 1 5B2C1D52
P 2250 1200
F 0 "R4" V 2330 1200 50  0000 C CNN
F 1 "240" V 2250 1200 50  0000 C CNN
F 2 "Resistors_SMD:R_0603_HandSoldering" V 2180 1200 50  0001 C CNN
F 3 "" H 2250 1200 50  0001 C CNN
	1    2250 1200
	-1   0    0    1   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:GND #PWR012
U 1 1 5B2C1D58
P 2250 1350
F 0 "#PWR012" H 2250 1100 50  0001 C CNN
F 1 "GND" H 2250 1200 50  0000 C CNN
F 2 "" H 2250 1350 50  0001 C CNN
F 3 "" H 2250 1350 50  0001 C CNN
	1    2250 1350
	1    0    0    -1  
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:+3V3 #PWR013
U 1 1 5B2C1F93
P 1950 750
F 0 "#PWR013" H 1950 600 50  0001 C CNN
F 1 "+3.3V" H 1950 890 50  0000 C CNN
F 2 "" H 1950 750 50  0001 C CNN
F 3 "" H 1950 750 50  0001 C CNN
	1    1950 750 
	1    0    0    -1  
$EndComp
$Comp
L Jumper:SolderJumper_2_Open JP1
U 1 1 5BCFAE3F
P 4750 2350
F 0 "JP1" V 4704 2418 50  0000 L CNN
F 1 "deepsleep" H 4550 2450 50  0000 L CNN
F 2 "custom:jumper" H 4750 2350 50  0001 C CNN
F 3 "~" H 4750 2350 50  0001 C CNN
	1    4750 2350
	0    1    1    0   
$EndComp
Wire Wire Line
	4750 2200 4600 2200
Wire Wire Line
	4600 2200 4600 2250
Wire Wire Line
	4600 2250 4500 2250
Wire Wire Line
	4500 2450 4600 2450
Wire Wire Line
	4600 2450 4600 2500
Wire Wire Line
	4600 2500 4750 2500
NoConn ~ 6200 -3400
NoConn ~ 6800 -3300
NoConn ~ 4500 2150
Connection ~ 2450 2650
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:Screw_Terminal_01x02 J3
U 1 1 5BE7342F
P 3950 800
F 0 "J3" H 3950 900 50  0000 C CNN
F 1 "sense" V 4050 800 50  0000 C CNN
F 2 "Connectors_Terminal_Blocks:TerminalBlock_Altech_AK300-2_P5.00mm" H 3950 800 50  0001 C CNN
F 3 "" H 3950 800 50  0001 C CNN
	1    3950 800 
	0    -1   -1   0   
$EndComp
Wire Wire Line
	4050 1050 4300 1050
$Comp
L power:GND #PWR0102
U 1 1 5BE7483F
P 4300 1050
F 0 "#PWR0102" H 4300 800 50  0001 C CNN
F 1 "GND" H 4305 877 50  0000 C CNN
F 2 "" H 4300 1050 50  0001 C CNN
F 3 "" H 4300 1050 50  0001 C CNN
	1    4300 1050
	1    0    0    -1  
$EndComp
Wire Wire Line
	3950 1000 3950 1050
Wire Wire Line
	4050 1050 4050 1000
$Comp
L Device:R R5
U 1 1 5BE92986
P 3950 1250
F 0 "R5" H 4020 1296 50  0000 L CNN
F 1 "330" H 4020 1205 50  0000 L CNN
F 2 "Resistors_SMD:R_0603_HandSoldering" V 3880 1250 50  0001 C CNN
F 3 "~" H 3950 1250 50  0001 C CNN
	1    3950 1250
	1    0    0    -1  
$EndComp
$Comp
L power:+3.3V #PWR0101
U 1 1 5BE93467
P 3950 1400
F 0 "#PWR0101" H 3950 1250 50  0001 C CNN
F 1 "+3.3V" V 3965 1528 50  0000 L CNN
F 2 "" H 3950 1400 50  0001 C CNN
F 3 "" H 3950 1400 50  0001 C CNN
	1    3950 1400
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2450 2750 2600 2750
Wire Wire Line
	2700 2750 2600 2750
Connection ~ 2600 2750
Wire Wire Line
	3000 2250 2900 2250
$Comp
L Sensor_Temperature:DS18B20 U3
U 1 1 5C092FAF
P 4950 1050
F 0 "U3" V 4676 1050 50  0000 C CNN
F 1 "DS18B20" V 4600 1050 50  0000 C CNN
F 2 "custom:temperature_sensor" H 3950 800 50  0001 C CNN
F 3 "http://datasheets.maximintegrated.com/en/ds/DS18B20.pdf" H 4800 1300 50  0001 C CNN
	1    4950 1050
	0    1    -1   0   
$EndComp
$Comp
L power:+3.3V #PWR015
U 1 1 5C093158
P 5250 750
F 0 "#PWR015" H 5250 600 50  0001 C CNN
F 1 "+3.3V" H 5265 923 50  0000 C CNN
F 2 "" H 5250 750 50  0001 C CNN
F 3 "" H 5250 750 50  0001 C CNN
	1    5250 750 
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR014
U 1 1 5C0931D7
P 4650 1050
F 0 "#PWR014" H 4650 800 50  0001 C CNN
F 1 "GND" H 4650 900 50  0000 C CNN
F 2 "" H 4650 1050 50  0001 C CNN
F 3 "" H 4650 1050 50  0001 C CNN
	1    4650 1050
	1    0    0    -1  
$EndComp
$Comp
L Device:R R6
U 1 1 5C09361D
P 5100 750
F 0 "R6" H 4950 800 50  0000 L CNN
F 1 "4K7" H 5000 700 50  0000 L CNN
F 2 "Resistors_SMD:R_0603_HandSoldering" V 5030 750 50  0001 C CNN
F 3 "~" H 5100 750 50  0001 C CNN
	1    5100 750 
	0    1    1    0   
$EndComp
Wire Wire Line
	5250 1050 5250 750 
Connection ~ 5250 750 
Wire Wire Line
	4500 1950 4550 1950
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:+3V3 #PWR?
U 1 1 5D2E6701
P 4700 3050
F 0 "#PWR?" H 4700 2900 50  0001 C CNN
F 1 "+3.3V" V 4700 3300 50  0000 C CNN
F 2 "" H 4700 3050 50  0001 C CNN
F 3 "" H 4700 3050 50  0001 C CNN
	1    4700 3050
	0    1    1    0   
$EndComp
$Comp
L wasserschaden-cache-2018-10-17-20-35-24:+3V3 #PWR?
U 1 1 5D2E75DE
P 4500 1750
F 0 "#PWR?" H 4500 1600 50  0001 C CNN
F 1 "+3.3V" H 4500 1890 50  0000 C CNN
F 2 "" H 4500 1750 50  0001 C CNN
F 3 "" H 4500 1750 50  0001 C CNN
	1    4500 1750
	1    0    0    -1  
$EndComp
Text GLabel 4550 1950 2    50   Input ~ 0
temp
Text GLabel 4950 750  0    50   Output ~ 0
temp
Text GLabel 2250 750  1    50   Output ~ 0
info
Text GLabel 2550 750  1    50   Output ~ 0
valve
Text GLabel 3000 2150 1    50   Output ~ 0
valve
Wire Wire Line
	3000 2150 3000 2250
Text GLabel 3800 1050 0    50   Output ~ 0
sense
Wire Wire Line
	3800 1050 3950 1050
Connection ~ 3950 1050
Wire Wire Line
	3950 1050 3950 1100
NoConn ~ 3500 2050
Text GLabel 3500 2250 0    50   Input ~ 0
valve
Text GLabel 3500 2150 0    50   Input ~ 0
info
Text GLabel 4500 2050 2    50   Input ~ 0
sense
$EndSCHEMATC
