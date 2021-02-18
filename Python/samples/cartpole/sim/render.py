"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""

import math
import pyglet
from pyglet.gl import (gl, glBegin, glBlendFunc, glClearColor, glColor4f, 
                       glEnable, glEnd, glLineWidth, glPopMatrix, glPushMatrix, 
                       glRotatef, glTranslatef, glVertex2f, glVertex3f, 
                       GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

import six

RAD2DEG = 57.29577951308232

def draw_cartpole(cartpole, screen_width, screen_height):
    world_width = cartpole.x_threshold*2
    scale = screen_width/world_width
    carty = 100  # TOP OF CART
    polewidth = 10.0
    polelen = scale * cartpole._pole_length
    # target pole position is relative to the center of the screen
    targetpos = scale * (cartpole._target_pole_position + world_width/2)
    cartwidth = 50.0
    cartheight = 30.0
    
    # Draw track
    glColor4f(0,0,0,1.0)
    glLineWidth(1.0)
    glBegin(gl.GL_LINES)
    glVertex2f(0, carty)
    glVertex2f(screen_width, carty)
    glEnd()

    # Draw target position
    gray = 0.4
    glColor4f(gray,gray,gray,1.0)
    glLineWidth(1.0)
    glBegin(gl.GL_LINES)
    glVertex2f(targetpos, 0)
    glVertex2f(targetpos, screen_height)
    glEnd()


    # Draw Cart
    l, r, t, b = -cartwidth/2, cartwidth/2, cartheight/2, -cartheight/2
    cartx = cartpole._cart_position*scale+screen_width/2.0  # MIDDLE OF CART
    
    glColor4f(0.,0.,0.,1.0)
    glPushMatrix()  # Push Translation
    glTranslatef(cartx, carty, 0)
    glBegin(gl.GL_QUADS)
    glVertex3f(l, b, 0)
    glVertex3f(l, t, 0)
    glVertex3f(r, t, 0)
    glVertex3f(r, b, 0)
    glEnd()
    
    # Draw Pole
    l, r, t, b = (
        -polewidth/2,
        polewidth/2,
        polelen-polewidth/2,
        -polewidth/2)
    
    glColor4f(.8, .6, .4, 1.0)
    glPushMatrix()  # Push Rotation
    glRotatef(RAD2DEG * -cartpole._pole_angle, 0, 0, 1.0)
    glBegin(gl.GL_QUADS)
    glVertex3f(l, b, 0)
    glVertex3f(l, t, 0)
    glVertex3f(r, t, 0)
    glVertex3f(r, b, 0)
    glEnd()
    glPopMatrix()  # Pop Rotation
    
    # Draw Axle
    radius = polewidth/2
    glColor4f(0.5, 0.5, 0.8, 1.0)
    glBegin(gl.GL_POLYGON)
    for i in range(12):
        ang = 2 * math.pi * i / 12
        x=math.cos(ang)*radius
        y=math.sin(ang)*radius
        glVertex3f(x, y, 0)
    glEnd()
    glPopMatrix()  # Pop Translation


class Viewer(pyglet.window.Window):
    
    def __init__(self, width=600, height=400, display=None):
        display = self._get_display(display)
        super().__init__(width=width, height=height, display=display)
        
        self.model = None

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def _get_display(self, spec):
        """Convert a display specification (such as :0) into an actual Display
        object.

        Pyglet only supports multiple Displays on Linux.
        """
        if spec is None:
            return None
        
        if isinstance(spec, six.string_types):
            return pyglet.canvas.Display(spec)
        
        raise ValueError("Invalid display specification: {}. \
        (Must be a string like :0 or None.)".format(spec))

    def update(self):
        pyglet.clock.tick()
        self.switch_to()
        self.dispatch_events()
        self.dispatch_event('on_draw')
        self.flip()
    
    def on_draw(self):
        glClearColor(1, 1, 1, 1)
        self.clear()
        
        draw_cartpole(self.model, self.width, self.height)

