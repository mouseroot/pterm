import json
import pygame, sys
import time
import os
import os.path
import subprocess
from pygame.locals import (
    K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE, #Movement Keys
    K_ESCAPE,K_BACKSPACE,K_RETURN, #Menu 
    QUIT, KEYDOWN, KEYUP #Pygame Events
)

clock = pygame.time.Clock()
pygame.init()

input_line = ""
output_line = ""
history = []
history_index = 0
history_str = ""
database = {}

def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 1, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


#Load settings
config = json.load(open("config.json"))
window_config = config["window"]
history_config = config["history"]
text_size = window_config["text_size"]
title = window_config["title"]
cursor_config = config["cursor"]
output_config = config["output"]

def write_history():
    with open(history_config["save_file"],"w") as history_file:
        global history
        for item in history:
            if item == '' or item == '\n':
                pass
            else:
                history_file.write(f"{item}\n")

def read_history():
    if os.path.exists(".phistory"):
        with open(history_config["save_file"],"r") as history_file:
            return history_file.read().split("\n")
    else:
        print(f'Creating {history_config["save_file"]}')
        write_history()



font = pygame.font.SysFont("Consolas",text_size)

pygame.display.set_caption(title)

WINDOW_SIZE = (window_config["width"],window_config["height"])
game_running = True

screen = pygame.display.set_mode(WINDOW_SIZE,0, 32)
cursor_rect = pygame.Rect(0,0,0,0)
history_rect = pygame.Rect(5,50,history_config["width"],history_config["height"])
output_rect = pygame.Rect(5,300,output_config["width"],output_config["height"])
intro_text = """
Pygame Terminal
v0.1 - Alpha Testing
"""



if history_config["enabled"]:
    print(f"Loading History file: {history_config['save_file']}")
    history = read_history()

#Gameloop
while game_running:
    

    for event in pygame.event.get():
        if event.type == QUIT:
            game_running = False
        
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                input_line = input_line[:-1]
            elif event.key == K_RETURN:
                if input_line == "delete history":
                    history = []
                    input_line = ""
                    try:
                        os.remove(history_config["save_file"])
                    except FileNotFoundError:
                        print("File already deleted")
                elif input_line == "quit" or input_line == "exit":
                    game_running = False
                    break
                else:
                    #other command
                    
                    if history_config["enabled"]:
                        history.append(input_line.replace('\n',''))
                        write_history()
                input_line = ""
            elif event.key == K_UP:
                try:
                    history_index += 1
                    input_line = history[history_index]
                except IndexError:
                    history_index = 0
                    input_line = history[history_index]
            elif event.key == K_DOWN:
                try:
                    history_index -= 1
                    input_line = history[history_index]
                except IndexError:
                    history_index = len(history) - 1
                    input_line = history[history_index]
            else:
                input_line += event.unicode
    #Update
    
    
    #Draw Background
    screen.fill(window_config["background"])

    #History
    if history_config["enabled"]:
        pygame.draw.rect(screen, pygame.Color("lightgreen"),history_rect)
        blit_text(screen,"History",(history_rect.x + 5, history_rect.y + 5),font,pygame.Color("Black"))
        if history:
            blit_text(screen,"\n".join(history),(history_rect.x + 5, history_rect.y + 20),font, pygame.Color("black"))

    #MOTD
    blit_text(screen,intro_text,(0,0),font,pygame.Color("lightgreen"))

    #Output
    pygame.draw.rect(screen, pygame.Color("gray"),output_rect)
    blit_text(screen, output_line,(output_rect.x + 5, output_rect.y + 10),font,pygame.Color("white"))

    #blit_text(screen,input_line,(10,WINDOW_SIZE[1]-50),font,pygame.Color("green"))

    text_img = font.render(input_line, True, pygame.Color(window_config["text_color"]))
    rect = text_img.get_rect()
    pygame.draw.rect(screen, pygame.Color("gray"),pygame.Rect(10,WINDOW_SIZE[1]-50,500,15))
    screen.blit(text_img, pygame.Rect(10,WINDOW_SIZE[1]-50,WINDOW_SIZE[0],500))
    if time.time() % 1 > cursor_config["blink_rate"]:
        pygame.draw.rect(screen, pygame.Color("red"),pygame.Rect(rect.x + rect.width + 10, WINDOW_SIZE[1]-50, cursor_config["width"],15))
    pygame.display.update()
    clock.tick(60)


pygame.quit()
sys.exit(0)