import pygame
import math

from pathlib import Path

import constants as con


class Button:
    def __init__(self, x, y, w, h, color, text, radius=-1, click_counter=0, info=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.info = info
        self.color = color
        self.text = text
        self.radius = radius
        self.rect = pygame.Rect(x, y, w, h)
        self.click_counter = click_counter


    def draw(self, surface, color=-1):

        if color == -1:
            display_color = self.color
        else:
            display_color = color

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, display_color, self.rect, border_radius=self.radius)

        lines = self.text.split("\n")

        max_height = 0
        for i in lines:
            text_surface = con.basic_font.render(i, True, con.COLOR_PALETTE["black"])
            if text_surface.get_height() > max_height:
                max_height = text_surface.get_height()

        for i in range(len(lines)):
            text_surface = con.basic_font.render(lines[i], True, con.COLOR_PALETTE["black"])
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - max_height * (len(lines)-1)/2 + max_height*i))
            surface.blit(text_surface, text_rect)

    def is_clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos) and event.button == 1:
                    self.click_counter += 1
                    return self.click_counter
                self.click_counter = 0
                return 0
            self.click_counter = 0
            return 0
    ### TODO prevent it from incrementing clickcounter more than once per frame

class Toggle:
    def __init__(self, x, y, w=116, h=65, default=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.state = default
        self.velocity = 0
        self.spring_slider = 1 if self.state else 0

        offpos  = self.x -1
        onpos = self.x + self.w - 83
        self.togl_head = pygame.Rect(onpos if self.state else offpos, self.y - self.h/4, 83, self.h)

    def draw(self, surface, events):

        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(self.x, self.y, self.w, self.h).collidepoint(event.pos):
                    self.state = not self.state


        dest = 1 if self.state else 0

        offset = dest - self.spring_slider 
        self.velocity += offset * 0.2 - self.velocity * 0.4
        if abs(offset) < 0.0001 and self.velocity < 0.0008:
            self.velocity = 0
        self.spring_slider += self.velocity

        self.togl_head.x = self.x + self.spring_slider* (self.w-83)


        
        # slider 
        rect = pygame.Rect(self.x, self.y, self.w, self.h/2)
        pygame.draw.rect(surface, con.COLOR_PALETTE["list item selected"], rect, border_radius=15)
        rect = pygame.Rect(self.x + 5, self.y +5, self.w-10, self.h/2-10)
        pygame.draw.rect(surface, con.COLOR_PALETTE["shadow"], rect, border_radius=10)

        # On/Off head

        color = [con.COLOR_PALETTE["face"][x] + (con.COLOR_PALETTE["list item selected"][x]-con.COLOR_PALETTE["face"][x])*(1-self.spring_slider) for x in range(3)]
        pygame.draw.rect(surface, con.COLOR_PALETTE["textinput selected"], self.togl_head, border_radius=20)
        self.togl_head.inflate_ip(-10, -10)
        pygame.draw.rect(surface, color, self.togl_head, border_radius=15)
        self.togl_head.inflate_ip(10, 10)

        text_surface = con.basic_font.render("On" if self.state else "Off", True, con.COLOR_PALETTE["black"])
        text_rect = text_surface.get_rect(center=(self.togl_head.centerx, self.togl_head.centery))
        surface.blit(text_surface, text_rect)


        # pygame.draw.rect(surface, (100, 100, 255), pygame.Rect(self.x, self.y,self.w, self.h))
        # pygame.draw.rect(surface, (255, 100, 100), rect)   

class Warning:
    def __init__(self, text, position=(40, con.HEIGHT-80, con.WIDTH-80), level="warning", counter=180):

        WARNING_COLOR_PALETTE = {
            "info" : con.COLOR_PALETTE["face"],
            "warning" : con.COLOR_PALETTE["red accent"],
            "error" : con.COLOR_PALETTE["black"]
        }

        self.text = text
        self.dest = position[1]
        self.y = con.HEIGHT + 50
        self.level = level
        self.color = con.COLOR_PALETTE["black"] if self.level != "error" else con.COLOR_PALETTE["red accent"]
        self.islandcolor = WARNING_COLOR_PALETTE[self.level]

        for i in range(len(self.islandcolor)):
            if self.islandcolor[i] < 0:
                self.islandcolor = (self.islandcolor[0] if i != 0 else 0, self.islandcolor[1] if i != 1 else 0, self.islandcolor[2] if i != 2 else 0)


        self.counter = counter
        self.death = False
        self.warning_text = con.basic_font.render(self.text, True, self.color)
        self.x = con.WIDTH/2 - (self.warning_text.get_width() + 15)/2
        self.velocity = 0

        self.spr_force = 0.2
        self.spr_damp  = 0.4


    def get_circle_vertex_pos(self, x, y, poly_count, radius, counter, max, min):

        progress = (counter-min) / (max-min) * poly_count
        progress = math.ceil(progress)
        result = [(x, y)]
        for i in range(progress) :
            newx = math.cos((2*math.pi*i)/poly_count) * radius
            newy = math.sin((2*math.pi*i)/poly_count) * radius

            result.append((newx + x, newy + y))
        result.append((x, y))
        result.append((x, y))
        return result
    
    def tick(self, surface):

        
        pygame.draw.rect(surface, self.islandcolor, pygame.Rect(self.x - 20, self.y, (self.warning_text.get_width() + 15) + 40, 52), border_radius=20)

        surface.blit(self.warning_text , (self.x + 30/2 + 10, self.y))
        
        #pygame.draw.circle(surface, self.color, (self.x, self.y + 26), 15)

        pygame.draw.polygon(surface, self.color, self.get_circle_vertex_pos(self.x + 5, self.y + 26, 50, 10, self.counter if self.counter < 180 - 30 else 180 - 30, 180 - 30, 30))


        offset = self.dest - self.y
        self.velocity += offset * self.spr_force - self.velocity * self.spr_damp
        if abs(offset) < 0.5 and self.velocity < 0.0008:
            self.velocity = 0
        self.y += self.velocity

        if self.counter < 20:
            self.spr_damp = 0.4
            self.spr_force = 0.1
            self.dest = con.HEIGHT + 50
            # self.warning_text.set_alpha(255 - i*255/5)

        self.counter -= 1
        if self.counter < 1:
            self.death = True

class Textinput:
    def __init__(self, x, y, w, h, radius, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.radius = radius
        self.color = color
        self.text = ""
        self.focused = False
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    
    def draw(self, surface, events):
        
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if not self.focused:    
            pygame.draw.rect(surface, (self.color[0] , self.color[1], self.color[2]), self.rect, border_radius=self.radius)
        else:
            pygame.draw.rect(surface, (self.color[0] - 50 if (self.color[0] - 50) > 0 else 0, self.color[1] - 50 if (self.color[0] - 50) > 0 else 0, self.color[2] - 50 if (self.color[0] - 50) > 0 else 0), self.rect, border_radius=self.radius)
        
        for event in events:   
            if self.focused: 
                if event.type == pygame.TEXTINPUT:
                    self.text += event.text     
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif event.key == pygame.K_DELETE:
                        self.text = ""                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.focused = True
                else:
                    self.focused = False

        text_text = con.basic_font.render(self.text, True, con.COLOR_PALETTE["black"])
        surface.blit(text_text, (self.x + 5, self.y + 5))
        
