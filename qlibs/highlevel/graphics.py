"""
  Highlevel graphics things
"""

from ..gui.sprite_drawer import SpriteDrawer, TEXTURE_POINTS
from ..resources.resource_loader import get_image_data
from ..math import Matrix4, IDENTITY

class SpriteMasterBase:
    """
      Base SpriteMaster class which does not handle drawers.
      Used for forking
    """
    def __init__(self, master):
        self.master = master
        self._derive_drawers(master)
        self.last_used_matrix = None

    def add_sprite_rect(self, id_, x, y, w, h, z=0, color=(1, 1, 1, 1), tpoints=TEXTURE_POINTS):
        drawer_id, sprite_id = self.id_map[id_]
        drawer = self.drawers[drawer_id]
        drawer.add_sprite_rect(sprite_id, x, y, w, h, z, color, tpoints)
    
    def add_sprite_centered(self, id_, x, y, w, h, z=0, color=(1, 1, 1, 1), tpoints=TEXTURE_POINTS):
        drawer_id, sprite_id = self.id_map[id_]
        drawer = self.drawers[drawer_id]
        drawer.add_sprite_centered(sprite_id, x, y, w, h, z, color, tpoints)

    def add_sprite_rotated(self, id_, x, y, w, h, r, z=0, color=(1, 1, 1, 1), tpoints=TEXTURE_POINTS):
        drawer_id, sprite_id = self.id_map[id_]
        drawer = self.drawers[drawer_id]
        drawer.add_sprite_rotated(sprite_id, x, y, w, h, r, z, color, tpoints)

    def render(self, mvp=Matrix4(IDENTITY), reset=True):
        for drawer in self.drawers:
            drawer.render(mvp=mvp, reset=reset)

    def render_centered(self, center, size, reset=True):
        mvp = Matrix4.orthogonal_projection(center[0]-size[0]/2, center[0]+size[0]/2, center[1]-size[1]/2, center[1]+size[1]/2)
        self.last_used_matrix = mvp
        self.render(mvp=mvp, reset=reset)
    
    def render_rescaled(self, x, y, w, h, reset=True):
        mvp = Matrix4.orthogonal_projection(x, w, h, y)
        self.render(mvp=mvp, reset=reset)
    
    def render_like(self, master, reset=True):
        self.render(mvp=master.last_used_matrix, reset=reset)

    def _derive_drawers(self, master):
        self.id_map = master.id_map
        self.drawers = [drawer.fork() for drawer in master.drawers]

    def clear(self):
        for drawer in self.drawers:
            drawer.clear()

    def fork(self):
        """
          Create another sprite master with it's own set of buffers
        """
        fork = SpriteMasterBase(self.master)
        self.master.forks.append(fork)
        return fork

class ObjectSpriteMaster:
    """
    Like the usual sprite master, but uses "Objects" to manipulate buffers.
    
    More effient when you don't need to update everything.
    """
    def __init__(self, master):
        self._derive_drawers(master)
    
    def add_sprite(self, id_, x, y, w, h, r=0, z=0, color=(1, 1, 1, 1)):
        drawer_id, sprite_id = self.id_map[id_]
        drawer = self.drawers[drawer_id]
        return drawer.add_sprite(id_, x, y, w, h, r, z, color)

    def render(self, mvp=Matrix4(IDENTITY)):
        for drawer in self.drawers:
            drawer.render()

    def render_centered(self, center, size):
        mvp = Matrix4.orthogonal_projection(center[0]-size[0]/2, center[0]+size[0]/2, center[1]-size[1]/2, center[1]+size[1]/2)
        self.render()
    
    def _derive_drawers(self, master):
        self.id_map = master.id_map
        self.drawers = [drawer.fork() for drawer in master.drawers]


class SpriteMaster(SpriteMasterBase):
    """
    Does loading, managing and drawing. All at once.
    
    Can also calculate mvps.
    
    Quite effient in terms of draw calls.
    """
    def __init__(self, ctx):
        self.ctx = ctx
        self.drawers = list()
        self.id_map = dict()
        self.images = dict()
        #self.load_calls = list()
        self.max_sprites_per_drawer = ctx.info.get('GL_MAX_ARRAY_TEXTURE_LAYERS', 256)
        self.forks = []
        self.last_used_matrix = None

    def load_file(self, sprite_id, file_id):
        self.images[sprite_id] = get_image_data(file_id, mode="RGBA")
        #self.load_calls.append((sprite_id, file_id))

    def init(self):
        self.drawers.clear()
        self.id_map.clear()
        #Count sizes
        cnt = dict()
        for sprite, img in self.images.items():
            if img.size not in cnt:
                cnt[img.size] = list()

            cnt[img.size].append(img)
            if not hasattr(img, "sprite"):
                img.sprite = []
            img.sprite.insert(0, sprite)
        
        #Create drawers
        for size, images in cnt.items():
            for i in range(0, len(images), self.max_sprites_per_drawer):
                drawer_id = len(self.drawers)
                am = min(len(images)-i, self.max_sprites_per_drawer)
                data = b"".join((img.data for img in images[i:i+am]))
                self.drawers.append(SpriteDrawer(self.ctx, (*size, am), data))
                for j, img in enumerate(images[i:i+am]):
                    self.id_map[img.sprite.pop()] = (drawer_id, j)
        
        #print(self.id_map)
        #And it is ready!
        #Update forks
        for fork in self.forks:
            fork._derive_drawers(self)

    def fork(self):
        """
          Create another sprite master with it's own set of buffers
        """
        fork = SpriteMasterBase(self)
        self.forks.append(fork)
        return fork

        