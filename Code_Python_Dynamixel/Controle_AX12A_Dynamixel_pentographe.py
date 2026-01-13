#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from dynamixel_sdk import * # Utilise la librairie officielle

# --- CONFIGURATION CLAVIER ---
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode().lower()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()

# --- CONFIGURATION AX-12A (Protocol 1.0) ---
ADDR_TORQUE_ENABLE    = 24
ADDR_GOAL_POSITION    = 30
ADDR_PRESENT_POSITION = 36
PROTOCOL_VERSION      = 1.0

# Paramètres de ton scan Dynamixel Wizard
BAUDRATE   = 115200
DEVICENAME = 'COM4' 
DXL1_ID    = 1
DXL2_ID    = 2

# Paramètres de mouvement
STEP       = 30      # Valeur de déplacement à chaque appui
pos1       = 512     # Position de départ (milieu)
pos2       = 512

# Initialisation des gestionnaires
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Ouverture du port
if not portHandler.openPort():
    print("Erreur : Impossible d'ouvrir le port COM4")
    quit()

# Réglage du Baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("Erreur : Impossible de régler le baudrate à 115200")
    quit()

# Activation du Torque (Couple) pour les deux moteurs
packetHandler.write1ByteTxRx(portHandler, DXL1_ID, ADDR_TORQUE_ENABLE, 1)
packetHandler.write1ByteTxRx(portHandler, DXL2_ID, ADDR_TORQUE_ENABLE, 1)

print("--- CONTROLE DES AX-12A ACTIVE ---")
print("Moteur 1 (ID 1) : Touches A / D")
print("Moteur 2 (ID 2) : Touches W / S")
print("ESC pour quitter")

try:
    while True:
        key = getch()
        
        if key == chr(0x1b): # Touche ESC
            break
            
        # --- Contrôle Moteur 1 (ID 1) ---
        elif key == 'a':
            pos1 = max(0, pos1 - STEP)
            packetHandler.write2ByteTxRx(portHandler, DXL1_ID, ADDR_GOAL_POSITION, pos1)
        elif key == 'd':
            pos1 = min(1023, pos1 + STEP)
            packetHandler.write2ByteTxRx(portHandler, DXL1_ID, ADDR_GOAL_POSITION, pos1)
            
        # --- Contrôle Moteur 2 (ID 2) ---
        elif key == 'w':
            pos2 = min(1023, pos2 + STEP)
            packetHandler.write2ByteTxRx(portHandler, DXL2_ID, ADDR_GOAL_POSITION, pos2)
        elif key == 's':
            pos2 = max(0, pos2 - STEP)
            packetHandler.write2ByteTxRx(portHandler, DXL2_ID, ADDR_GOAL_POSITION, pos2)


        # Lecture de la position réelle pour vérification
        cur_pos1, _, _ = packetHandler.read2ByteTxRx(portHandler, DXL1_ID, ADDR_PRESENT_POSITION)
        cur_pos2, _, _ = packetHandler.read2ByteTxRx(portHandler, DXL2_ID, ADDR_PRESENT_POSITION)

        print(f"\rPositions réelles -> ID1: {cur_pos1:4} | ID2: {cur_pos2:4}", end="")

finally:
    # Désactivation du couple avant de quitter
    packetHandler.write1ByteTxRx(portHandler, DXL1_ID, ADDR_TORQUE_ENABLE, 0)
    packetHandler.write1ByteTxRx(portHandler, DXL2_ID, ADDR_TORQUE_ENABLE, 0)
    portHandler.closePort()
    print("\n\nProgramme arrêté proprement.")