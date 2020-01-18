import threading
import numpy as np
import pygame

class GuiThread(threading.Thread):
    def __init__(self, nodes, config, maze):
        threading.Thread.__init__(self, name='GuiThread')
        self.nodes = nodes
        self.config = config
        self.running = True
        self.maze = maze

        self.width = int(config.get('gui', 'window_size_x', fallback=400))
        self.height = int(config.get('gui', 'window_size_y', fallback=400))
        self.scaler = self.height
        pygame.init()
        self.fpsCam = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.width, self.height), 0, 32)

        self.tx_line1 = int(config.get('gui', 'tx_line1', fallback='-40'))
        self.tx_line2 = int(config.get('gui', 'tx_line2', fallback='-80'))

    def run(self):
        # Render gui
        while self.running:
            self.window.fill((255, 255, 255))

            # Draw environment
            self.draw_environment()

            for nodename, node in self.nodes.items():
                x,y = self.get_screen_position(node.position)
                pygame.draw.circle(self.window, (255, 0, 0), (int(x), int(y)), 2, 0)

                # Draw -40dBm line
                clr = (0,0,255)
                if node.rx_dat:
                    node.rx_dat = False
                    if self.config.get('gui', 'clr_change_dat', fallback='true')=='true':
                        clr = (255,0,0)
                    if self.config.get('gui', 'draw_line', fallback='true')=='true':
                        for n in node.tx_list:
                            px,py = self.get_screen_position(n)
                            pygame.draw.line(self.window, (0,0,0), (int(px), int(py)), (int(x), int(y)), 4)
                elif node.rx_ctl:
                    node.rx_ctl = False
                    if self.config.get('gui', 'clr_change_ctl', fallback='true')=='true':
                        clr = (0,255,0)
                d = node.calc_dist(self.tx_line1)
                pygame.draw.circle(self.window, clr, (int(x), int(y)), int(self.get_screen_length(d)), 1)
                d = node.calc_dist(self.tx_line2)
                clr=(180,180,255)
                pygame.draw.circle(self.window, clr, (int(x), int(y)), int(self.get_screen_length(d)), 1)

            for event in pygame.event.get():
                pass

            pygame.display.update()
            self.fpsCam.tick(15)
        pygame.quit()

    def stop(self):
        self.running = False

    def get_screen_position(self, pos):
        x, y = pos
        m = self.maze
        gs = self.height//(m.height+2)
        offs = gs

        wx = (x+0.5)*gs+offs
        wy = (y+0.5)*gs+offs
        return wx,wy

    def get_screen_length(self, length):
        m = self.maze
        gs = self.height//(m.height+2)
        return gs*length

    # ENVIRONMENT
    def draw_environment(self):
        m = self.maze
        gs = self.height//(m.height+2)
        offs = gs
        for w in range(m.width):
            for h in range(m.height):
                if m.grid[(w,h)].west:
                    pygame.draw.line(self.window, (0,0,0), (offs+w*gs, offs+h*gs), (offs+w*gs, offs+(h+1)*gs), 1)
                if m.grid[(w,h)].north:
                    pygame.draw.line(self.window, (0,0,0), (offs+w*gs, offs+h*gs), (offs+(w+1)*gs, offs+h*gs), 1)
                if m.grid[(w,h)].east:
                    pygame.draw.line(self.window, (0,0,0), (offs+(w+1)*gs, offs+h*gs), (offs+(w+1)*gs, offs+(h+1)*gs), 1)
                if m.grid[(w,h)].south:
                    pygame.draw.line(self.window, (0,0,0), (offs+w*gs, offs+(h+1)*gs), (offs+(w+1)*gs, offs+(h+1)*gs), 1)