import pygame
import threading
import queue
import serial
import time

# Configurazione Pygame
pygame.init()
width, height = 400, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Parametri di gioco
gravity = 0.2
jump_strength = 10
bird_velocity = 0

# Coda per i dati dell'accelerometro
q = queue.Queue()

class Read_Microbit(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True
      
    def terminate(self):
        self._running = False
        
    def run(self):
        # Configurazione seriale
        port = "COM9"  # Sostituisci con la porta seriale corretta
        s = serial.Serial(port)
        s.baudrate = 115200
        while self._running:
            data = s.readline().decode()
            try:
                acc = [float(x) for x in data[1:-3].split(",")]
            except:
                print("Errore nella lettura dell'accelerometro")
                continue
            q.put(acc)
            time.sleep(0.01)

# Funzione per il salto dell'uccello
def jump():
    global bird_velocity
    bird_velocity -= jump_strength

# Inizializzazione gioco
bird_img = pygame.image.load("bird.png")
bird_rect = bird_img.get_rect()
bird_rect.center = (width // 2, height // 2)

running = True
rm = Read_Microbit()
rm.start()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Lettura dati accelerometro
    if not q.empty():
        acc = q.get()
        accel_x, accel_y, accel_z = acc

        # Aggiornamento velocità uccello in base all'accelerazione
        bird_velocity += (accel_y / 100)
        bird_velocity *= 0.9  # Fattore di smorzamento

    # Applicazione gravità all'uccello
    bird_velocity += gravity

    # Applicazione velocità all'uccello
    bird_rect.centery += bird_velocity

    # Disegno dello sfondo e dell'uccello
    screen.fill((255, 255, 255))
    screen.blit(bird_img, bird_rect)

    # Aggiornamento schermo
    pygame.display.flip()
    clock.tick(60)

# Terminazione thread e chiusura Pygame
rm.terminate()
rm.join()
pygame.quit()
